import gzip
import json
import os
import torch
import pickle
import random

file_path = "datasets/Hooktheory.json.gz"


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
    vector[0] = 1.0
    for i in range(len(interval)):
        vector[sum(interval[0 : i + 1]) % 12] = 1.0
    return vector


def get_batch_data(split, batch_size, block_size) -> dict:
    harmonys_raw = load_harmonys(split)
    def initialize_batch_data():
        return {
            "durations": torch.zeros(batch_size, block_size, 1),
            "root_pitchs": torch.zeros(batch_size, block_size, 1, dtype=torch.int),
            "intervals": torch.zeros(batch_size, block_size, 12),
            "inversions": torch.zeros(batch_size, block_size, 1, dtype=torch.int),
        }
    
    batch_data_x = initialize_batch_data()
    batch_data_y = initialize_batch_data()
    
    for i in range(batch_size):
        harmony = random.choice(harmonys_raw)
        while harmony == None or len(harmony) - block_size - 1 <= 0:
            harmony = random.choice(harmonys_raw)
        start_idx = random.randint(0, len(harmony) - block_size - 1)
        selected_harmony = harmony[start_idx : start_idx + block_size + 1]
        for j in range(block_size):
            for data, chord in zip((batch_data_x, batch_data_y), (selected_harmony[j], selected_harmony[j + 1])):
                data["durations"][i, j, 0] = chord["offset"] - chord["onset"]
                data["root_pitchs"][i, j, 0] = chord["root_pitch_class"]
                data["intervals"][i, j] = encode_chord_interval(chord["root_position_intervals"])
                data["inversions"][i, j, 0] = chord["inversion"]
                
    return batch_data_x, batch_data_y
