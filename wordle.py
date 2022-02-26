import os
import random
import time
from abc import ABC, abstractmethod
from collections import Counter

from tqdm import tqdm
import pandas as pd
from scipy import stats

COMPARE_PATTERNS = "patterns.h5"
BENCHMARK_RESULTS = "benchmark_results.h5"


def frequency_score(word, counter):
    return sum(counter[c] for c in set(word))


def color_remaining(c, index, pattern, count):
    if count.get(c, 0):
        pattern[index] = 'y'
        count[c] -= 1
    else:
        pattern[index] = 'r'


def compare(this, other):
    this_count, other_count = Counter(this), Counter(other)
    this_matches, other_matches = [None] * len(this), [None] * len(other)

    for index, this_char, other_char in zip(range(5), other, this):
        if this_char == other_char:
            other_matches[index] = this_matches[index] = 'g'
            this_count[other_char] -= 1
            other_count[this_char] -= 1

    for index, this_char, other_char in zip(range(5), this, other):
        if not this_matches[index]:
            color_remaining(this_char, index, this_matches, other_count)
            color_remaining(other_char, index, other_matches, this_count)

    return ''.join(this_matches), ''.join(other_matches)


def entropy_score(guess, word_list):
    global compare_results_df
    if not isinstance(compare_results_df, pd.DataFrame):
        if not os.path.exists(COMPARE_PATTERNS):
            generate_comparison_dict()
        compare_results_df = pd.read_hdf(COMPARE_PATTERNS)
    probs = compare_results_df.loc[guess][word_list].value_counts()
    return stats.entropy(probs)


def top_word(words, use_entropy=False):
    if use_entropy:
        scores = [(entropy_score(word, words), word) for word in words]
    else:
        counter = Counter()
        for w in words: counter.update(w)
        scores = [(frequency_score(word, counter), word) for word in words]
    scores.sort(reverse=True)
    return scores[0][1]


def word_matches_pattern(word, guess, pattern):
    return compare(guess, word)[0] == pattern


class Solver(ABC):
    def __init__(self, word_list):
        self.word_list = word_list
        self.first_word = self.top_word(word_list)

    def top_word(self, words):
        char_counts = Counter()
        for w in words: char_counts.update(w)
        scores = [(self.score(word, words, char_counts), word) for word in words]
        scores.sort(reverse=True)
        # print(scores)
        return scores[0][1]

    def next_guess(self, words, prev_guess=None, prev_result=None, explore=False):
        if not prev_guess:
            return self.first_word, words
        words = list(filter(lambda word: word_matches_pattern(word, prev_guess, prev_result), words))
        return self.top_word(words), words

    @abstractmethod
    def score(self, word, words, char_counts):
        pass


class SimpleSolve(Solver):

    def score(self, word, words, char_counts):
        return sum(char_counts[c] for c in word)


class RandomExploreExploit(Solver):
    def next_guess(self, words, prev_guess=None, prev_result=None, explore=False):
        if not prev_guess:
            return self.first_word, words
        words = list(filter(lambda word: word_matches_pattern(word, prev_guess, prev_result), words))
        if explore:
            random.shuffle(words)
            return words[0], words[1:]
        return self.top_word(words), words

    def score(self, word, words, char_counts):
        return sum(char_counts[c] for c in word)


class EntropyExplore(Solver):

    def score(self, word, words, char_counts):
        probs = compare_results_df.loc[word][words].value_counts()
        return stats.entropy(probs)


def generate_comparison_dict(word_list):
    df = pd.DataFrame(None, columns=word_list, index=word_list)
    for i, w1 in tqdm(enumerate(word_list)):
        df[w1][w1] = 'g' * len(w1)
        for w2 in word_list[i + 1:]:
            this_pattern, other_pattern = compare(w1, w2)
            df[w1][w2] = other_pattern
            df[w2][w1] = this_pattern
    with pd.HDFStore(COMPARE_PATTERNS) as hdf:
        hdf.put(key="df", value=df)


def simple_guess(words, prev_result, explore=True):
    if prev_result:
        prev_guess, result_pattern = prev_result
        words = list(filter(lambda word: word_matches_pattern(word, prev_guess, result_pattern), words))
    return top_word(words), words


def simple_guess_with_random_explore(words, prev_result, explore=True):
    if prev_result:
        prev_guess, result_pattern = prev_result
        words = list(filter(lambda word: word_matches_pattern(word, prev_guess, result_pattern), words))
    if explore:
        random.shuffle(words)
        return words[0], words[1:]
    return top_word(words), words


def entropy_explore(words, prev_result, explore=False):
    if prev_result:
        prev_guess, result_pattern = prev_result
        words = list(filter(lambda word: word_matches_pattern(word, prev_guess, result_pattern), words))
    if explore:
        return top_word(words, use_entropy=True), words
    else:
        return top_word(words, use_entropy=False), words


def time_solve(target, word_list, solver: Solver):
    start = time.time()
    steps = 0
    last_guess = last_pattern = None

    while word_list:
        next_guess, word_list = solver.next_guess(word_list, last_guess, last_pattern, steps < 3)
        # last_pattern = compare(next_guess, target)[0]
        last_pattern = compare_results_df[target][next_guess]
        if last_pattern == 'ggggg':
            end = time.time()
            return target, steps <= 6, steps, end - start
        last_guess = next_guess
        steps += 1


def benchmark_strategy(word_list, strategy):
    words, results, steps, durations = zip(*[time_solve(target, word_list, strategy) for target in word_list])
    for no_of_steps in range(1, 7):
        print(f"{stats.percentileofscore(steps, no_of_steps, 'weak'):0.2f}% solved in {no_of_steps} steps")
    return words, results, steps, durations


def run_benchmark(target_word_list, dictionary):
    strategies = [
        ('simple', SimpleSolve),
        ('random_explore', RandomExploreExploit),
        ('entropy_explore', EntropyExplore)
    ]
    df = pd.DataFrame()
    for name, strategy in strategies:
        solver = strategy(dictionary)
        words, results, steps, durations = zip(*[time_solve(target, dictionary, solver)
                                                 for target in tqdm(target_word_list)])
        df = df.append(pd.DataFrame(
            {'strategy': name, 'word': words, 'duration': durations, 'result': results, 'step': steps}),
            ignore_index=True
        )
    return df


if __name__ == "__main__":
    source_dir = os.path.dirname(__file__)
    file_name = os.path.join(source_dir, 'word_list.txt')
    dictionary = list(map(str.strip, open('word_list.txt').readlines()))
    target_word_list = list(map(str.strip, open('subset.txt').readlines()))

    if not os.path.exists(COMPARE_PATTERNS):
        generate_comparison_dict()

    compare_results_df = pd.read_hdf(COMPARE_PATTERNS)

    df = run_benchmark(target_word_list, dictionary)
    with pd.HDFStore(BENCHMARK_RESULTS) as hdf:
        hdf.put(key="df", value=df)

