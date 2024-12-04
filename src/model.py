import torch
import torch.nn as nn

# 参数定义
batch_size = 2
block_size = 4
embedding_dim = 32

# 模拟和弦数据，每个batch有block_size个block，每个block有4个字段
batch_data = {
    "durations": torch.rand(batch_size, block_size, 1),  # 和弦持续小节数
    "root_pitchs": torch.randint(0, 12, (batch_size, block_size, 1)),  # 根音偏移
    "intervals": torch.randint(0, 2, (batch_size, block_size, 12)),  # 音程多热向量
    "inversions": torch.randint(0, 4, (batch_size, block_size, 1)),  # 转位信息
}


class ChordEmbedding(nn.Module):
    """和弦的嵌入层"""

    def __init__(self, embedding_dim):
        super().__init__()
        self.duration_embedding = nn.Linear(1, embedding_dim)  # 持续小节数 -> 嵌入
        self.root_pitch_embedding = nn.Embedding(12, embedding_dim)  # 根音偏移 -> 嵌入
        self.interval_embedding = nn.Linear(12, embedding_dim)  # 多热向量 -> 嵌入
        self.inversion_embedding = nn.Embedding(4, embedding_dim)  # 转位信息 -> 嵌入

        self.fusion_layer = nn.Linear(4 * embedding_dim, embedding_dim)  # 融合层

    def forward(self, durations, root_pitchs, intervals, inversions):
        # 各字段嵌入
        duration_emb = self.duration_embedding(durations)
        root_pitch_emb = self.root_pitch_embedding(root_pitchs.squeeze(-1))
        interval_emb = self.interval_embedding(intervals.float())
        inversion_emb = self.inversion_embedding(inversions.squeeze(-1))
        # 拼接并融合
        combined_emb = torch.cat(
            [duration_emb, root_pitch_emb, interval_emb, inversion_emb], dim=-1
        )
        fused_emb = self.fusion_layer(combined_emb)
        return fused_emb


class ChordPredictor(nn.Module):
    def __init__(
        self,
        embedding_dim,
        num_heads,
        num_layers,
    ):
        super().__init__()
        self.chord_embedding = ChordEmbedding(embedding_dim)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=embedding_dim, nhead=num_heads),
            num_layers=num_layers,
        )
        self.output_layer = nn.Linear(
            embedding_dim, embedding_dim
        )  # 可扩展到预测多字段

    def forward(self, durations, root_offsets, intervals, inversions):
        # 嵌入和弦
        chord_emb = self.chord_embedding(durations, root_offsets, intervals, inversions)
        # 使用Transformer建模
        transformer_output = self.transformer(chord_emb)
        # 预测下一个和弦
        prediction = self.output_layer(transformer_output)
        return prediction


# 模拟输入
durations = batch_data["durations"]
root_pitchs = batch_data["root_pitchs"]
intervals = batch_data["intervals"]
inversions = batch_data["inversions"]

# chordembedding = ChordEmbedding(embedding_dim)
# fused_emb = chordembedding.forward(durations,root_pitchs,intervals,inversions)

# print(fused_emb.shape)

# 初始化模型
model = ChordPredictor(embedding_dim, num_heads=4, num_layers=2)

# 前向传播
output = model(durations, root_pitchs, intervals, inversions)
print(output.shape)  # 输出形状为 (batch_size, block_size, embedding_dim)
