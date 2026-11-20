"""Run with python -m conlang from a clone. Uses Python's standard library."""
import argparse
import json
import sys
from math import isclose
from pathlib import Path

from . import VERSION
from .calibrate import select
from .runner import MODELS, bound, new_bundle, price, run, settings, summarize
from .scoring import compare, grade
from .suite import ROOT, build, certified, digest, load_suite, read, sample_manifest, write


def bundle_manifest(bundle):
    name = bundle["suite"]
    if not isinstance(name, str) or not name.isalnum():
        raise ValueError("invalid suite name")
    return load_suite(name)


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sample = commands.add_parser("sample", help="create a new answer-balanced seed manifest")
    sample.add_argument("--name", required=True)
    sample.add_argument("--seed", required=True, type=int)
    sample.add_argument("--count", required=True, type=int)
    sample.add_argument("--length", type=int, choices=(2, 3, 4, 12), required=True)
    sample.add_argument("--out", type=Path, required=True)
    gen = commands.add_parser("generate", help="export model prompts separately from evaluator data")
    gen.add_argument("--suite", default="smoke")
    gen.add_argument("--manifest", type=Path, help="use a custom seed manifest")
    gen.add_argument("--out", type=Path, required=True)
    for name in ("estimate", "run"):
        p = commands.add_parser(name)
        p.add_argument("--suite", default="smoke")
        p.add_argument("--model", default=next(iter(MODELS)))
        p.add_argument("--effort", default="default")
        p.add_argument("--max-output", type=int, default=64)
        p.add_argument("--rates", nargs=2, type=float, metavar=("INPUT", "OUTPUT"),
                       help="USD per million tokens; required for an unlisted model")
        if name == "run":
            p.add_argument("--out", required=True, type=Path)
            source = p.add_mutually_exclusive_group(required=True)
            source.add_argument("--budget", type=float, help="USD cap for this bundle")
            source.add_argument("--import", dest="import_file", type=Path, help="external adapter bundle")
    p = commands.add_parser("score")
    p.add_argument("bundle", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--strict", action="store_true", help="audit original bare-JSON scoring")
    p = commands.add_parser("compare")
    p.add_argument("first", type=Path)
    p.add_argument("second", type=Path)
    p = commands.add_parser("calibrate")
    p.add_argument("--results", type=Path, default=ROOT / "results")
    p = commands.add_parser("verify-results")
    p.add_argument("--results", type=Path, default=ROOT / "results")
    p.add_argument("--index", type=Path, help="write the independently recomputed index")

    args = parser.parse_args(argv)
    if args.command == "sample":
        if args.out.exists():
            raise ValueError("choose a new manifest path")
        write(args.out, sample_manifest(args.name, args.seed, args.count, args.length))
    elif args.command == "generate":
        m = read(args.manifest) if args.manifest else load_suite(args.suite)
        prompts, keys, rejected = build(m)
        write(args.out / "public" / "prompts.json", prompts)
        write(args.out / "evaluator" / "keys.json", keys)
        write(args.out / "evaluator" / "rejected.json", rejected)
        write(args.out / "manifest.json", m)
        template = new_bundle(m, prompts, dict(provider="replace", model="replace", effort="default",
                                               temperature=None, max_completion_tokens=64))
        template["responses"] = {i: dict(prompt_hash=digest(p), raw="") for i, p in prompts.items()}
        write(args.out / "adapter-template.json", template)
        if rejected:
            raise ValueError(f"{len(rejected)} rejected pairs; see evaluator/rejected.json")
        print_json(dict(items=len(prompts), suite_hash=digest([m, prompts])))
    elif args.command in ("estimate", "run"):
        m = load_suite(args.suite)
        prompts, _ = certified(m)
        if args.command == "run" and args.import_file:
            bundle = read(args.import_file)
            if bundle["suite"] != m["name"]:
                raise ValueError("import suite differs")
            validate_bundle(bundle)
            if args.out.exists():
                raise ValueError("import destination exists")
            write(args.out, bundle)
            return
        conf = settings(args.model, args.effort, args.max_output, args.rates)
        if args.command == "estimate":
            print_json(dict(calls=len(prompts), upper_usd=sum(bound(conf, p) for p in prompts.values()),
                            settings=conf))
        else:
            print_json(run(m, conf, args.out, args.budget)["usage_summary"])
    elif args.command == "score":
        b = read(args.bundle)
        report = grade(bundle_manifest(b), b, strict=args.strict)
        if args.out:
            write(args.out, report)
        else:
            print_json(report)
    elif args.command == "compare":
        a, b = read(args.first), read(args.second)
        print_json(compare(bundle_manifest(a), a, b))
    elif args.command == "calibrate":
        print_json(select(args.results))
    else:
        paths = sorted(args.results.glob("*/*.json"))
        if not paths:
            raise ValueError("no results found")
        index = {}
        for path in paths:
            b = read(path)
            if path.parent.name != b["suite"]:
                raise ValueError("bundle filed under wrong suite")
            report = validate_bundle(b)
            if not report["complete"]:
                raise ValueError(f"incomplete submission: {path.name}")
            index[path.relative_to(args.results).as_posix()] = dict(
                status="regraded", scorer_version=report["scorer_version"],
                suite_hash=b["suite_hash"], settings=b["settings"], accuracy=report["accuracy"],
                headline=report["headline"], all_four_correct=report["all_four_correct"],
                usage=b.get("usage_summary"), independent_rerun_of=b.get("independent_rerun_of"))
            print(f"regraded {path.parent.name}/{path.name}  headline={report['headline']}")
        for name, row in index.items():
            previous = row["independent_rerun_of"]
            if previous is not None and (previous not in index or previous == name
                    or index[previous]["suite_hash"] != row["suite_hash"]
                    or index[previous]["settings"] != row["settings"]):
                raise ValueError(f"invalid independent rerun reference: {name}")
        if args.index:
            write(args.index, index)


def validate_bundle(b):
    if not isinstance(b.get("started"), str) or not b.get("benchmark_commit"):
        raise ValueError("missing date or benchmark revision")
    for k in ("provider", "model", "effort", "temperature", "max_completion_tokens"):
        if k not in b["settings"]:
            raise ValueError(f"missing settings field: {k}")
    if any(b["settings"][k] in ("", "replace", None) for k in ("model", "provider", "effort")):
        raise ValueError("provide actual adapter settings")
    if b.get("usage_summary") and "list_price_usd" in b["usage_summary"]:
        for row in b["responses"].values():
            usage = row["usage"]
            expected = price(b["settings"], usage["prompt_tokens"], usage["completion_tokens"])
            if not isclose(expected, row["cost_usd"]):
                raise ValueError("response token cost mismatch")
        calculated = summarize(b)
        if any(not isclose(v, b["usage_summary"][k]) for k, v in calculated.items()):
            raise ValueError("bundle usage summary mismatch")
    return grade(bundle_manifest(b), b)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        sys.exit(f"conlang: {exc}")
