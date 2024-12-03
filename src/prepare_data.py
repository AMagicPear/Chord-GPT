import gzip
import json
import os
import torch
import pickle

file_path = "datasets/Hooktheory.json.gz"
device = torch.device("mps" if torch.mps.is_available() else "cpu")


def load_harmonys(split: str) -> dict[str, any]:
    """从文件中读取各歌曲的和弦进行"""
    harmony_cache = f"./cache/harmony_{split}.pkl"
    harmony = []
    if os.path.exists(harmony_cache):
        with open(harmony_cache, "rb") as cache:
            harmony = pickle.load(cache)
        return harmony
    else:
        with gzip.open(file_path, "rt") as file:
            data = json.load(file)
            for value in data.values():
                if value["split"] == split.upper():
                    harmony.append(value["annotations"]["harmony"])
        with open(harmony_cache, "wb") as cache:
            pickle.dump(harmony, cache)
        return harmony


def encode_harmony(harmony: list):
    """将一个和弦进行编码为Tensor"""
    harmony_sequence = []
    for chord in harmony:
        chord_sequence = [
            chord["onset"],
            chord["offset"] - chord["onset"],
            chord["root_pitch_class"],
            *chord["root_position_intervals"],  # TODO: 任意的音阶映射到一个位置
            chord["inversion"],
        ]
        harmony_sequence.append(chord_sequence)
    harmony_tensor = torch.Tensor(harmony_sequence)
    return harmony_tensor


harmonys = load_harmonys("test")
print(harmonys[0])
print(encode_harmony(harmonys[0]))
