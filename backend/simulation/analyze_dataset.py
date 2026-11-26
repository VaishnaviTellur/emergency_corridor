import pandas as pd
import matplotlib.pyplot as plt

from config import (
    DATASET_FILE,
    DATASET_DIR,
    FEATURE_COLUMNS,
    CLASS_NAMES
)

def analyze_dataset():

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            "Generate the traffic dataset first."
        )

    df = pd.read_csv(DATASET_FILE)

    print("\nDATASET SHAPE")
    print(df.shape)

    print("\nFIRST FIVE RECORDS")
    print(df.head())

    print("\nMISSING VALUES")
    print(
        df[FEATURE_COLUMNS + ["label"]]
        .isnull()
        .sum()
    )

    print("\nFEATURE STATISTICS")
    print(df[FEATURE_COLUMNS].describe())

    counts = (
        df["congestion"]
        .value_counts()
        .reindex(CLASS_NAMES, fill_value=0)
    )

    print("\nCONGESTION DISTRIBUTION")
    print(counts)

    print("\nSCENARIO DISTRIBUTION")
    print(
        pd.crosstab(
            df["scenario"],
            df["congestion"]
        )
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        counts.index,
        counts.values,
        color=["green", "orange", "red"]
    )

    plt.title("Traffic Congestion Distribution")
    plt.xlabel("Congestion Class")
    plt.ylabel("Number of Samples")
    plt.tight_layout()

    output_file = (
        DATASET_DIR
        / "congestion_distribution.png"
    )

    plt.savefig(output_file, dpi=150)

    print("\nGraph saved:", output_file)

    plt.show()

if __name__ == "__main__":
    analyze_dataset()