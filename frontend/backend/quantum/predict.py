import argparse

import joblib
import numpy as np
import torch

from config import (
    MODEL_FILE,
    SCALER_FILE,
    FEATURE_COLUMNS,
    CLASS_NAMES
)

from quantum.vqc_model import VQCModel

class CongestionPredictor:

    def __init__(self):

        if not MODEL_FILE.exists():

            raise FileNotFoundError(
                "VQC model not found. "
                "Run python -m quantum.train first."
            )

        if not SCALER_FILE.exists():

            raise FileNotFoundError(
                "Preprocessing scaler not found."
            )

        self.scaler = joblib.load(
            SCALER_FILE
        )

        checkpoint = torch.load(
            MODEL_FILE,
            map_location="cpu",
            weights_only=True
        )

        if (
            checkpoint["feature_columns"]
            != FEATURE_COLUMNS
        ):

            raise ValueError(
                "Model feature configuration mismatch."
            )

        if checkpoint["class_names"] != CLASS_NAMES:

            raise ValueError(
                "Model class configuration mismatch."
            )

        self.model = VQCModel()

        self.model.load_state_dict(
            checkpoint["model_state"]
        )

        self.model.eval()

    def predict_many(self, records):

        if not records:
            return []

        features = np.asarray(
            [
                [
                    record[column]
                    for column in FEATURE_COLUMNS
                ]
                for record in records
            ],
            dtype=np.float32
        )

        if not np.isfinite(features).all():

            raise ValueError(
                "Traffic features must be finite."
            )

        if (features < 0).any():

            raise ValueError(
                "Traffic features cannot be negative."
            )

        if (features[:, 3] > 100).any():

            raise ValueError(
                "Occupancy must be between 0 and 100."
            )

        scaled = self.scaler.transform(
            features
        )

        tensor = torch.tensor(
            scaled,
            dtype=torch.float32
        )

        with torch.no_grad():

            logits = self.model(tensor)

            probabilities = torch.softmax(
                logits,
                dim=1
            )

        results = []

        for record, probs in zip(
            records,
            probabilities
        ):

            class_id = int(
                probs.argmax().item()
            )

            result = {
                "edge_id": record.get("edge_id"),
                "class_id": class_id,
                "congestion": CLASS_NAMES[class_id],
                "confidence": float(
                    probs[class_id].item()
                ),
                "probabilities": {
                    name: float(probs[index].item())
                    for index, name
                    in enumerate(CLASS_NAMES)
                }
            }

            results.append(result)

        return results

    def predict(self, record):

        return self.predict_many(
            [record]
        )[0]

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--density",
        type=float,
        default=80.0
    )

    parser.add_argument(
        "--speed",
        type=float,
        default=3.0
    )

    parser.add_argument(
        "--queue",
        type=float,
        default=12.0
    )

    parser.add_argument(
        "--occupancy",
        type=float,
        default=65.0
    )

    args = parser.parse_args()

    predictor = CongestionPredictor()

    sample = {
        "edge_id": "test_edge",
        "density": args.density,
        "average_speed": args.speed,
        "queue_length": args.queue,
        "occupancy": args.occupancy
    }

    result = predictor.predict(sample)

    print("\nINPUT TRAFFIC FEATURES")

    print(sample)

    print("\nVQC PREDICTION")

    print(result)