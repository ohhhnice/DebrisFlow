import math
import torch
from torch import nn


class SelfAttention(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        self.q_proj = nn.Linear(emb_dim, emb_dim)
        self.k_proj = nn.Linear(emb_dim, emb_dim)
        self.v_proj = nn.Linear(emb_dim, emb_dim)

    def forward(self, X):
        # X （batch_size, seq_len, emb_dim)
        q = self.q_proj(X)
        k = self.k_proj(X)
        v = self.v_proj(X)
        weight = torch.matmul(q, k.transpose(1, 2))
        weight = torch.softmax(weight, dim=-1)
        return torch.matmul(weight, v)


X = torch.ones(2, 3, 4)
attn = SelfAttention(4)
res = attn(X)
print(res)
 