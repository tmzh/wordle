from unittest import TestCase
from wordle import  compare


class Test(TestCase):
    def test_compare(self):
        params = [
            # left,   right, (left_as_guess, right_as_guess)
            ['other', 'arose', ('yrryy', 'ryyry')],
            ['other', 'quick', ('rrrrr', 'rrrrr')],
            ['other', 'bored', ('yrrgy', 'ryygr')],
            ['other', 'other', ('ggggg', 'ggggg')],
            ['other', 'ether', ('rgggg', 'rgggg')],
            ['other', 'abade', ('rrryr', 'rrrry')],
         ]
        for word, guess, pattern in params:
            with self.subTest():
                self.assertEqual(compare(word, guess), pattern)
