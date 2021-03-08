import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class MyConv1dPadSame(nn.Module):
    """
    extend nn.Conv1d to support SAME padding
    """

    def __init__(self, in_channels, out_channels, kernel_size, stride):
        super(MyConv1dPadSame, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.conv = torch.nn.Conv1d(
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            kernel_size=self.kernel_size,
            stride=self.stride)

    def forward(self, x):
        net = x

        # compute pad shape
        in_dim = net.shape[-1]
        out_dim = (in_dim + self.stride - 1) // self.stride
        p = max(0, (out_dim - 1) * self.stride + self.kernel_size - in_dim)
        pad_left = p // 2
        pad_right = p - pad_left
        net = F.pad(net, (pad_left, pad_right), "constant", 0)

        net = self.conv(net)

        return net


class MyMaxPool1dPadSame(nn.Module):
    """
    extend nn.MaxPool1d to support SAME padding
    """

    def __init__(self, kernel_size, stride_size):
        super(MyMaxPool1dPadSame, self).__init__()
        self.kernel_size = kernel_size
        self.stride = stride_size
        self.max_pool = torch.nn.MaxPool1d(kernel_size=self.kernel_size)

    def forward(self, x):
        net = x

        # compute pad shape
        in_dim = net.shape[-1]
        out_dim = (in_dim + self.stride - 1) // self.stride
        p = max(0, (out_dim - 1) * self.stride + self.kernel_size - in_dim)
        pad_left = p // 2
        pad_right = p - pad_left
        net = F.pad(net, (pad_left, pad_right), "constant", 0)

        net = self.max_pool(net)

        return net


# Convolutional neural network (two convolutional layers)
class DF(nn.Module):
    def __init__(self, length, num_classes=100):
        super(DF, self).__init__()
        self.length = length
        self.num_classes = num_classes
        self.layer1 = nn.Sequential(
            # nn.Conv1d(1, 32, kernel_size=9, stride=1, padding=4),
            MyConv1dPadSame(1, 32, 8, 1),
            nn.BatchNorm1d(32),
            nn.ELU(),
            # nn.Conv1d(32, 32, kernel_size=9, stride=1, padding=4),
            MyConv1dPadSame(32, 32, 8, 1),
            nn.BatchNorm1d(32),
            nn.ELU(),
            # nn.MaxPool1d(kernel_size=4, stride=4),
            MyMaxPool1dPadSame(8, 1),
            nn.Dropout(0.1)
        )
        self.layer2 = nn.Sequential(
            # nn.Conv1d(32, 64, kernel_size=9, stride=1, padding=4),
            MyConv1dPadSame(32, 64, 8, 1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            # nn.Conv1d(64, 64, kernel_size=9, stride=1, padding=4),
            MyConv1dPadSame(64, 64, 8, 1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            # nn.MaxPool1d(kernel_size=4, stride=4),
            MyMaxPool1dPadSame(8, 1),
            nn.Dropout(0.1)
        )
        self.layer3 = nn.Sequential(
            # nn.Conv1d(64, 128, kernel_size=9, stride=1, padding=4),
            MyConv1dPadSame(64, 128, 8, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            # nn.Conv1d(128, 128, kernel_size=9, stride=1, padding=4),
            MyConv1dPadSame(128, 128, 8, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            # nn.MaxPool1d(kernel_size=4, stride=4),
            MyMaxPool1dPadSame(8, 1),
            nn.Dropout(0.1)
        )
        self.layer4 = nn.Sequential(
            MyConv1dPadSame(128, 256, 8, 1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            MyMaxPool1dPadSame(8, 1),
            nn.Dropout(0.1)
        )
        self.layer5 = nn.Sequential(
            nn.Linear(256 * self.linear_input(), 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.7),
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.5)
        )
        self.fc = nn.Linear(512, self.num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = out.reshape(out.size(0), -1)
        out = self.layer5(out)
        out = self.fc(out)
        return out

    def linear_input(self):
        res = self.length
        for i in range(4):
            res = int(np.ceil(res / 8))
        return res
