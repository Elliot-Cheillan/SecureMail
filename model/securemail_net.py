import torch.nn as nn

# just the class, I defined it into the train.py at first, but finally it's not efficient cause it launch all the train.py
# for each imports.

# I built this model by looking a simple project of pytorch, and re used the program, changes the variables multiples times
# to get model that return a satisfying accuracy and added some Dropout cause I had some trouble with the training.


class SecureMailNet(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(1)
