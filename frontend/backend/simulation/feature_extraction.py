import sumolib

from config import NETWORK_FILE, ROUTING_EDGES

def load_network():

    return sumolib.net.readNet(
        str(NETWORK_FILE)
    )

def extract_edge_features(
    connection,
    network,
    edge_id
):

    edge = network.getEdge(edge_id)

    lane_ids = [
        lane.getID()
        for lane in edge.getLanes()
    ]

    lane_count = len(lane_ids)

    length_m = edge.getLength()

    free_flow_speed = edge.getSpeed()

    vehicle_count = (
        connection.edge.getLastStepVehicleNumber(
            edge_id
        )
    )

    average_speed = (
        connection.edge.getLastStepMeanSpeed(
            edge_id
        )
    )

    queue_length = (
        connection.edge.getLastStepHaltingNumber(
            edge_id
        )
    )

    lane_occupancies = [
        connection.lane.getLastStepOccupancy(
            lane_id
        )
        for lane_id in lane_ids
    ]

    occupancy = (
        sum(lane_occupancies) / lane_count
    )

    density = vehicle_count / (
        (length_m / 1000) * lane_count
    )

    # Empty roads are treated as free-flow roads.
    if vehicle_count == 0 or average_speed < 0:
        average_speed = free_flow_speed

    return {
        "edge_id": edge_id,
        "density": float(density),
        "average_speed": float(average_speed),
        "queue_length": int(queue_length),
        "occupancy": float(occupancy),
        "vehicle_count": int(vehicle_count),
        "free_flow_speed": float(free_flow_speed),
        "length_m": float(length_m)
    }

def extract_all_features(
    connection,
    network
):

    return [
        extract_edge_features(
            connection,
            network,
            edge_id
        )
        for edge_id in ROUTING_EDGES
    ]

def congestion_label(
    average_speed,
    free_flow_speed
):

    ratio = average_speed / max(
        free_flow_speed, 0.001
    )

    if ratio >= 0.75:
        return 0

    elif ratio >= 0.40:
        return 1

    return 2