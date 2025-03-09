import prepare_data
import musicpy

harmonys = prepare_data.load_harmonys("train")

class Chord_after:
    def __init__(self, root: str, chord_type: str):
        self.root = root
        self.type = chord_type
    
    def to_string(self) -> str:
        return f"{self.root}{self.type}"

harmonys_after: list[list[Chord_after]] = []

for harmony_after in harmonys.values():
    chords_after: list[Chord_after] = []
    for raw_chord in harmony_after:
        chord = prepare_data.make_up_chord(raw_chord)
        detect = musicpy.alg.detect(
            chord,
            show_degree=True,
            get_chord_type=True,
        )
        chord_type = detect.chord_type
        polychords = detect.polychords
        if chord_type:
            chords_after.append(Chord_after(detect.root, chord_type))
        elif polychords:
            chords_after.append(Chord_after(detect.root, polychords))
    if len(chords_after) > 0:
        harmonys_after.append(chords_after)

# 创建数据集
import os
import csv

dataset = []
for harmony in harmonys_after:
    if len(harmony) < 2:
        continue
    mid = len(harmony) // 2
    prompt = " ".join(c.to_string() for c in harmony[:mid])
    completion = " ".join(c.to_string() for c in harmony[mid:])
    dataset.append([prompt, completion])

# 写入 CSV
# os.makedirs("datasets", exist_ok=True)
with open("datasets/harmony_pairs.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Prompt", "Completion"])
    writer.writerows(dataset)
