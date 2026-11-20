"""One fresh user message per request. A bundle journals charges and supports resume."""
import contextlib
import json
import math
import os
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import VERSION
from .suite import certified, digest, read, write

MODELS = {
    "gpt-4o-mini-2024-07-18": (0.15, 0.60),
    "gpt-4.1-mini-2025-04-14": (0.40, 1.60),
}
PRICE_DATE = "2026-11-19"
ENDPOINT = "https://api.openai.com/v1/chat/completions"


def now():
    return datetime.now(timezone.utc).isoformat()


def settings(model, effort, limit, rates=None):
    rates = rates or MODELS.get(model)
    if not rates or any(not math.isfinite(x) or x < 0 for x in rates) or limit <= 0:
        raise ValueError("provide valid prices per million tokens and a positive output limit")
    return dict(provider="OpenAI", model=model, effort=effort, temperature=0 if effort == "default" else None,
                max_completion_tokens=limit, input_usd_per_million=rates[0],
                output_usd_per_million=rates[1], price_date=PRICE_DATE if model in MODELS else now()[:10])


def price(conf, inputs, outputs):
    return (inputs * conf["input_usd_per_million"] + outputs * conf["output_usd_per_million"]) / 1e6


def bound(conf, prompt):
    # UTF-8 bytes bound visible BPE tokens. Allow 128 extra tokens for one chat envelope.
    return price(conf, len(prompt.encode()) + 128, conf["max_completion_tokens"])


def new_bundle(manifest, prompts, conf):
    rev = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return dict(version=VERSION, suite=manifest["name"], suite_hash=digest([manifest, prompts]),
                benchmark_commit=rev.stdout.strip() or "uncommitted", started=now(), settings=conf,
                responses={}, attempts=[], usage_summary={})


@contextlib.contextmanager
def locked(path):
    """OS releases the advisory lock even if a run is killed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(".lock").open("a+b") as f:
        f.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def summarize(bundle):
    usage = [r["usage"] for r in bundle["responses"].values()]
    total = sum(r["cost_usd"] for r in bundle["responses"].values())
    reserved = sum(a["reserved_usd"] for a in bundle["attempts"] if a["status"] in ("pending", "uncertain"))
    return dict(input_tokens=sum(u["prompt_tokens"] for u in usage),
                output_tokens=sum(u["completion_tokens"] for u in usage),
                reasoning_tokens=sum(u.get("completion_tokens_details", {}).get("reasoning_tokens", 0) for u in usage),
                list_price_usd=total, outstanding_reservations_usd=reserved)


def run(manifest, conf, path, budget):
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError("positive finite budget required")
    prompts, _ = certified(manifest)
    key = os.environ["OPENAI_API_KEY"]
    path = Path(path)
    with locked(path):
        bundle = read(path) if path.exists() else new_bundle(manifest, prompts, conf)
        if bundle["suite_hash"] != digest([manifest, prompts]) or bundle["settings"] != conf:
            raise ValueError("resume requires identical settings and suite")
        for item, prompt in prompts.items():
            if item in bundle["responses"]:
                continue
            worst = bound(conf, prompt)
            summary = summarize(bundle)
            if summary["list_price_usd"] + summary["outstanding_reservations_usd"] + worst > budget:
                raise ValueError("bundle spending limit reached")
            attempt = dict(item=item, time=now(), reserved_usd=worst, status="pending")
            bundle["attempts"].append(attempt)
            bundle["usage_summary"] = summarize(bundle)
            write(path, bundle)
            payload = dict(model=conf["model"], messages=[dict(role="user", content=prompt)],
                           max_completion_tokens=conf["max_completion_tokens"])
            if conf["temperature"] is not None:
                payload["temperature"] = conf["temperature"]
            if conf["effort"] != "default":
                payload["reasoning_effort"] = conf["effort"]
            request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
                                             headers={"Authorization": "Bearer " + key,
                                                      "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(request, timeout=75) as resp:
                    data = json.load(resp)
                usage = data["usage"]
                cost = price(conf, usage["prompt_tokens"], usage["completion_tokens"])
                raw = data["choices"][0]["message"].get("content") or ""
                bundle["responses"][item] = dict(prompt_hash=digest(prompt), raw=raw,
                    model_revision=data["model"], usage=usage, cost_usd=cost, time=now())
                attempt["status"] = "completed"
            except urllib.error.HTTPError as exc:
                try:
                    code = json.loads(exc.read()).get("error", {}).get("code")
                except ValueError:
                    code = None
                attempt.update(status="rejected" if 400 <= exc.code < 500 else "uncertain",
                               http_status=exc.code, error_code=code)
                raise ValueError(f"provider HTTP {exc.code} ({code}); progress saved") from None
            except Exception:
                attempt["status"] = "uncertain"
                raise
            finally:
                bundle["usage_summary"] = summarize(bundle)
                write(path, bundle)
            if len(bundle["responses"]) % 12 == 0:
                print(f"{len(bundle['responses'])}/{len(prompts)} responses", flush=True)
        return bundle
