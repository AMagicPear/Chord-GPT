from typing import List, Dict
# 定义每个片段的类
class Segment:
    def __init__(self, beat: str, tonic: str, scale: str):
        self.beat = beat
        self.tonic = tonic
        self.scale = scale

# 定义 KeyToneDict 类
class KeyToneDict:
    def __init__(self, key_tone_dict: Dict[str, List[Segment]]):
        self.key_tone_dict = key_tone_dict