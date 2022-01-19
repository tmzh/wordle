from unittest import TestCase
from wordle import exclude_chars, include_matches


class Test(TestCase):
    def test_exclude_chars(self):
        words = ['arose', 'wharf', 'think']
        self.assertEqual(['think'], exclude_chars(words, ['a']))
        self.assertEqual([], exclude_chars(words, ['a', 'i']))
        self.assertEqual(words, exclude_chars(words, ['x']))
        self.assertEqual(words, exclude_chars(words, []))

    def test_include_matches(self):
        words = ['hoard', 'wharf', 'think']
        self.assertEqual(['think'], include_matches(words, {0: 't'}))
        self.assertEqual(['hoard', 'wharf'], include_matches(words, {2: 'a'}))
        self.assertEqual([], include_matches(words, {2: 'x'}))
