"""One fixed question with progressively layered, reversible sound changes."""
from .suite import certified, load_suite

SOURCE = "grammarcombined"
STORY = "w1459502337-l803843998"
VOWELS = "aeiou"


def build(layers):
    if not 0 <= layers <= 12:
        raise ValueError("layer count must be between 0 and 12")
    prompts, keys = certified(load_suite(SOURCE))
    prompt = prompts[STORY + "/minimal"]
    parts = prompt.split("\n\n")
    story = parts[2].splitlines()
    rules = []
    for layer in range(layers):
        divisor = layer + 2
        rules.append(f"On transfers divisible by {divisor}, advance each ending vowel "
                     "one step around a→e→i→o→u→a. Apply this rule after all earlier sound rules.")
        for index in range(3, len(story)):
            if (index - 2) % divisor == 0:
                words = []
                for word in story[index].split():
                    name, suffix = word.split("-")
                    words.append(name + "-" + suffix.translate(str.maketrans(VOWELS, VOWELS[1:] + VOWELS[0])))
                story[index] = " ".join(words)
    # The rendering has an exact inverse; names and initial statements are unchanged.
    restored = story.copy()
    for layer in reversed(range(layers)):
        divisor = layer + 2
        for index in range(3, len(restored)):
            if (index - 2) % divisor == 0:
                words = []
                for word in restored[index].split():
                    name, suffix = word.split("-")
                    words.append(name + "-" + suffix.translate(str.maketrans(VOWELS[1:] + VOWELS[0], VOWELS)))
                restored[index] = " ".join(words)
    if restored != parts[2].splitlines():
        raise ValueError("sound rules did not round-trip")
    instruction = ("Answer the question. The answer is Ada, Bo, Cy, Dee, Eli, or Fay. "
                   "Return only a JSON array containing the one name.")
    question = "Who holds the coin at the end?"
    full = "\n\n".join([instruction, parts[1], "\n".join(rules), "\n".join(story), question])
    return full, keys[STORY]["answers"][2]
