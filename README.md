# Wordle Solver analysis

## Naive solution
Using Donald Knuth's master mind algorithm, we can solve most words within 6 attempts. We start off with word that is made of the most frequent letters.

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