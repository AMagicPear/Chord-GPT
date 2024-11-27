import gzip
import json
import os
from src.interfaces import KeyToneDict

def load_key_tone_dict() -> KeyToneDict:
    key_tone_dict_path = "./datasets/key_tone_dict.json"
    if os.path.exists(key_tone_dict_path):
        with open(key_tone_dict_path,'r',encoding='utf8') as file:
            key_tone_dict = json.load(file)
        return key_tone_dict
    else:
        result_dict = {}
        key_tone_dict = {}
        file_path = "./datasets/Hooktheory_Raw.json.gz"
        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            data = json.load(file)
            for key, value in data.items():
                if "json" in value:
                    result_dict[key] = value["json"]
        for song in result_dict:
            if result_dict[song]:
                key_tone_dict[song] = result_dict[song]['keys']
        with open(key_tone_dict_path,'w+') as file:
            json.dump(key_tone_dict,file)
        return key_tone_dict