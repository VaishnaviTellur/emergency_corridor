import argparse
import json
import tempfile

from pathlib import Path

from config import (
    SUMO_DIR,
    DATASET_DIR,
    SIMULATION_DURATION,
    RANDOM_SEED,
    WARMUP_STEPS,
    SAMPLE_INTERVAL,
    CLASS_NAMES
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

from quantum.predict import CongestionPredictor

def predict_live_congestion(
    scenario="mixed",
    gui=False,
    prediction_time=240,
    seed=RANDOM_SEED
):

    if prediction_time < WARMUP_STEPS:

        raise ValueError(
            "Prediction time must be after warmup."
        )

    target_time = (
        prediction_time + SAMPLE_INTERVAL
    )

    if target_time > SIMULATION_DURATION:

        raise ValueError(
            "Prediction horizon exceeds simulation duration."
        )

    predictor = CongestionPredictor()

    network = load_network()

    with tempfile.TemporaryDirectory(
        dir=SUMO_DIR
    ) as temporary_directory:

        route_file = (
            Path(temporary_directory)
            / "prediction.rou.xml"
        )

        generate_traffic(
            scenario=scenario,
            output_file=route_file
        )

        with sumo_session(
            gui=gui,
            seed=seed,
            route_file=route_file
        ) as connection:

            # Run SUMO until the observation time.
            for _ in range(prediction_time):

                connection.simulationStep()

            # Extract actual SUMO traffic features.
            features = extract_all_features(
                connection,
                network
            )

            # Perform actual VQC inference.
            predictions = predictor.predict_many(
                features
            )

            # Advance SUMO to obtain future ground truth.
            for _ in range(SAMPLE_INTERVAL):

                connection.simulationStep()

            future_features = extract_all_features(
                connection,
                network
            )

    future_by_edge = {
        record["edge_id"]: record
        for record in future_features
    }

    results = []

    for feature, prediction in zip(
        features,
        predictions
    ):

        future = future_by_edge[
            feature["edge_id"]
        ]

        actual_class = congestion_label(
            future["average_speed"],
            future["free_flow_speed"]
        )

        results.append({
            **feature,
            **prediction,
            "actual_class_id": actual_class,
            "actual_congestion":
                CLASS_NAMES[actual_class]
        })

    output = {
        "scenario": scenario,
        "seed": seed,
        "simulation_time": prediction_time,
        "target_time": target_time,
        "road_segments": results
    }

    output_file = (
        DATASET_DIR
        / "live_predictions.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )

    print("\nLIVE VQC CONGESTION PREDICTION")

    print(
        f"{'Edge':<8}"
        f"{'Density':<12}"
        f"{'Speed':<12}"
        f"{'Predicted':<12}"
        f"{'Actual':<12}"
        f"{'Confidence':<12}"
    )

    print("-" * 68)

    for result in results:

        print(
            f"{result['edge_id']:<8}"
            f"{result['density']:<12.2f}"
            f"{result['average_speed']:<12.2f}"
            f"{result['congestion']:<12}"
            f"{result['actual_congestion']:<12}"
            f"{result['confidence']:<12.2%}"
        )

    correct = sum(
        row["class_id"] == row["actual_class_id"]
        for row in results
    )

    print(
        f"\nSnapshot accuracy: "
        f"{correct}/{len(results)}"
    )

    print("Results saved:", output_file)

    return output

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS),
        default="mixed"
    )

    parser.add_argument(
        "--gui",
        action="store_true"
    )

    parser.add_argument(
        "--time",
        type=int,
        default=240
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED
    )

    args = parser.parse_args()

    predict_live_congestion(
        scenario=args.scenario,
        gui=args.gui,
        prediction_time=args.time,
        seed=args.seed
    )