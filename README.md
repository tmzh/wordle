# Wordle Solver analysis

# The game
After guessing a five-letter word, the game tells you whether any of your letters are in the secret word and whether they are in the correct place. You have six tries to get it right.

The wordle website uses two dictionaries. The first one is a smaller dictionary consisting of more familiar words is used as the challenge every day. The second word list is a larger one, which consists of words that are accepted as guesses.

## Base solution
Using Donald Knuth's master mind algorithm, we can solve most words within 6 attempts. The algorith works by <...>. 

After each iteration, we have to score the remaining word list to return the best guess. 

### Character frequency

As a simple strategy, we can prioritize the words containing most common characters.  

```python
def score_word(word, counter):
    return sum(counter[c] for c in set(word))
```

Almost half the time, it only takes 3 attempts to guess the word correctly. 93% of the time we are able to guess within 6 attempts.

```
from scipy import stats

[stats.percentileofscore(df.steps, x, 'weak') for x in range(1, 7)]
Out[23]: 
[1.379895158803577,
 16.33518347209374,
 47.50231267345051,
 71.7468393462843,
 85.39161270428616,
 92.5531914893617]
```

But for certain words, the clues don't converge to a solution soon enough. For example, it takes 13 attempts to predict the word `wares`

```
time_solve('wares', word_list)
# Next guess, remaining word list
soare 12972
aesir 61
rales 32
tares 12
nares 11
dares 10
cares 9
pares 8
mares 7
hares 6
gares 5
bares 4
fares 3
wares 2
```

The problem here is that once we reach the 3rd guess `rales`, there are 13 more possibilities for the first char. The game treats solving within the first 6 attempts as a win. The best option is to explore the problem space with a bit of stochasticity in the first 3 attempts so that by the time we are down to our 4th attempt 


## First attempt
Introduce a bit of randomness while exploring

```
if explore:
    random.shuffle(words)
    return words[0]

scores = [(score_word(set(word), counter), word) for word in words]
scores.sort(reverse=True)
return scores[0][1], words
```

## Second attempt
Explore smartly so that it increases the information available while exploiting. 
1. During explore phase, avoid valid and invalid characters

## Third attempt
Use secretary problem. During exploration shuffle the list and score the first 37% of the words in the list and return the best so far.

How to score

## Fourth attempt
The intuition behind this is that first the objective during explore phase is different from exploit phase. Objective of explore phase is to maximise the information available for later choices. Low probability events convey more information about the characters that belong and don't belong to our target word. This is opposite to the exploit phase where we want to choose the high probability characters. 

* Low Probability Event: High Information
* High Probability Event: Low Information

    