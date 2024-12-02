# 南京邮电大学大学生创新创业训练计划项目：
# 音乐生成的算法研究
# 使用Transformer架构测试
import torch
import numpy as np
import torch.nn as nn
from src.prepare_data import load_songid_tone_dict

device = (
    "mps"
    if torch.mps.is_available()
    else "cuda" if torch.cuda.is_available() else "cpu"
)

# key_tone_dict包含各个歌的调式信息，内部是一个列表，表示每首歌的1或多个片段
# 其中每个片段是一个字典，包括'beat'（ TODO 还不知道是啥）,'tonic','scale'三个值
songid_tone_dict = load_songid_tone_dict()