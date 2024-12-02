import gzip
import json
import os
import csv


def load_songid_tone_dict() -> dict[int, list[dict]]:
    """加载各首歌曲的调式调号信息"""
    key_tone_dict_path = "./datasets/key_tone_dict.csv"
    if os.path.exists(key_tone_dict_path):
        key_tone_dict = {}
        with open(key_tone_dict_path, "r", encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                song_id, keys = int(row[0]), json.loads(row[1])
                key_tone_dict[song_id] = keys
        return key_tone_dict
    else:
        result_dict = {}
        key_tone_dict = {}
        file_path = "./datasets/Hooktheory_Raw.json.gz"
        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            data = json.load(file)
            for _, value in data.items():
                if "json" in value:
                    result_dict[value["id"]] = value["json"]
        for song_id, value in result_dict.items():
            if value:
                key_tone_dict[song_id] = value["keys"]
        with open(key_tone_dict_path, "w+", encoding="utf8") as file:
            writer = csv.writer(file)
            for song_id, keys in key_tone_dict.items():
                writer.writerow([song_id, json.dumps(keys)])
        return key_tone_dict


if __name__ == "__main__":
    # key_tone_dict = load_songid_tone_dict()

    # # 检查键是否存在
    # song_id = 690062
    # if song_id in key_tone_dict:
    #     print(key_tone_dict[song_id])
    # else:
    #     print(f"Song ID {song_id} not found in key_tone_dict.")
    file_path = "./datasets/Hooktheory_Raw.json.gz"
    with gzip.open(file_path, "rt", encoding="utf-8") as file:
        data = json.load(file)
        print(data.keys())