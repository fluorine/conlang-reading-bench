"""Tier 5: progressive rule disclosure over a multi-feature conlang."""
import hashlib
import json
from collections import Counter
from random import Random

from .scoring import parse_final_answer
from .suite import read
from .tier5_grammar import (LABELS, LEVELS, card_orders, card_text, family_text, level,
                            sample_language)
from .tier5_verify import Unknown, answer_sets
from .tier5_world import (answer, english, make_lines, question_text, render,
                          select_questions, _transfer)

PROTOCOL = "tier5-0.1"
QUESTIONS = 6
ATTEMPTS = 200
# Fixed per level so every story and model shares the same four card orders.
ORDER_SEED = 5


def _instruction(count):
    return (f"You may reason before answering. End your reply with a JSON array of "
            f"{count} names in question order.")


def build_story(world_seed, language_seed, level_name, order_index, answerability=False):
    """Return one Tier 5 item with a prompt for every disclosure stage."""
    lvl = level(level_name)
    lang = sample_language(language_seed, lvl)
    order = card_orders(lvl, ORDER_SEED)[order_index % 4]
    for attempt in range(ATTEMPTS):
        rng = Random(world_seed * 1000 + attempt)
        drawn = make_lines(rng, lvl, lang)
        if drawn is None:
            continue
        people, membership, initial, text = drawn
        chosen = select_questions(rng, lvl, lang, membership, initial, text, QUESTIONS)
        if chosen is None:
            continue
        lines = render(lvl, lang, membership, initial, text)
        specs = [spec for spec, _, _ in chosen]
        gold = [value for _, value, _ in chosen]
        final = answer_sets(lvl, lang, membership, lines, specs, set(order))
        if final != [{g} for g in gold]:
            continue
        break
    else:
        raise ValueError("no admissible story within the attempt limit")
    questions = [question_text(spec) for spec in specs]
    lexicon = "; ".join(f"{word} = {meaning}" for meaning, word in lang["roots"].items())
    question_block = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
    prompts = []
    for stage in range(len(order) + 1):
        cards = [card_text(card, lang, lvl, membership) for card in order[:stage]]
        revealed = "\n".join("- " + c for c in cards) if cards else "None yet."
        prompts.append("\n\n".join([
            "Read a story written in an invented language, then answer the questions.",
            "Grammar family:\n" + family_text(lvl),
            "Word meanings: " + lexicon + ".",
            "Rules revealed so far:\n" + revealed,
            "Story:\n" + "\n".join(lines),
            "Questions:\n" + question_block,
            _instruction(QUESTIONS),
        ]))
    english_prompt = "\n\n".join([
        "Read the story, then answer the questions.",
        "Story:\n" + "\n".join(english(initial, text)),
        "Questions:\n" + question_block,
        _instruction(QUESTIONS),
    ])
    item = dict(level=level_name, world_seed=world_seed, language_seed=language_seed,
                order_index=order_index % 4, cards=order, prompts=prompts,
                english=english_prompt, questions=questions, specs=[list(s) for s in specs],
                answers=gold, tags=[sorted(tags) for _, _, tags in chosen],
                baselines=baselines(lvl, initial, text, specs, gold),
                classes={p: LABELS[l] for p, l in membership.items()})
    if answerability:
        item["answerable"] = stage_answerability(lvl, lang, membership, lines, specs, order)
    return item


def stage_answerability(lvl, lang, membership, lines, specs, order, cap=300_000):
    """Per stage: one bool per question, or None when the search hit its cap."""
    out = []
    for stage in range(len(order) + 1):
        try:
            sets = answer_sets(lvl, lang, membership, lines, specs, set(order[:stage]), cap)
            out.append([len(s) == 1 for s in sets])
        except Unknown:
            out.append(None)
    return out


def baselines(lvl, initial, text, specs, gold):
    """Shortcut readers that use only visible information. Accuracy per reader."""
    names = [p for line in text for p, _, pronoun in line["persons"] if not pronoun]
    counts = Counter(names)
    constant = {
        "last_name": names[-1],
        "first_name": names[0],
        "most_frequent": max(counts, key=lambda p: (counts[p], -names.index(p))),
    }
    out = {key: sum(value == g for g in gold) / len(gold) for key, value in constant.items()}
    for key in ("english_order", "suffix_blind"):
        holder, transfers, last = dict(initial), [], None
        for line in text:
            persons = []
            for person, _, pronoun in line["persons"]:
                persons.append(last if pronoun else person)
                last = persons[-1]
            agent, other = persons
            if key == "suffix_blind":
                giver, recipient = _transfer(line["verb"], agent, other)
                if holder[line["obj"]] != giver:
                    agent, other = other, agent
            giver, recipient = _transfer(line["verb"], agent, other)
            holder[line["obj"]] = recipient
            transfers.append((line["obj"], giver, recipient))
        predicted = [answer(initial, transfers, spec) for spec in specs]
        out[key] = sum(p == g for p, g in zip(predicted, gold)) / len(gold)
    return out


def prompts_digest(items):
    """Hash of every prompt and gold answer, to detect generator drift."""
    payload = [[item["prompts"], item["english"], item["answers"]] for item in items]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=True).encode()).hexdigest()


def load_manifest(path):
    """Read a Tier 5 manifest, rebuild its items and check the frozen digest."""
    manifest = read(path)
    stories = manifest.get("stories")
    if (manifest.get("protocol") != PROTOCOL or manifest.get("level") not in LEVELS
            or not stories or len({tuple(s[:2]) for s in stories}) != len(stories)):
        raise ValueError("not a Tier 5 manifest")
    items = [build_story(w, l, manifest["level"], o) for w, l, o in stories]
    if prompts_digest(items) != manifest.get("prompts_sha256"):
        raise ValueError("generator output differs from the frozen manifest")
    return manifest, items


def score(raw, answers):
    parsed = parse_final_answer(raw, max_items=len(answers))
    return [i < len(parsed) and parsed[i] == gold.casefold() for i, gold in enumerate(answers)]
