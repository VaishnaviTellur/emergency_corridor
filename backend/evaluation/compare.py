import argparse
import json

from config import (
    DATASET_DIR,
    RANDOM_SEED
)

from simulation.traffic_generator import SCENARIOS

from simulation.live_prediction import (
    predict_live_congestion
)

from routing.optimized_route import compare_routes

from evaluation.ambulance_runner import (
    measure_travel_time
)


COMPARISON_FILE = (
    DATASET_DIR / "comparison_results.json"
)


def run_comparison(
    scenario="mixed",
    seed=RANDOM_SEED,
    departure_time=240,
    gui=False,
    save=True
):

    print("\nSTEP 1: Predicting congestion")

    prediction_data = predict_live_congestion(
        scenario=scenario,
        gui=False,
        prediction_time=departure_time,
        seed=seed
    )

    print("\nSTEP 2: Calculating both routes")

    routing_result = compare_routes(
        prediction_data
    )

    baseline = routing_result["baseline"]
    enhanced = routing_result["enhanced"]

    print("\nSTEP 3: Evaluating conventional A*")

    baseline_measurement = measure_travel_time(
        edges=baseline["edges"],
        scenario=scenario,
        seed=seed,
        departure_time=departure_time,
        gui=gui
    )

    print("\nSTEP 4: Evaluating VQC-enhanced A*")

    enhanced_measurement = measure_travel_time(
        edges=enhanced["edges"],
        scenario=scenario,
        seed=seed,
        departure_time=departure_time,
        gui=gui
    )

    baseline_time = (
        baseline_measurement["travel_time"]
    )

    enhanced_time = (
        enhanced_measurement["travel_time"]
    )

    time_saved = None
    improvement = None

    if (
        baseline_time is not None
        and enhanced_time is not None
        and baseline_time > 0
    ):

        time_saved = round(
            baseline_time - enhanced_time,
            2
        )

        improvement = round(
            (time_saved / baseline_time) * 100,
            2
        )

    result = {
        **routing_result,

        "baseline": {
            **baseline,
            **baseline_measurement
        },

        "enhanced": {
            **enhanced,
            **enhanced_measurement
        },

        "comparison": {
            "time_saved_seconds": time_saved,
            "travel_time_improvement_percent":
                improvement,

            "distance_difference_m": round(
                enhanced["distance_m"]
                - baseline["distance_m"],
                2
            ),

            "high_congestion_edges_avoided": (
                baseline[
                    "predicted_congestion_counts"
                ]["High"]
                - enhanced[
                    "predicted_congestion_counts"
                ]["High"]
            )
        },

        "predictions":
            prediction_data["road_segments"]
    }

    if save:

        with open(
            COMPARISON_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                allow_nan=False
            )

    print("\nFINAL COMPARISON")

    print("Conventional A*:", baseline_time)
    print("VQC-enhanced A*:", enhanced_time)
    print("Time saved:", time_saved)
    print("Improvement (%):", improvement)

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS),
        default="mixed"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED
    )

    parser.add_argument(
        "--time",
        type=int,
        default=240
    )

    parser.add_argument(
        "--gui",
        action="store_true"
    )

    args = parser.parse_args()

    run_comparison(
        scenario=args.scenario,
        seed=args.seed,
        departure_time=args.time,
        gui=args.gui
    )