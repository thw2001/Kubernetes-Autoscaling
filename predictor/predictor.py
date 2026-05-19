import torch
import numpy as np
from train_lstm import LSTMModel
from config.load_config import load_config


class MCPredictor:
    def __init__(self):
        cfg = load_config()

        self.samples = cfg[
            "lstm"
        ]["mc_dropout_samples"]

        self.model = LSTMModel()
        self.model.load_state_dict(
            torch.load("lstm_model.pt")
        )

    def predict(self, x):
        self.model.train()

        preds = []

        for _ in range(self.samples):
            with torch.no_grad():
                y = self.model(x)
                preds.append(y.item())

        mu = np.mean(preds)
        sigma = np.std(preds)

        return mu, sigma