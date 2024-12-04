from src.prepare_data import get_batch_data
import torch
import torch.nn as nn
import torch.optim as optim
import src.model

batch_size = src.model.batch_size
block_size = src.model.block_size
embedding_dim = src.model.embedding_dim
batch_data = get_batch_data("test", batch_size, block_size)

