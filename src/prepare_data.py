import gzip
import json
import os
import torch
import pickle
import random
import musicpy
import musicpy.database

_polychords_dict = {
    (1, 4, 1, 4, 11): 0,
    (2, 3, 2, 4, 9): 1,
    (3, 3, 1, 4, 10): 2,
    (3, 4, 7, 4): 3,
    (3, 3, 3, 8): 4,
    (2, 3, 2, 4, 7): 5,
    (5, 1, 8): 6,
    (4, 3, 4, 4, 5): 7,
    (4, 3, 8, 3): 8,
    (4, 4, 3, 2, 6, 2): 9,
    (4, 3, 6, 4): 10,
    (4, 3, 3, 8, 2): 11,
}
reverse_polychords_dict = {v: k for k, v in _polychords_dict.items()}
chord_types = musicpy.database.chordTypes.keys()
num_intervals = len(musicpy.database.NAME_OF_INTERVAL)  # 22
num_chord_types = len(chord_types)  # 61
chord_intevals_size = (
    num_intervals + num_chord_types + len(_polychords_dict.keys())
)  # 95
chord_vocab_size = chord_intevals_size * 12


def load_harmonys(
    split: str, file_path="datasets/Hooktheory.json.gz"
) -> dict[str, list[dict[str, any]]]:
    """从文件中读取各歌曲的和弦进行"""
    harmony_cache = f"./cache/harmony_{split}.pkl"
    harmonys = dict()
    if os.path.exists(harmony_cache):
        with open(harmony_cache, "rb") as cache:
            harmonys = pickle.load(cache)
        return harmonys
    else:
        with gzip.open(file_path, "rt") as file:
            data = json.load(file)
            for key, value in data.items():
                harmony = value["annotations"]["harmony"]
                # 排除一些特殊的没有标明和声进行的歌曲
                if (
                    value["split"] == split.upper()
                    and harmony != None
                    and len(harmony) > 0
                ):
                    harmonys[key] = harmony
        with open(harmony_cache, "wb") as cache:
            pickle.dump(harmonys, cache)
        return harmonys


def encode_chord_interval_multihot(interval: list):
    """采用多热编码，编码和弦的音程关系（暂时弃用）"""
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
        harmony = random.choice(list(harmonys_raw.values()))
        while harmony == None or len(harmony) - block_size - 1 <= 0:
            harmony = random.choice(list(harmonys_raw.values()))
        start_idx = random.randint(0, len(harmony) - block_size - 1)
        selected_harmony = harmony[start_idx : start_idx + block_size + 1]
        for j in range(block_size):
            for data, chord in zip(
                (batch_data_x, batch_data_y),
                (selected_harmony[j], selected_harmony[j + 1]),
            ):
                data["durations"][i, j, 0] = chord["offset"] - chord["onset"]
                data["root_pitchs"][i, j, 0] = chord["root_pitch_class"]
                data["intervals"][i, j] = encode_chord_interval_multihot(
                    chord["root_position_intervals"]
                )
                data["inversions"][i, j, 0] = chord["inversion"]

    return batch_data_x, batch_data_y


def make_up_chord(raw_chord: dict[str, any]):
    """使用MusicPy库，将原始和弦数据转换为MusicPy和弦类型"""
    # 由于本项目使用首调，所以不妨设根音为C，不会影响其他判断
    base_note = musicpy.N("C5").up(raw_chord["root_pitch_class"])
    raw_interval = raw_chord["root_position_intervals"]
    chord = musicpy.chord(
        [base_note]
        + [base_note.up(sum(raw_interval[: i + 1])) for i in range(len(raw_interval))]
    )
    return chord


def _encode_chord_type(chord_type):
    """对三音及以上的普通和弦类型编码"""
    chord_types = musicpy.database.chordTypes.keys()
    chord_type_dict = {
        chord: idx for idx, chords in enumerate(chord_types) for chord in chords
    }
    return chord_type_dict.get(chord_type, None)


def encode_chord_interval(raw_chord: dict[str, any]) -> int | None:
    """根据和弦每两个音之间的相对音程列表编码和弦音程类型"""
    raw_interval = raw_chord["root_position_intervals"]
    # 当和弦是单音时直接返回0
    if len(raw_interval) == 0:
        return 0
    # 双音及以上和弦使用MusicPy分析
    chord = make_up_chord(raw_chord)
    detect = musicpy.alg.detect(
        chord,
        show_degree=True,
        get_chord_type=True,
    )
    # 当和弦是双音时编码为双音间音程
    if len(raw_interval) == 1:
        interval_name = detect.interval_name
        return musicpy.database.NAME_OF_INTERVAL[interval_name]
    chord_type = detect.chord_type
    polychords = detect.polychords
    # 是普通和弦时接着前面继续编码
    if chord_type:
        # 可以正确得到编码时返回附加编码，否则返回None
        code = _encode_chord_type(chord_type)
        return (code + num_intervals) if code != None else None
    # 是复合和弦时
    if polychords:
        offset = num_intervals + num_chord_types
        code = _polychords_dict[tuple(raw_interval)]
        return offset + code
    # 理论上不会运行到这里
    return None


def encode_chord_root_pitch(raw_chord: dict[str, any]) -> int:
    root_pitch = raw_chord["root_pitch_class"]
    return root_pitch


def encode_chord_all(raw_chord: dict[str, any]):
    chord_interval_encoded = encode_chord_interval(raw_chord)
    chord_root_pitch_encoded = encode_chord_root_pitch(raw_chord)
    chord_allover_encoded = (
        chord_root_pitch_encoded * chord_intevals_size + chord_interval_encoded
    )
    return chord_allover_encoded


def decode_chord(root_pitch: int, interval_code: int, scale_pitch=0) -> musicpy.chord:
    if interval_code == 0:
        chord_decoded = musicpy.C([musicpy.N("C")])
    elif interval_code < num_intervals:
        chord_decoded = musicpy.get_chord_by_interval("C", [interval_code])
    elif interval_code < num_intervals + num_chord_types:
        chord_type_code = interval_code - num_intervals
        chord_type_reverse_dict = {
            idx: chord for idx, chords in enumerate(chord_types) for chord in chords
        }
        chord_type = chord_type_reverse_dict[chord_type_code]
        chord_decoded = musicpy.get_chord("C", chord_type)
    elif interval_code < chord_intevals_size:
        polychords_type_code = interval_code - num_intervals - num_chord_types
        poly_interval = list(reverse_polychords_dict[polychords_type_code])
        chord_decoded = musicpy.get_chord_by_interval("C", poly_interval)
    return chord_decoded.up(root_pitch + scale_pitch)


def decode_chord_from_all_encoded(encoded_chord: int):
    root_pitch = encoded_chord // chord_intevals_size
    interval_code = encoded_chord % chord_intevals_size
    return decode_chord(root_pitch, interval_code)


if __name__ == "__main__":
    # harmonys = load_harmonys("train")
    # count_chord_type = [0] * chord_vocab_size
    # for harmony in harmonys.values():
    #     for chord in harmony:
    #         count_chord_type[encode_chord_all(chord)] += 1
    # print(count_chord_type)
    for i in range(chord_intevals_size):
        chord_decoded = decode_chord(0, i)
        print(chord_decoded, i)
        musicpy.play(chord_decoded, wait=True)
