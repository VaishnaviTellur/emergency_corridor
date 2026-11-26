import argparse
import tempfile

from pathlib import Path

import pandas as pd

from config import (
    DATASET_FILE,
    SUMO_DIR,
    CLASS_NAMES,
    SIMULATION_DURATION,
    WARMUP_STEPS,
    SAMPLE_INTERVAL
)

from simulation.sumo_runner import sumo_session

from simulation.traffic_generator import (
    generate_traffic,
    SCENARIOS
)

from simulation.feature_extraction import (
    load_network,
    extract_all_features,
    congestion_label
)

def collect_simulation(
    scenario,
    seed,
    network,
    route_file
):

    generate_traffic(
        scenario=scenario,
        output_file=route_file
    )

    records = []

    previous_snapshot = None

    run_id = f"{scenario}_{seed}"

    with sumo_session(
        gui=False,
        seed=seed,
        route_file=route_file
    ) as connection:

        for step in range(
            1,
            SIMULATION_DURATION + 1
        ):

            connection.simulationStep()

            if step < WARMUP_STEPS:
                continue

            if step % SAMPLE_INTERVAL != 0:
                continue

            features = extract_all_features(
                connection,
                network
            )

            current_snapshot = {
                row["edge_id"]: row
                for row in features
            }

            if previous_snapshot is not None:

                for edge_id, previous in (
                    previous_snapshot.items()
                ):

                    future = current_snapshot[edge_id]

                    label = congestion_label(
                        future["average_speed"],
                        future["free_flow_speed"]
                    )

                    record = {
                        "run_id": run_id,
                        "scenario": scenario,
                        "seed": seed,
                        "time": step - SAMPLE_INTERVAL,
                        "target_time": step,
                        **previous,
                        "future_average_speed":
                            future["average_speed"],
                        "label": label,
                        "congestion": CLASS_NAMES[label]
                    }

                    records.append(record)

            previous_snapshot = current_snapshot

    return records

def generate_dataset(runs_per_scenario=4):

    if runs_per_scenario < 3:
        raise ValueError(
            "Use at least 3 runs per scenario."
        )

    network = load_network()

    all_records = []

    total_runs = (
        len(SCENARIOS) * runs_per_scenario
    )

    completed = 0

    # Temporary route files prevent overwriting
    # the normal demonstration traffic file.
    with tempfile.TemporaryDirectory(
        dir=SUMO_DIR
    ) as temporary_directory:

        route_file = (
            Path(temporary_directory)
            / "training.rou.xml"
        )

        for scenario in SCENARIOS:

            for index in range(runs_per_scenario):

                seed = 100 + index

                records = collect_simulation(
                    scenario=scenario,
                    seed=seed,
                    network=network,
                    route_file=route_file
                )

                all_records.extend(records)

                completed += 1

                print(
                    f"[{completed}/{total_runs}] "
                    f"{scenario}, seed={seed}, "
                    f"rows={len(records)}"
                )

    dataset = pd.DataFrame(all_records)

    if dataset.empty:
        raise RuntimeError(
            "No traffic data was generated."
        )

    dataset.to_csv(
        DATASET_FILE,
        index=False
    )

    print("\nDataset generated successfully.")
    print("Dataset location:", DATASET_FILE)
    print("Total records:", len(dataset))

    print("\nClass distribution:")

    print(
        dataset["congestion"]
        .value_counts()
        .reindex(CLASS_NAMES, fill_value=0)
    )

    if dataset["label"].nunique() != 3:

        raise RuntimeError(
            "Dataset does not contain all three "
            "congestion classes. Inspect traffic "
            "conditions and adjust simulation demand "
            "or bottlenecks before training."
        )

    return dataset

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--runs",
        type=int,
        default=4
    )

    args = parser.parse_args()

    generate_dataset(
        runs_per_scenario=args.runs
    )