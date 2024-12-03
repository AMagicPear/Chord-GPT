import gzip
import json

file_path = "datasets/Hooktheory.json.gz"
special_interval_song = dict()
with gzip.open(file_path, "rt") as file:
    data = json.load(file)
    for key, value in data.items():
        if value["annotations"]["harmony"]:
            for chord in value["annotations"]["harmony"]:
                intervals: list = chord["root_position_intervals"]
                if len(intervals) != 2:
                    if key not in special_interval_song:
                        special_interval_song[key] = value["annotations"]["harmony"]
                elif not (
                    (intervals[0] == 4 and intervals[1] == 3)
                    or (intervals[0] == 3 and intervals[1] == 4)
                ):
                    if key not in special_interval_song:
                        special_interval_song[key] = value["annotations"]["harmony"]
with open("./tests/统计出现不常规音程.json", "w") as file:
    json.dump(special_interval_song, file)
