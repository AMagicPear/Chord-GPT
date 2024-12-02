import json
with open("./tests/b_beat.json",'r') as f:
    data = json.load(f)
    chords = data["json"]["chords"]
    chord_count = len(chords)
    print(f"Number of chords: {chord_count}")
