from src.prepare_data import *

input_chords = [
    {
        "onset": 0,
        "offset": 2,
        "root_pitch_class": 0,
        "root_position_intervals": [4, 3],
        "inversion": 0,
    },
    {
        "onset": 2,
        "offset": 4,
        "root_pitch_class": 7,
        "root_position_intervals": [4, 3],
        "inversion": 0,
    }
]
input_chords_encoded = [encode_chord_all(input_chord) for input_chord in input_chords]
print(input_chords_encoded)
decode = [decode_chord_from_all_encoded(input_chord_encoded) for input_chord_encoded in input_chords_encoded]
print(decode)