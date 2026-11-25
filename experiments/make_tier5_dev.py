"""Write the frozen Tier 5 dev manifests, one per difficulty level."""
import argparse
from random import Random

from conlang.suite import write
from conlang.tier5 import PROTOCOL, build_story, prompts_digest
from conlang.tier5_grammar import LEVELS


def manifest(name, level_name, count, seed_text):
    rng = Random(seed_text)
    stories = []
    while len(stories) < count:
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        if any(s[:2] == [world, language] for s in stories):
            continue
        stories.append([world, language, len(stories) % 4])
    items = [build_story(w, l, level_name, o) for w, l, o in stories]
    return dict(name=name, protocol=PROTOCOL, level=level_name, stories=stories,
                prompts_sha256=prompts_digest(items))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=8)
    args = parser.parse_args(argv)
    for level_name in LEVELS:
        name = f"tier5-dev-{level_name}"
        write(f"experiments/{name}.json", manifest(name, level_name, args.count, f"{name}:seeds"))
        print(f"experiments/{name}.json")


if __name__ == "__main__":
    main()
