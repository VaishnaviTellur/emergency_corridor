import argparse
import copy
import hashlib
import json
import random

import joblib
import numpy as np
import torch

from torch import nn
from torch.utils.data import (
    TensorDataset,
    DataLoader
)

from sklearn.metrics import f1_score

from config import (
    DATASET_FILE,
    MODEL_DIR,
    MODEL_FILE,
    SCALER_FILE,
    FEATURE_COLUMNS,
    CLASS_NAMES,
    RANDOM_SEED
)

from quantum.vqc_model import VQCModel

from quantum.preprocessing import prepare_data

def set_seed(seed):

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

def train_model(
    epochs=20,
    batch_size=64,
    learning_rate=0.01
):

    set_seed(RANDOM_SEED)

    data = prepare_data()

    X_train = torch.tensor(
        data["X_train"],
        dtype=torch.float32
    )

    y_train = torch.tensor(
        data["y_train"],
        dtype=torch.long
    )

    X_val = torch.tensor(
        data["X_val"],
        dtype=torch.float32
    )

    y_val = torch.tensor(
        data["y_val"],
        dtype=torch.long
    )

    train_dataset = TensorDataset(
        X_train,
        y_train
    )

    generator = torch.Generator()

    generator.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator
    )

    val_loader = DataLoader(
        TensorDataset(X_val, y_val),
        batch_size=batch_size,
        shuffle=False
    )

    model = VQCModel()

    # Balance the contribution of each class.
    class_counts = np.bincount(
        data["y_train"],
        minlength=3
    )

    class_weights = (
        len(data["y_train"])
        / (3 * class_counts)
    )

    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(
            class_weights,
            dtype=torch.float32
        )
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate
    )

    best_f1 = -1.0
    best_state = None
    best_epoch = 0

    history = []

    patience = 5
    stale_epochs = 0

    for epoch in range(epochs):

        model.train()

        total_loss = 0.0
        correct = 0
        total = 0

        for features, labels in train_loader:

            optimizer.zero_grad()

            logits = model(features)

            loss = criterion(
                logits,
                labels
            )

            loss.backward()

            optimizer.step()

            total_loss += (
                loss.item() * labels.size(0)
            )

            predictions = logits.argmax(dim=1)

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

        train_loss = total_loss / total

        train_accuracy = correct / total

        model.eval()

        val_predictions = []
        val_targets = []

        with torch.no_grad():

            for features, labels in val_loader:

                logits = model(features)

                predictions = logits.argmax(dim=1)

                val_predictions.extend(
                    predictions.tolist()
                )

                val_targets.extend(
                    labels.tolist()
                )

        val_f1 = f1_score(
            val_targets,
            val_predictions,
            average="macro",
            zero_division=0
        )

        history.append({
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "validation_f1": float(val_f1)
        })

        print(
            f"Epoch {epoch + 1:02d}/{epochs} | "
            f"Loss: {train_loss:.4f} | "
            f"Train Accuracy: {train_accuracy:.4f} | "
            f"Validation F1: {val_f1:.4f}"
        )

        if val_f1 > best_f1 + 1e-5:

            best_f1 = val_f1

            best_state = copy.deepcopy(
                model.state_dict()
            )

            best_epoch = epoch + 1

            stale_epochs = 0

        else:

            stale_epochs += 1

        if stale_epochs >= patience:

            print("Early stopping activated.")
            break

    model.load_state_dict(best_state)

    dataset_hash = hashlib.sha256(
        DATASET_FILE.read_bytes()
    ).hexdigest()

    torch.save(
        {
            "model_state": model.state_dict(),
            "feature_columns": FEATURE_COLUMNS,
            "class_names": CLASS_NAMES,
            "best_epoch": best_epoch,
            "dataset_hash": dataset_hash
        },
        MODEL_FILE
    )

    joblib.dump(
        data["scaler"],
        SCALER_FILE
    )

    np.save(
        MODEL_DIR / "test_indices.npy",
        data["test_indices"]
    )

    with open(
        MODEL_DIR / "training_history.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4
        )

    print("\nVQC training completed.")

    print("Best epoch:", best_epoch)
    print("Best validation F1:", best_f1)

    print("Model saved:", MODEL_FILE)
    print("Scaler saved:", SCALER_FILE)

    return model

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--epochs",
        type=int,
        default=20
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=64
    )

    args = parser.parse_args()

    if args.epochs < 1 or args.batch_size < 1:

        parser.error(
            "Epochs and batch size must be positive."
        )

    train_model(
        epochs=args.epochs,
        batch_size=args.batch_size
    )