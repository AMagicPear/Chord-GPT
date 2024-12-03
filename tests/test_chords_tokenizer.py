import unittest
from src.chords_tokenizer import Chord

# FILE: src/test_chords_tokenizer.py


class TestChord(unittest.TestCase):

    def test_chord_initialization(self):
        chord = Chord(
            root=5,
            duration=4,
            type=1,
            inversion=2,
            applied=1,
            adds=[2, 4],
            omits=[3],
            alterations=[1],
            suspensions=[2],
            borrowed="dorian"
        )
        self.assertEqual(chord.root, 5)
        self.assertEqual(chord.duration, 4)
        self.assertEqual(chord.type, 1)
        self.assertEqual(chord.inversion, 2)
        self.assertEqual(chord.applied, 1)
        self.assertEqual(chord.adds, [2, 4])
        self.assertEqual(chord.omits, [3])
        self.assertEqual(chord.alterations, [1])
        self.assertEqual(chord.suspensions, [2])
        self.assertEqual(chord.borrowed, "dorian")

    def test_chord_default_initialization(self):
        chord = Chord()
        self.assertEqual(chord.root, 0)
        self.assertEqual(chord.duration, 0)
        self.assertEqual(chord.type, 0)
        self.assertEqual(chord.inversion, 0)
        self.assertEqual(chord.applied, 0)
        self.assertEqual(chord.adds, [])
        self.assertEqual(chord.omits, [])
        self.assertEqual(chord.alterations, [])
        self.assertEqual(chord.suspensions, [])
        self.assertEqual(chord.borrowed, "")

if __name__ == '__main__':
    unittest.main()