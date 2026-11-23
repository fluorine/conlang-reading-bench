"""Suffix-blind holder possibilities at an intermediate story checkpoint."""
from itertools import permutations, product

from .three_object_probe import PEOPLE
from .tier4_dynamic import OBJECTS


def suffix_blind_checkpoint(prompt, checkpoint):
    """Return target-holder sets compatible with every unmarked transfer.

    Forward states are intersected with states that can complete the remaining
    lines. The answer is an over-approximation of any suffix-aware solution.
    """
    lines = prompt.split('\n\n')[2].splitlines()[1:]
    initial = tuple(line.split()[0] for line in lines[:len(OBJECTS)])
    transfers = [[word.split('-')[0] for word in line.split()]
                 for line in lines[len(OBJECTS):]]
    if type(checkpoint) is not int or not 1 <= checkpoint <= len(transfers):
        raise ValueError('invalid checkpoint')
    states = {initial}
    for names in transfers[:checkpoint]:
        following = set()
        for state in states:
            for index, (giver, receiver) in product(range(len(OBJECTS)), permutations(names)):
                if state[index] == giver:
                    updated = list(state)
                    updated[index] = receiver
                    following.add(tuple(updated))
        states = following
    viable = set(product(PEOPLE, repeat=len(OBJECTS)))
    for names in reversed(transfers[checkpoint:]):
        previous = set()
        for state in viable:
            for index, (giver, receiver) in product(range(len(OBJECTS)), permutations(names)):
                if state[index] == receiver:
                    updated = list(state)
                    updated[index] = giver
                    previous.add(tuple(updated))
        viable = previous
    states &= viable
    return [{state[index] for state in states} for index in range(len(OBJECTS))]
