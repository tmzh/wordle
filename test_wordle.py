from unittest import TestCase
from wordle import  compare


class Test(TestCase):
    def test_compare(self):
        params = [
            # left,   right, (left_as_guess, right_as_guess)
            ['other', 'arose', ('🟨🟥🟥🟨🟨', '🟥🟨🟨🟥🟨')],
            ['other', 'quick', ('🟥🟥🟥🟥🟥', '🟥🟥🟥🟥🟥')],
            ['other', 'bored', ('🟨🟥🟥🟩🟨', '🟥🟨🟨🟩🟥')],
            ['other', 'other', ('🟩🟩🟩🟩🟩', '🟩🟩🟩🟩🟩')],
            ['other', 'ether', ('🟥🟩🟩🟩🟩', '🟥🟩🟩🟩🟩')],
            ['other', 'abade', ('🟥🟥🟥🟨🟥', '🟥🟥🟥🟥🟨')],
         ]
        for word, guess, pattern in params:
            with self.subTest():
                self.assertEqual(compare(word, guess), pattern)
