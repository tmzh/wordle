import os
import time
from typing import List
from collections import Counter, defaultdict
import pandas as pd
from scipy import stats
import random


def score_word(word, counter):
    return sum(counter[c] for c in set(word))


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


def top_word(words):
    counter = Counter()
    for w in word_list: counter.update(w)
    scores = [(score_word(word, counter), word) for word in words]
    scores.sort(reverse=True)
    return scores[0][1], words


def guess_word_1(words, matches, incorrect, misplaced_chars, explore=True):
    words = list(filter(lambda word: word_matches_pattern(word, matches, incorrect, misplaced_chars), words))
    if explore:
        random.shuffle(words)
        return words[0], words
    return top_word(words)


def guess_word_2(words, matches, incorrect, misplaced_chars, explore=True):
    if explore:
        try:
            incorrect_ = incorrect.union(*misplaced_chars.values())
            incorrect_ |= set(matches.values())
            new_words = exclude_chars(words, incorrect_)
            return random.choice(new_words), words
        except IndexError:
            pass
    return guess_word(words, matches, incorrect, misplaced_chars, explore=True)


def guess_word(words, matches, incorrect, misplaced_chars, explore=True):
    words = list(filter(lambda word: word_matches_pattern(word, matches, incorrect, misplaced_chars), words))
    return top_word(words)


def time_solve(target, word_list, strategy):
    start = time.time()
    misplaced = defaultdict(set)
    matches = {}
    incorrect = set()
    steps = 0

    while word_list:
        next_guess, word_list = strategy(word_list, matches, incorrect, misplaced, steps < 3)
        # print(next_guess, len(word_list))
        matches_, misplaced_, incorrect_ = eval_guess(next_guess, target)
        matches = matches | matches_
        if len(matches) == 5:
            end = time.time()
            # if steps > 6: print(target, steps, end - start)
            return target, steps <= 6, steps, end - start
        incorrect = incorrect | incorrect_
        misplaced = merge_dict(misplaced, misplaced_)
        steps += 1


def benchmark_strategy(word_list, strategy):
    words, results, steps, durations = zip(*[time_solve(target, word_list, strategy) for target in word_list])
    for no_of_steps in range(1, 7):
        print(f"{stats.percentileofscore(steps, no_of_steps, 'weak'):0.2f}% solved in {no_of_steps} steps")
    return words, results, steps, durations


def run_benchmark(word_list):
    strategies = [('simple', guess_word), ('random_explore', guess_word_1), ('scored_explore', guess_word_2)]
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
