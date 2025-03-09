from src.prepare_data import get_batch_data
import torch
import torch.nn as nn
import torch.optim as optim
import src.model

batch_size = src.model.batch_size
block_size = src.model.block_size
embedding_dim = src.model.embedding_dim

# 初始化模型和优化器
chord_emd = src.model.ChordEmbedding(embedding_dim)
chord_model = src.model.ChordModel()
optimizer = optim.AdamW(chord_model.parameters(), lr=0.001)

# 训练循环
for epoch in range(100):
    xb, yb = get_batch_data("train", batch_size, block_size)
    x_emb = chord_emd(xb)
    y_emb = chord_emd(yb)
    
    optimizer.zero_grad()
    out, loss = chord_model(x_emb, y_emb)
    loss.backward()
    optimizer.step()
    
    print(f'Epoch {epoch+1}, Loss: {loss.item()}')

