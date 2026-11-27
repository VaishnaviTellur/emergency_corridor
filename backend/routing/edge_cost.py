from config import CLASS_NAMES


CONGESTION_PENALTIES = {
    "Low": 1.0,
    "Medium": 1.5,
    "High": 3.0
}


def apply_dynamic_costs(graph, predictions):

    prediction_map = {}

    for prediction in predictions:

        edge_id = prediction["edge_id"]

        if edge_id in prediction_map:
            raise ValueError(
                f"Duplicate prediction: {edge_id}"
            )

        prediction_map[edge_id] = prediction

    for source, target, data in graph.edges(data=True):

        edge_id = data["edge_id"]

        if edge_id not in prediction_map:

            raise ValueError(
                f"Missing VQC prediction for {edge_id}"
            )

        prediction = prediction_map[edge_id]

        congestion = prediction["congestion"]

        if congestion not in CLASS_NAMES:

            raise ValueError(
                f"Invalid congestion class: {congestion}"
            )

        penalty = CONGESTION_PENALTIES[congestion]

        dynamic_cost = (
            data["baseline_cost"] * penalty
        )

        graph[source][target].update({
            "congestion": congestion,
            "confidence": prediction["confidence"],
            "penalty": penalty,
            "dynamic_cost": dynamic_cost
        })

    return graph