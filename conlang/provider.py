"""Provider transport. Sends only the given messages: no system prompt, no tools."""
import json
import os
import urllib.request

OPENAI = "https://api.openai.com/v1/chat/completions"
ANTHROPIC = "https://api.anthropic.com/v1/messages"


def request(conf, messages, timeout=75):
    """Return dict(raw, usage, model, finish_reason). Usage uses prompt/completion token names."""
    provider = conf.get("provider", "OpenAI")
    if provider == "OpenAI":
        payload = dict(model=conf["model"], messages=messages,
                       max_completion_tokens=conf["max_completion_tokens"])
        if conf["temperature"] is not None:
            payload["temperature"] = conf["temperature"]
        if conf["effort"] != "default":
            payload["reasoning_effort"] = conf["effort"]
        url, headers = OPENAI, {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]}
    elif provider == "Anthropic":
        payload = dict(model=conf["model"], messages=messages, max_tokens=conf["max_completion_tokens"])
        if conf["temperature"] is not None:
            payload["temperature"] = conf["temperature"]
        if conf["effort"] != "default":
            payload["output_config"] = {"effort": conf["effort"]}
        url = ANTHROPIC
        headers = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}
    else:
        raise ValueError(f"unknown provider: {provider}")
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=True).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    if provider == "OpenAI":
        return dict(raw=data["choices"][0]["message"].get("content") or "", usage=data["usage"],
                    model=data["model"], finish_reason=data["choices"][0].get("finish_reason"))
    usage = data["usage"]
    text = "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
    return dict(raw=text, model=data["model"], finish_reason=data.get("stop_reason"),
                usage=dict(prompt_tokens=usage["input_tokens"], completion_tokens=usage["output_tokens"],
                           raw_provider_usage=usage))


def body_size(conf, messages):
    """Conservative UTF-8 byte count of the request body, for budget reservations."""
    return len(json.dumps(dict(model=conf["model"], effort=conf["effort"], messages=messages),
                          ensure_ascii=True).encode())
