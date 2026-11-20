"""Run with python -m conlang from a clone. Uses Python's standard library."""
import argparse
import json
import sys
from pathlib import Path

from . import VERSION
from .calibrate import select
from .runner import MODELS, bound, new_bundle, run, settings
from .scoring import compare, grade
from .suite import ROOT, build, certified, digest, load_suite, read, write


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
    p = commands.add_parser("compare")
    p.add_argument("first", type=Path)
    p.add_argument("second", type=Path)
    p = commands.add_parser("calibrate")
    p.add_argument("--results", type=Path, default=ROOT / "results")
    p = commands.add_parser("verify-results")
    p.add_argument("--results", type=Path, default=ROOT / "results")

    args = parser.parse_args(argv)
    if args.command == "generate":
        m = read(args.manifest) if args.manifest else load_suite(args.suite)
        prompts, keys, rejected = build(m)
        write(args.out / "public" / "prompts.json", prompts)
        write(args.out / "evaluator" / "keys.json", keys)
        write(args.out / "evaluator" / "rejected.json", rejected)
        write(args.out / "manifest.json", m)
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
        report = grade(bundle_manifest(b), b)
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
        for path in paths:
            b = read(path)
            if path.parent.name != b["suite"]:
                raise ValueError("bundle filed under wrong suite")
            report = validate_bundle(b)
            if not report["complete"]:
                raise ValueError(f"incomplete submission: {path.name}")
            print(f"regraded {path.parent.name}/{path.name}  headline={report['headline']}")


def validate_bundle(b):
    if not isinstance(b.get("started"), str) or not b.get("benchmark_commit"):
        raise ValueError("missing date or benchmark revision")
    for k in ("provider", "model", "effort", "temperature", "max_completion_tokens"):
        if k not in b["settings"]:
            raise ValueError(f"missing settings field: {k}")
    return grade(bundle_manifest(b), b)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        sys.exit(f"conlang: {exc}")
