import gzip
import json

file_path = "./datasets/Hooktheory_Raw.json.gz"
# scales = set()

# with gzip.open(file_path,'rt',encoding='utf-8') as file:
#     data = json.load(file)
#     for _, value in data.items():
#         if value["json"]:
#             keys = value['json']['keys']
#             for key in keys:
#                 scales.add(key['scale'])

# with open("./tests/scale-set.txt",'w+') as file:
#     file.write("\n".join(scales))
splits = set()

with gzip.open(file_path,'rt',encoding='utf-8') as file:
    data = json.load(file)
    for _, value in data.items():
        splits.add(value['split'])

with open("./tests/spilit-set.txt",'w+') as file:
    file.write("\n".join(splits))