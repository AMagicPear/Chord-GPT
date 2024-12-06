import torch
import torch.nn as nn
import torch.nn.functional as F
from src.prepare_data import get_batch_data
import tqdm

# 参数定义

batch_size = 64
block_size = 4
embedding_dim = 32
device = torch.device("mps" if torch.mps.is_available() else "cpu")
dropout = 0.2

class ChordEmbedding(nn.Module):
    """和弦的嵌入层"""

    def __init__(self, embedding_dim):
        super().__init__()
        self.duration_embedding = nn.Linear(1, embedding_dim)  # 持续小节数 -> 嵌入
        self.root_pitch_embedding = nn.Embedding(12, embedding_dim)  # 根音偏移 -> 嵌入
        self.interval_embedding = nn.Linear(12, embedding_dim)  # 多热向量 -> 嵌入
        self.inversion_embedding = nn.Embedding(4, embedding_dim)  # 转位信息 -> 嵌入

        self.fusion_layer = nn.Linear(4 * embedding_dim, embedding_dim)  # 融合层

    def forward(self, batchdata):
        # 各字段嵌入
        duration_emb = self.duration_embedding(batchdata["durations"])
        root_pitch_emb = self.root_pitch_embedding(batchdata["root_pitchs"].squeeze(-1))
        interval_emb = self.interval_embedding(batchdata["intervals"].float())
        inversion_emb = self.inversion_embedding(batchdata["inversions"].squeeze(-1))
        # 拼接并融合
        combined_emb = torch.cat(
            [duration_emb, root_pitch_emb, interval_emb, inversion_emb], dim=-1
        )
        fused_emb = self.fusion_layer(combined_emb)
        return fused_emb

class Head(nn.Module):
    """自注意力头"""

    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(embedding_dim, head_size, bias=False)
        self.query = nn.Linear(embedding_dim, head_size, bias=False)
        self.value = nn.Linear(embedding_dim, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # 输入 (batch, time-step, channels)
        # 输出 (batch, time-step, head size)
        B, T, C = x.shape
        k = self.key(x)  # (B,T,hs)
        q = self.query(x)  # (B,T,hs)
        # compute attention scores ("affinities")
        wei = (
            q @ k.transpose(-2, -1) * k.shape[-1] ** -0.5
        )  # (B, T, hs) @ (B, hs, T) -> (B, T, T)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))  # (B, T, T)
        wei = F.softmax(wei, dim=-1)  # (B, T, T)
        wei = self.dropout(wei)
        # perform the weighted aggregation of the values
        v = self.value(x)  # (B,T,hs)
        out = wei @ v  # (B, T, T) @ (B, T, hs) -> (B, T, hs)
        return out


class ChordModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.head = Head(embedding_dim)

    def forward(self, x, y):
        out = self.head(x)
        loss = F.cross_entropy(out, y)
        return out, loss

if __name__ == '__main__':
    chord_emd = ChordEmbedding(embedding_dim)
    xb, yb = get_batch_data("test", batch_size, block_size)

    # x_emb = chord_emd(xb)
    # print(x_emb[0])
    # y_emb = chord_emd(yb)

    chord_model = ChordModel()
    optimizer = torch.optim.AdamW(chord_model.parameters(), lr=0.3)

    for opoch in tqdm.trange(100):
        xb, yb = get_batch_data("train", batch_size, block_size)
        x_emb = chord_emd(xb)
        y_emb = chord_emd(yb)
        out, loss = chord_model(x_emb, y_emb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        tqdm.tqdm.write("loss:" + str(loss.item()))
