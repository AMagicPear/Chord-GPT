import gzip
import json

filename = "datasets/Hooktheory.json.gz"
# with gzip.open(filename,'rt') as file:
#     data = json.load(file)
#     with open("./tests/new_data.json",'w') as f:
#         count = 0
#         new_data = dict()
#         for new_key1, new_data_1 in data.items():
#             new_data[new_key1] = new_data_1
#             count += 1
#             if count == 5:
#                 json.dump(new_data,f)
#                 exit()
with gzip.open(filename,'rt') as file:
    data = json.load(file)
    with open('./tests/strange_song_scale.json','w') as f:
        json.dump(data['WeglGRKKmrY'],f)