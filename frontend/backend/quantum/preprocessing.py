import numpy as np
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import MinMaxScaler

from config import (
    DATASET_FILE,
    FEATURE_COLUMNS,
    RANDOM_SEED
)

def prepare_data():

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            "Generate the traffic dataset first."
        )

    df = pd.read_csv(DATASET_FILE)

    required_columns = (
        FEATURE_COLUMNS
        + ["label", "run_id"]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    df = df.dropna(
        subset=required_columns
    ).reset_index(drop=True)

    X = df[FEATURE_COLUMNS].to_numpy(
        dtype=np.float32
    )

    y = df["label"].to_numpy(
        dtype=np.int64
    )

    groups = df["run_id"].to_numpy()

    if not np.isfinite(X).all():

        raise ValueError(
            "Dataset contains non-finite values."
        )

    if set(np.unique(y)) != {0, 1, 2}:

        raise ValueError(
            "All three congestion classes are required."
        )

    # Approximately 20% of simulation runs
    # are reserved for final testing.
    outer_split = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=RANDOM_SEED
    )

    train_val_idx, test_idx = next(
        outer_split.split(X, y, groups)
    )

    # Split remaining runs into training
    # and validation.
    inner_split = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=RANDOM_SEED
    )

    train_local, val_local = next(
        inner_split.split(
            X[train_val_idx],
            y[train_val_idx],
            groups[train_val_idx]
        )
    )

    train_idx = train_val_idx[train_local]
    val_idx = train_val_idx[val_local]

    for name, indices in [
        ("Training", train_idx),
        ("Validation", val_idx),
        ("Testing", test_idx)
    ]:

        if set(np.unique(y[indices])) != {0, 1, 2}:

            raise ValueError(
                f"{name} split is missing a class. "
                "Generate more diverse simulation runs."
            )

    scaler = MinMaxScaler(
        feature_range=(0, np.pi),
        clip=True
    )

    X_train = scaler.fit_transform(
        X[train_idx]
    )

    X_val = scaler.transform(
        X[val_idx]
    )

    X_test = scaler.transform(
        X[test_idx]
    )

    print("Training samples:", len(train_idx))
    print("Validation samples:", len(val_idx))
    print("Testing samples:", len(test_idx))

    return {
        "X_train": X_train.astype(np.float32),
        "y_train": y[train_idx],
        "X_val": X_val.astype(np.float32),
        "y_val": y[val_idx],
        "X_test": X_test.astype(np.float32),
        "y_test": y[test_idx],
        "test_indices": test_idx,
        "scaler": scaler
    }

if __name__ == "__main__":

    data = prepare_data()

    print("\nPreprocessing successful.")

    print(
        "Training feature shape:",
        data["X_train"].shape
    )