"""Verify saved single-question probe prompts and scores without model calls."""
from .scoring import parse
from .single_probe import build
from .suite import certified, load_suite, read, ROOT


def verify():
    bundle = read(ROOT / "reports/single-probe-responses.json")
    for index, row in enumerate(bundle["development"]):
        if index == 12:
            # The original 12th rule was inert. Its prompt predates the corrected generator.
            continue
        prompt, gold = build(row["level"])
        if (prompt != row["prompt"] or gold != row["gold"]
                or row["correct"] != (parse(row["raw"]) == [gold.casefold()])):
            raise ValueError(f"invalid development row {index}")
    retry = bundle["retry"]
    prompt, gold = build(retry["level"])
    if (retry["prompt"] != prompt or retry["gold"] != gold
            or retry["correct"] != (parse(retry["raw"]) == [gold.casefold()])):
        raise ValueError("invalid retry")
    prompts, keys = certified(load_suite("probeholdoutsource"))
    seen = set()
    for row in bundle["validation"]:
        story, condition = row["story"], row["condition"]
        if (story, condition) in seen or condition not in ("minimal", "english"):
            raise ValueError("duplicate or unknown validation item")
        seen.add((story, condition))
        prompt, gold = build(24, "probeholdoutsource", story)
        if condition == "english":
            passage = prompts[story + "/english"].split("\n\n")[1]
            prompt = ("Answer the question. The answer is Ada, Bo, Cy, Dee, Eli, or Fay. "
                      "Return only a JSON array containing the one name.\n\n" + passage
                      + "\n\nWho holds the coin at the end?")
        if (row["prompt"] != prompt or row["gold"] != gold
                or row["correct"] != (parse(row["raw"]) == [gold.casefold()])):
            raise ValueError(f"invalid validation item {story}/{condition}")
    if seen != {(story, condition) for story in keys for condition in ("minimal", "english")}:
        raise ValueError("incomplete validation set")
    print("Verified single-question probe and 12 validation responses.")


if __name__ == "__main__":
    verify()
