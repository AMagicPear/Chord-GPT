import gzip
import json

borrowed_set = []
file_path = "./datasets/Hooktheory_Raw.json.gz"

# with gzip.open(file_path, "rt", encoding="utf-8") as file:
#     data = json.load(file)
#     for song in data.values():
#         if song["json"]:
#             if song["json"]["chords"]:
#                 if len(song["json"]["chords"]) != 0:
#                     for chord in song["json"]["chords"]:
#                         if chord["borrowed"]:
#                             borrowed_set.append(
#                                 (
#                                     song["id"],
#                                     chord["beat"],
#                                     chord["borrowed"],
#                                     song["urls"]["song"],
#                                 )
#                             )
# with open("./tests/borrowed.txt", "w+") as file:
#     for borrowed in borrowed_set:
#         song_id, beat, borrowed_scale, url = borrowed
#         if borrowed_scale:
#             borrowed_str = str(borrowed)
#             file.write(borrowed_str)
#             file.write("\n")

with gzip.open(file_path,'rt',encoding='utf-8') as file:
    data = json.load(file)
    for song in data.values():
        if song['id'] == 15232:
            special_song_chord = song['json']['chords']

with open('./tests/special_song_chord.json','w+') as file:
    json.dump(special_song_chord,file)