import torch
import json
from src.prepare_data import encode_chord_interval_multihot
import gzip

with open("./tests/不常规音程集合.json", "r") as f:
    data = json.load(f)
    chord_tones = [tone for tone in data]

test_tones = chord_tones[0:10]
print(test_tones)

# encode_test = encode_chord_interval(test_tones[0])
# print(encode_test)
max_chord_length = 0
max_chord_length_song = None
with gzip.open("./datasets/Hooktheory.json.gz", "rt") as file:
    data = json.load(file)
    duration = set()
    for key, song in data.items():
        if "annotations" in song:
            if "harmony" in song["annotations"]:
                harmony = song["annotations"]["harmony"]
                if harmony:
                    for chord in harmony:
                        chord_length = chord["offset"] - chord["onset"]
                        duration.add(chord_length)
                        if chord_length>max_chord_length:
                            max_chord_length = chord_length
                            max_chord_length_song = key
    max_chord_length_song = data[max_chord_length_song]         

# with open("./tests/和弦长度的可能取值.json", "w") as f:
#     f.write(duration)
with open('./tests/和弦长度最大的歌曲信息.json','w') as f:
    json.dump(max_chord_length_song,f)