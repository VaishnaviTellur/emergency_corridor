import argparse

import pandas as pd

from config import DATASET_DIR

from simulation.traffic_generator import SCENARIOS

from evaluation.compare import run_comparison


def batch_evaluation(runs=5):

    records = []

    for scenario in SCENARIOS:

        for index in range(runs):

            seed = 1000 + index

            print(
                f"\nEvaluating {scenario}, "
                f"seed={seed}"
            )

            result = run_comparison(
                scenario=scenario,
                seed=seed,
                departure_time=240,
                gui=False,
                save=False
            )

            baseline = result["baseline"]
            enhanced = result["enhanced"]
            comparison = result["comparison"]

            records.append({
                "scenario": scenario,
                "seed": seed,

                "baseline_route":
                    " -> ".join(baseline["path"]),

                "enhanced_route":
                    " -> ".join(enhanced["path"]),

                "baseline_completed":
                    baseline["completed"],

                "enhanced_completed":
                    enhanced["completed"],

                "baseline_time":
                    baseline["travel_time"],

                "enhanced_time":
                    enhanced["travel_time"],

                "baseline_distance":
                    baseline["distance_m"],

                "enhanced_distance":
                    enhanced["distance_m"],

                "route_changed":
                    result["route_changed"],

                "time_saved":
                    comparison["time_saved_seconds"],

                "improvement_percent":
                    comparison[
                        "travel_time_improvement_percent"
                    ]
            })

    df = pd.DataFrame(records)

    output_file = (
        DATASET_DIR / "research_results.csv"
    )

    df.to_csv(output_file, index=False)

    completed_pairs = df.dropna(
        subset=[
            "baseline_time",
            "enhanced_time"
        ]
    )

    print("\nRESEARCH SUMMARY")

    print("Total experiments:", len(df))

    print(
        "Completed paired experiments:",
        len(completed_pairs)
    )

    print(
        "Baseline completion rate:",
        df["baseline_completed"].mean()
    )

    print(
        "Enhanced completion rate:",
        df["enhanced_completed"].mean()
    )

    if not completed_pairs.empty:

        print(
            "Mean baseline travel time:",
            completed_pairs["baseline_time"].mean()
        )

        print(
            "Mean enhanced travel time:",
            completed_pairs["enhanced_time"].mean()
        )

        print(
            "Mean paired improvement (%):",
            completed_pairs[
                "improvement_percent"
            ].mean()
        )

        print("\nScenario-wise comparison:")

        print(
            completed_pairs.groupby("scenario")[
                [
                    "baseline_time",
                    "enhanced_time",
                    "improvement_percent"
                ]
            ].mean()
        )

    print("\nResults saved:", output_file)

    return df


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--runs",
        type=int,
        default=5
    )

    args = parser.parse_args()

    if args.runs < 1:
        parser.error("Runs must be positive.")

    batch_evaluation(args.runs)