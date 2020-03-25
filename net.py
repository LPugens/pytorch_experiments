import torch
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.batch_norm1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 32, 3, 1)
        self.batch_norm2 = nn.BatchNorm2d(32)
        self.dropout1 = nn.Dropout2d(0.25)
        self.conv3 = nn.Conv2d(32, 32, 3, 1)
        self.batch_norm3 = nn.BatchNorm2d(32)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(209280, 16)
        self.batch_norm4 = nn.BatchNorm1d(16)
        self.fc2 = nn.Linear(16, 2) 
        self.batch_norm5 = nn.BatchNorm1d(2)

    def forward(self, x):
        x = self.conv1(x)
        x = self.batch_norm1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = self.batch_norm2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = self.conv3(x)
        x = self.batch_norm3(x)
        x = F.relu(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = self.batch_norm4(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        x = self.batch_norm5(x)
        output = F.log_softmax(x, dim=1)
        return output
