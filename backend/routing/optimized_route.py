import argparse
import json

from config import DATASET_DIR

from routing.graph_builder import build_graph
from routing.edge_cost import apply_dynamic_costs
from routing.astar import calculate_route


PREDICTION_FILE = (
    DATASET_DIR / "live_predictions.json"
)

RESULT_FILE = (
    DATASET_DIR / "routing_results.json"
)


def route_statistics(graph, route):

    counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0
    }

    dynamic_cost = 0.0

    for source, target in zip(
        route["path"][:-1],
        route["path"][1:]
    ):

        edge = graph[source][target]

        counts[edge["congestion"]] += 1

        dynamic_cost += edge["dynamic_cost"]

    return {
        **route,
        "predicted_congestion_counts": counts,
        "congestion_aware_cost": round(
            dynamic_cost, 2
        )
    }


def compare_routes(prediction_data):

    graph = build_graph()

    baseline = calculate_route(
        graph,
        source="S",
        destination="H",
        weight="baseline_cost"
    )

    graph = apply_dynamic_costs(
        graph,
        prediction_data["road_segments"]
    )

    enhanced = calculate_route(
        graph,
        source="S",
        destination="H",
        weight="dynamic_cost"
    )

    baseline = route_statistics(
        graph,
        baseline
    )

    enhanced = route_statistics(
        graph,
        enhanced
    )

    roads = []

    for source, target, data in graph.edges(data=True):

        roads.append({
            "source": source,
            "target": target,
            **data
        })

    nodes = [
        {
            "id": node,
            "x": float(data["position"][0]),
            "y": float(data["position"][1])
        }
        for node, data in graph.nodes(data=True)
    ]

    result = {
        "scenario": prediction_data["scenario"],
        "seed": prediction_data["seed"],
        "simulation_time":
            prediction_data["simulation_time"],
        "baseline": baseline,
        "enhanced": enhanced,
        "route_changed":
            baseline["edges"] != enhanced["edges"],
        "nodes": nodes,
        "roads": roads
    }

    return result


def run_optimization():

    if not PREDICTION_FILE.exists():

        raise FileNotFoundError(
            "Run simulation.live_prediction first."
        )

    with open(
        PREDICTION_FILE,
        encoding="utf-8"
    ) as file:

        prediction_data = json.load(file)

    result = compare_routes(
        prediction_data
    )

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(result, file, indent=4)

    print("\nCONVENTIONAL A*")

    print(
        json.dumps(
            result["baseline"],
            indent=4
        )
    )

    print("\nVQC-ENHANCED A*")

    print(
        json.dumps(
            result["enhanced"],
            indent=4
        )
    )

    print(
        "\nRoute changed:",
        result["route_changed"]
    )

    print("Results saved:", RESULT_FILE)

    return result


if __name__ == "__main__":
    run_optimization()