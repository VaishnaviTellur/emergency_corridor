import math
import json

import networkx as nx

from routing.graph_builder import build_graph


def create_heuristic(graph, weight):

    ratios = []

    for source, target, data in graph.edges(data=True):

        source_position = graph.nodes[source]["position"]
        target_position = graph.nodes[target]["position"]

        distance = math.dist(
            source_position,
            target_position
        )

        if distance > 0:

            ratios.append(
                data[weight] / distance
            )

    scale = min(ratios, default=0.0)

    def heuristic(node, target):

        return scale * math.dist(
            graph.nodes[node]["position"],
            graph.nodes[target]["position"]
        )

    return heuristic


def calculate_route(
    graph,
    source="S",
    destination="H",
    weight="baseline_cost"
):

    if source not in graph:
        raise ValueError("Invalid source node.")

    if destination not in graph:
        raise ValueError("Invalid destination node.")

    heuristic = create_heuristic(
        graph,
        weight
    )

    path = nx.astar_path(
        graph,
        source=source,
        target=destination,
        heuristic=heuristic,
        weight=weight
    )

    edge_ids = []
    total_distance = 0.0
    total_cost = 0.0
    free_flow_time = 0.0

    for start, end in zip(path[:-1], path[1:]):

        edge = graph[start][end]

        edge_ids.append(edge["edge_id"])

        total_distance += edge["length"]
        total_cost += edge[weight]
        free_flow_time += edge["baseline_cost"]

    return {
        "path": path,
        "edges": edge_ids,
        "distance_m": round(total_distance, 2),
        "route_cost": round(total_cost, 2),
        "free_flow_time": round(free_flow_time, 2),
        "cost_type": weight
    }


def conventional_astar(
    source="S",
    destination="H"
):

    graph = build_graph()

    return calculate_route(
        graph,
        source,
        destination,
        weight="baseline_cost"
    )


if __name__ == "__main__":

    result = conventional_astar()

    print("\nCONVENTIONAL A* RESULT")

    print(
        json.dumps(result, indent=4)
    )