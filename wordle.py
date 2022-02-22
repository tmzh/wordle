import os
import random
import time
from collections import Counter

from tqdm import tqdm
import pandas as pd
from scipy import stats

COMPARE_RESULTS_DICT = "patterns.h5"
compare_results_df = None


def frequency_score(word, counter):
    return sum(counter[c] for c in set(word))


def color_remaining(c, index, pattern, count):
    if count.get(c, 0):
        pattern[index] = '🟨'
        count[c] -= 1
    else:
        pattern[index] = '🟥'


def compare(this, other):
    this_count, other_count = Counter(this), Counter(other)
    this_matches, other_matches = [None] * len(this), [None] * len(other)

    for index, this_char, other_char in zip(range(5), other, this):
        if this_char == other_char:
            other_matches[index] = this_matches[index] = '🟩'
            this_count[other_char] -= 1
            other_count[this_char] -= 1

    for index, this_char, other_char in zip(range(5), this, other):
        if not this_matches[index]:
            color_remaining(this_char, index, this_matches, other_count)
            color_remaining(other_char, index, other_matches, this_count)

    return ''.join(this_matches), ''.join(other_matches)


def generate_comparison_dict():
    word_list = list(map(str.strip, open('word_list.txt').readlines()))
    df = pd.DataFrame(None, columns=word_list, index=word_list)
    for i, w1 in tqdm(enumerate(word_list)):
        df[w1][w1] = '🟩' * len(w1)
        for w2 in word_list[i + 1:]:
            this_pattern, other_pattern = compare(w1, w2)
            df[w1][w2] = other_pattern
            df[w2][w1] = this_pattern
    store = pd.HDFStore(COMPARE_RESULTS_DICT)
    store.put("df", df)
    store.close()


def entropy_score(guess, word_list):
    global compare_results_df
    if not isinstance(compare_results_df, pd.DataFrame):
        if not os.path.exists(COMPARE_RESULTS_DICT):
            generate_comparison_dict()
        compare_results_df = pd.read_hdf(COMPARE_RESULTS_DICT)
    probs = compare_results_df.loc[guess][word_list].value_counts()
    return stats.entropy(probs)


def top_word(words, use_entropy=False):
    if use_entropy:
        scores = [(entropy_score(word, words), word) for word in words]
        print(scores)
    else:
        counter = Counter()
        for w in words: counter.update(w)
        scores = [(frequency_score(word, counter), word) for word in words]
    scores.sort(reverse=True)
    return scores[0][1]


def word_matches_pattern(word, guess, pattern):
    return compare(guess, word) == pattern


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


def time_solve(target, word_list, strategy):
    start = time.time()
    steps = 0
    prev_result = None

    while word_list:
        next_guess, word_list = strategy(word_list, prev_result, steps < 3)
        print(next_guess, word_list)
        pattern = compare(next_guess, target)
        if pattern == '🟩🟩🟩🟩🟩':
            end = time.time()
            return target, steps <= 6, steps, end - start
        prev_result = next_guess, pattern
        steps += 1


def benchmark_strategy(word_list, strategy):
    words, results, steps, durations = zip(*[time_solve(target, word_list, strategy) for target in word_list])
    for no_of_steps in range(1, 7):
        print(f"{stats.percentileofscore(steps, no_of_steps, 'weak'):0.2f}% solved in {no_of_steps} steps")
    return words, results, steps, durations


def run_benchmark(target_word_list, dictionary):
    strategies = [
        # ('simple', simple_guess),
        # ('random_explore', simple_guess_with_random_explore),
        ('entropy_explore', entropy_explore)
    ]
    df = pd.DataFrame()
    for name, strategy in strategies:
        words, results, steps, durations = zip(*[time_solve(target, dictionary, strategy)
                                                 for target in target_word_list])
        df = df.append(pd.DataFrame(
            {'strategy': name, 'word': words, 'duration': durations, 'result': results, 'step': steps}))
    return df


if __name__ == "__main__":
    source_dir = os.path.dirname(__file__)
    file_name = os.path.join(source_dir, 'word_list.txt')
    dictionary = list(map(str.strip, open('word_list.txt').readlines()))
    target_word_list = list(map(str.strip, open('subset.txt').readlines()))

    df = run_benchmark(target_word_list, dictionary)
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
