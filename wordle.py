import os
import time
from math import log
from typing import List
from collections import Counter, defaultdict
import pandas as pd
from scipy import stats
import random


def frequency_score(word, counter):
    return sum(counter[c] for c in set(word))


def entropy_score(word, counter):
    total_letters = sum(counter.values())
    prob = {x: (counter[x] / total_letters) for x in counter.keys()}
    return sum(-prob[c] * log(prob[c]) for c in set(word))


def top_word(words, use_entropy=False):
    counter = Counter()
    for w in word_list: counter.update(w)
    if use_entropy:
        scores = [(entropy_score(word, counter), word) for word in words]
    else:
        scores = [(frequency_score(word, counter), word) for word in words]
    scores.sort(reverse=True)
    return scores[0][1]


def merge_dict(self, other):
    for key in other.keys():
        self[key].add(other[key])
    return self


def word_matches_pattern(word, matches, incorrect, misplaced_chars):
    for i, val in misplaced_chars.items():
        if word[i] in val:
            return False
        if any(c not in word for c in val):
            return False

    for letter in incorrect:
        if letter in word:
            return False

    for i in matches.keys():
        if word[i] != matches[i]:
            return False

    return True


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


def exclude_chars(words: List[str], letters: List[str]) -> List[str]:
    return list(filter(lambda word: all(letter not in word for letter in letters), words))


def include_matches(words: List[str], matches: dict) -> List[str]:
    return list(filter(lambda word: all(word[i] == matches[i] for i in matches.keys()), words))


def eval_guess(guess: str, word: str):
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
    words = list(filter(lambda word: word_matches_pattern(word, matches, incorrect, misplaced_chars), words))
    return top_word(words), words


def guess_word_1(words, matches, incorrect, misplaced_chars, explore=True):
    words = list(filter(lambda word: word_matches_pattern(word, matches, incorrect, misplaced_chars), words))
    if explore:
        random.shuffle(words)
        return words[0], words[1:]
    return top_word(words), words


def guess_word_2(words, matches, incorrect, misplaced_chars, explore=True):
    words = list(filter(lambda word: word_matches_pattern(word, matches, incorrect, misplaced_chars), words))
    if explore:
        # new_words = exclude_observed_chars(incorrect, matches, misplaced_chars, words)
        return top_word(words, use_entropy=True), words
    else:
        return top_word(words, use_entropy=False), words


def exclude_observed_chars(incorrect, matches, misplaced_chars, words):
    incorrect_and_misplaced = incorrect.union(*misplaced_chars.values())
    all_seen = incorrect_and_misplaced | set(matches.values())
    words_ = exclude_chars(words, all_seen)
    if not words_:
        return exclude_chars(words, incorrect_and_misplaced)
    else:
        return words_


def time_solve(target, word_list, strategy):
    start = time.time()
    misplaced, matches, incorrect = defaultdict(set), {}, set()
    steps = 0

    while word_list:
        next_guess, word_list = strategy(word_list, matches, incorrect, misplaced, steps < 3)
        matches_, misplaced_, incorrect_ = eval_guess(next_guess, target)
        if len(matches_) == 5:
            end = time.time()
            return target, steps <= 6, steps, end - start
        matches = matches | matches_
        incorrect = incorrect | incorrect_
        misplaced = merge_dict(misplaced, misplaced_)
        steps += 1


def benchmark_strategy(word_list, strategy):
    words, results, steps, durations = zip(*[time_solve(target, word_list, strategy) for target in word_list])
    for no_of_steps in range(1, 7):
        print(f"{stats.percentileofscore(steps, no_of_steps, 'weak'):0.2f}% solved in {no_of_steps} steps")
    return words, results, steps, durations


def run_benchmark(word_list):
    strategies = [('simple', guess_word), ('random_explore', guess_word_1), ('entropy_explore', guess_word_2)]
    df = pd.DataFrame()
    for name, strategy in strategies:
        words, results, steps, durations = zip(*[time_solve(target, word_list, strategy) for target in word_list])
        df = df.append(pd.DataFrame(
            {'strategy': name, 'word': words, 'duration': durations, 'result': results, 'step': steps}))
    return df


if __name__ == "__main__":
    source_dir = os.path.dirname(__file__)
    file_name = os.path.join(source_dir, 'word_list.txt')
    word_list = list(map(str.strip, open('word_list.txt').readlines()))
    word_list_2000 = list(map(str.strip, open('subset.txt').readlines()))

    df = run_benchmark(word_list_2000)
    print(df)

    # misplaced = defaultdict(set)
    # matches = {}
    # incorrect = set()

    # target = 'solar'
    #
    # for i in range(6):
    #     next_guess, word_list = guess_word(word_list, matches, incorrect, misplaced, i < 2)
    #     matches_, misplaced_, incorrect_ = check(next_guess, target)
    #     matches = matches | matches_
    #     if len(matches) == 5:
    #         print(matches)
    #         break
    #     incorrect = incorrect | incorrect_
    #     misplaced = merge_dict(misplaced, misplaced_)
