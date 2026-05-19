import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from config.load_config import load_config

cfg = load_config()

WINDOW = cfg["lstm"]["window_size"]
EPOCHS = cfg["lstm"]["epochs"]
LR = cfg["lstm"]["learning_rate"]
HIDDEN = cfg["lstm"]["hidden_size"]


class LSTMModel(nn.Module):
    def __init__(self, input_size=4, hidden_size=64):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True,
            dropout=0.2,
        )

        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def build_dataset(data, window):
    X = []
    y = []

    for i in range(len(data) - window):
        X.append(data[i:i + window])
        y.append(data[i + window][0])

    return np.array(X), np.array(y)


def main():
    df = pd.read_csv("metrics.csv")

    features = df[["cpu", "memory", "qps", "latency"]].values

    scaler = MinMaxScaler()
    features = scaler.fit_transform(features)

    X, y = build_dataset(features, WINDOW)

    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    model = LSTMModel(hidden_size=HIDDEN)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LR
    )

    criterion = nn.MSELoss()

    print("Training LSTM...")

    for epoch in range(EPOCHS):
        pred = model(X)

        loss = criterion(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print(
            f"Epoch {epoch+1}/{EPOCHS}, "
            f"Loss={loss.item():.6f}"
        )

    torch.save(model.state_dict(), "lstm_model.pt")
    print("Saved: lstm_model.pt")


if __name__ == "__main__":
    main()