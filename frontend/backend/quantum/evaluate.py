import hashlib
import json

import joblib
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from config import (
    DATASET_FILE,
    MODEL_DIR,
    MODEL_FILE,
    SCALER_FILE,
    METRICS_FILE,
    FEATURE_COLUMNS,
    CLASS_NAMES
)

from quantum.vqc_model import VQCModel

def evaluate_model():

    checkpoint = torch.load(
        MODEL_FILE,
        map_location="cpu",
        weights_only=True
    )

    current_hash = hashlib.sha256(
        DATASET_FILE.read_bytes()
    ).hexdigest()

    if current_hash != checkpoint["dataset_hash"]:

        raise RuntimeError(
            "Dataset changed after training. "
            "Train the model again before evaluation."
        )

    model = VQCModel()

    model.load_state_dict(
        checkpoint["model_state"]
    )

    model.eval()

    scaler = joblib.load(SCALER_FILE)

    df = pd.read_csv(DATASET_FILE)

    df = df.dropna(
        subset=FEATURE_COLUMNS + [
            "label",
            "run_id"
        ]
    ).reset_index(drop=True)

    test_indices = np.load(
        MODEL_DIR / "test_indices.npy"
    )

    test_df = df.iloc[test_indices]

    X_test = test_df[
        FEATURE_COLUMNS
    ].to_numpy(dtype=np.float32)

    y_test = test_df[
        "label"
    ].to_numpy(dtype=np.int64)

    X_test = scaler.transform(X_test)

    features = torch.tensor(
        X_test,
        dtype=torch.float32
    )

    predictions = []

    with torch.no_grad():

        for batch in features.split(64):

            logits = model(batch)

            predictions.extend(
                logits.argmax(dim=1).tolist()
            )

    predictions = np.asarray(predictions)

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1, 2]
    )

    metrics = {
        "accuracy": float(
            accuracy_score(
                y_test,
                predictions
            )
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0
            )
        ),
        "f1_score": float(
            f1_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0
            )
        ),
        "test_samples": int(len(y_test)),
        "confusion_matrix": matrix.tolist(),
        "class_names": CLASS_NAMES
    }

    print("\nVQC EVALUATION RESULTS")

    for key in [
        "accuracy",
        "precision",
        "recall",
        "f1_score"
    ]:

        print(
            f"{key}: {metrics[key]:.4f}"
        )

    print("\nCLASSIFICATION REPORT")

    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2],
            target_names=CLASS_NAMES,
            zero_division=0
        )
    )

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=CLASS_NAMES
    )

    display.plot(cmap="Blues")

    plt.title("VQC Confusion Matrix")
    plt.tight_layout()

    plt.savefig(
        MODEL_DIR / "confusion_matrix.png",
        dpi=150
    )

    print("\nMetrics saved:", METRICS_FILE)

    plt.show()

    return metrics

if __name__ == "__main__":
    evaluate_model()