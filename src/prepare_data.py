import gzip
import json
import os
import torch
import pickle
import random

file_path = "datasets/Hooktheory.json.gz"
device = torch.device("mps" if torch.mps.is_available() else "cpu")


def load_harmonys(split: str) -> list:
    """从文件中读取各歌曲的和弦进行"""
    harmony_cache = f"./cache/harmony_{split}.pkl"
    harmonys = []
    if os.path.exists(harmony_cache):
        with open(harmony_cache, "rb") as cache:
            harmonys = pickle.load(cache)
        return harmonys
    else:
        with gzip.open(file_path, "rt") as file:
            data = json.load(file)
            for value in data.values():
                if value["split"] == split.upper():
                    harmonys.append(value["annotations"]["harmony"])
        with open(harmony_cache, "wb") as cache:
            pickle.dump(harmonys, cache)
        return harmonys


def encode_chord_interval(interval: list):
    """采用多热编码，编码和弦的音程关系"""
    vector = torch.zeros(12, dtype=torch.float32)
    for i in range(len(interval)):
        vector[sum(interval[0 : i + 1]) % 12] = 1.0
    return vector


# harmonys[0][0] = {'onset': 0, 'offset': 2, 'root_pitch_class': 0, 'root_position_intervals': [3, 4], 'inversion': 0}

# batch_data = {
#     "durations": torch.rand(batch_size, block_size, 1),  # 和弦持续小节数，即上面的offset - onset
#     "root_pitchs": torch.randint(0, 12, (batch_size, block_size, 1)),  # 根音偏移，即root_pitch_class
#     "intervals": torch.randint(0, 2, (batch_size, block_size, 12)),  # 音程多热向量，即encode_chord_interval(root_position_intervals)
#     "inversions": torch.randint(0, 4, (batch_size, block_size, 1)),  # 转位信息，即inversion
# }


def get_batch_data(split, batch_size, block_size) -> dict:
    harmonys_raw = load_harmonys(split)

    batch_data = {
        "durations": torch.zeros(batch_size, block_size, 1),
        "root_pitchs": torch.zeros(batch_size, block_size, 1, dtype=torch.int),
        "intervals": torch.zeros(batch_size, block_size, 12),
        "inversions": torch.zeros(batch_size, block_size, 1, dtype=torch.int),
    }

    for i in range(batch_size):
        harmony = random.choice(harmonys_raw)
        start_idx = random.randint(0, len(harmony) - block_size)
        selected_harmony = harmony[start_idx : start_idx + block_size]

        for j, chord in enumerate(selected_harmony):
            batch_data["durations"][i, j, 0] = chord["offset"] - chord["onset"]
            batch_data["root_pitchs"][i, j, 0] = chord["root_pitch_class"]
            batch_data["intervals"][i, j] = encode_chord_interval(
                chord["root_position_intervals"]
            )
            batch_data["inversions"][i, j, 0] = chord["inversion"]

    return batch_data


if __name__ == "__main__":
    harmonys = load_harmonys("test")
    print(harmonys[0][0])
