import os
from typing import List
from collections import Counter, defaultdict


def score_word(word, counter):
    return sum(counter[c] for c in set(word))


def merge_dict(self, other):
    for key in other.keys():
        self[key].add(other[key])
    return self


def exclude_invalid_chars(words: List[str], letters: List[str]) -> List[str]:
    return list(filter(lambda word: all(letter not in word for letter in letters), words))


def check_word_pos(word, misplaced):
    for i, val in misplaced.items():
        if word[i] in val:
            return False
        if any(c not in word for c in val):
            return False
    return True


def exclude_invalid_pos(words: List[str], misplaced: defaultdict) -> List[str]:
    res = []
    for word in words:
        if check_word_pos(word, misplaced):
            res.append(word)
    return res


def include_matches(words: List[str], matches: dict) -> List[str]:
    return list(filter(lambda word: all(word[i] == matches[i] for i in matches.keys()), words))


def check(guess: str, word: str):
    matches, misplaced, incorrect = {}, {}, set()
    for i, c in enumerate(guess):
        if c == word[i]:
            matches[i] = c
        elif c in word:
            misplaced[i] = c
        else:
            incorrect.add(c)
    return matches, misplaced, incorrect


def guess_word(words, matches, incorrect, misplaced_chars, explore=True):
    if explore:
        words = set(words)
        # incorrect |= set().union(*misplaced_chars.values())
    words = include_matches(words, matches)
    words = exclude_invalid_pos(words, misplaced_chars)
    words = exclude_invalid_chars(words, incorrect)
    scores = [(score_word(set(word), c), word) for word in words]
    scores.sort(reverse=True)
    return scores[0][1], words


def benchmark_guess(target, word_list):
    matches = None
    misplaced = None
    return matches, misplaced


if __name__ == "__main__":
    source_dir = os.path.dirname(__file__)
    file_name = os.path.join(source_dir, 'word_list.txt')
    word_list = list(map(str.strip, open('word_list.txt').readlines()))

    misplaced = defaultdict(set)
    matches = {}
    incorrect = set()

    c = Counter()
    for w in word_list:
        c.update(w)

    target = 'solar'

    for i in range(6):
        next_guess, word_list = guess_word(word_list, matches, incorrect, misplaced, i < 2)
        matches_, misplaced_, incorrect_ = check(next_guess, target)
        matches = matches | matches_
        if len(matches) == 5:
            print(matches)
            break
        incorrect = incorrect | incorrect_
        misplaced = merge_dict(misplaced, misplaced_)
