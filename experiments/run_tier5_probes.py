"""Run a Tier 5 manifest: every stage plus the English control, fresh context each."""
import argparse
import hashlib
import json
import math
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from conlang.provider import body_size, request as provider_request
from conlang.runner import price, settings
from conlang.suite import read, write
from conlang.tier5 import load_manifest, score

CAPPED = ("length", "max_tokens")


def requests_for(items):
    """Yield (item, stage, prompt). Stage is an int or 'english'."""
    for item in items:
        for stage, prompt in enumerate(item["prompts"]):
            yield item, stage, prompt
        yield item, "english", item["english"]


def row_path(directory, item, stage):
    return directory / f"{item['world_seed']}-{item['language_seed']}-{stage}.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--budget", required=True, type=float)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", default="low")
    parser.add_argument("--provider", default="OpenAI", choices=("OpenAI", "Anthropic"))
    parser.add_argument("--max-output", type=int, default=16384)
    parser.add_argument("--rates", required=True, nargs=2, type=float)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--estimate", action="store_true",
                        help="print the worst-case cost of the remaining requests and exit")
    parser.add_argument("--retry-uncertain", action="store_true",
                        help="keep uncertain attempts, reserve their cost, then retry them")
    args = parser.parse_args(argv)
    if (not all(math.isfinite(x) and x >= 0 for x in [args.budget, *args.rates])
            or args.max_output < 1 or args.workers < 1):
        parser.error("invalid budget, rates, output limit or worker count")
    manifest, items = load_manifest(args.manifest)
    conf = settings(args.model, args.effort, args.max_output, args.rates, args.provider)
    directory = Path(args.out)
    todo = [(item, stage, prompt) for item, stage, prompt in requests_for(items)
            if not row_path(directory, item, stage).exists()]

    def reservation(prompt):
        messages = [{"role": "user", "content": prompt}]
        # UTF-8 bytes bound text tokens; allow one envelope per message.
        return price(conf, body_size(conf, messages) + 128, args.max_output)

    if args.estimate:
        total = sum(reservation(p) for _, _, p in todo)
        print(json.dumps(dict(manifest=manifest["name"], requests=len(list(requests_for(items))),
                              remaining=len(todo), worst_case_usd=round(total, 4))))
        return
    metadata = dict(manifest=manifest["name"],
                    manifest_sha256=hashlib.sha256(
                        json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
                    provider=args.provider, model=args.model, effort=args.effort,
                    max_output=args.max_output, rates=args.rates)
    directory.mkdir(parents=True, exist_ok=True)
    metadata_path = directory / "run.json"
    if metadata_path.exists():
        if read(metadata_path) != metadata:
            raise ValueError("output directory belongs to a different run configuration")
    elif any(directory.iterdir()):
        raise ValueError("output directory must be empty for a new run")
    else:
        write(metadata_path, metadata)
    pending_paths = list(directory.glob("*.pending"))
    if pending_paths and not args.retry_uncertain:
        raise ValueError("uncertain requests need manual reconciliation or --retry-uncertain")
    uncertain = directory / "uncertain"
    for path in pending_paths:
        uncertain.mkdir(exist_ok=True)
        path.rename(uncertain / f"{path.stem}-{uuid.uuid4().hex}.json")
    for item, stage, prompt in requests_for(items):
        path = row_path(directory, item, stage)
        if path.exists():
            row = read(path)
            if row["prompt"] != prompt or row["answers"] != item["answers"]:
                raise ValueError(f"existing transcript mismatch: {path}")
    spent = (sum(read(p)["cost"] for p in directory.glob("*.json") if p.name != "run.json")
             + sum(read(p)["reservation"] for p in uncertain.glob("*.json")))
    if spent > args.budget:
        raise ValueError("recorded and uncertain costs exceed budget")
    reserved = 0.0
    lock = threading.Lock()

    def call(job):
        nonlocal spent, reserved
        item, stage, prompt = job
        path = row_path(directory, item, stage)
        cost_bound = reservation(prompt)
        pending = path.with_suffix(".pending")
        started = datetime.now(timezone.utc).isoformat()
        with lock:
            if spent + reserved + cost_bound > args.budget:
                raise ValueError("budget cannot cover the next maximum-cost request")
            write(pending, {"reservation": cost_bound, "started_utc": started})
            reserved += cost_bound
        result = provider_request(conf, [{"role": "user", "content": prompt}], timeout=600)
        usage = result["usage"]
        row = dict(world=item["world_seed"], language=item["language_seed"],
                   level=item["level"], order_index=item["order_index"], stage=stage,
                   prompt=prompt, answers=item["answers"], raw=result["raw"],
                   marks=score(result["raw"], item["answers"]),
                   requested_model=args.model, model=result["model"], effort=args.effort,
                   max_output=args.max_output, started_utc=started,
                   finish_reason=result["finish_reason"],
                   capped=result["finish_reason"] in CAPPED, usage=usage,
                   cost=price(conf, usage["prompt_tokens"], usage["completion_tokens"]))
        write(path, row)
        with lock:
            spent += row["cost"]
            reserved -= cost_bound
            pending.unlink()
        print(item["world_seed"], stage, f"{sum(row['marks'])}/{len(row['marks'])}",
              f"${spent:.4f}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(call, todo))


if __name__ == "__main__":
    main()
