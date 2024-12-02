from src.prepare_data import load_song_id_tone_dict
import gzip
import json

key_tone_dict = load_song_id_tone_dict()
file_path = "./datasets/Hooktheory_Raw.json.gz"

count = 0

with gzip.open(file_path, "rt", encoding="utf-8") as file:
    data = json.load(file)
    result_dict = {}
    for key, value in data.items():
        result_dict[value["id"]] = value
    for key in key_tone_dict:
        for song_tonics in key_tone_dict[key]:
            if song_tonics["beat"] != 1:
                count += 1
                if count == 3:
                    with open("./tests/b_beat.json", "w") as f:
                        json.dump(result_dict[key], f)
                        exit()
