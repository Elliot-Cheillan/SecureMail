import torch.nn as nn


class ShapWrapper(nn.Module):
    # Wraps the model to restore the output dim SHAP expects (batch, 1) instead of (batch,)
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        return self.model(x).unsqueeze(1)
