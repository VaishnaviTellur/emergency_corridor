import networkx as nx
import sumolib

from config import NETWORK_FILE, ROUTING_EDGES


def build_graph():

    if not NETWORK_FILE.exists():
        raise FileNotFoundError(
            "SUMO network not found. "
            "Run simulation.build_network first."
        )

    network = sumolib.net.readNet(
        str(NETWORK_FILE)
    )

    graph = nx.DiGraph()

    for edge_id in ROUTING_EDGES:

        edge = network.getEdge(edge_id)

        source_node = edge.getFromNode()
        target_node = edge.getToNode()

        source = source_node.getID()
        target = target_node.getID()

        length = float(edge.getLength())
        speed = float(edge.getSpeed())

        if length <= 0 or speed <= 0:
            raise ValueError(
                f"Invalid road properties: {edge_id}"
            )

        baseline_cost = length / speed

        graph.add_node(
            source,
            position=source_node.getCoord()
        )

        graph.add_node(
            target,
            position=target_node.getCoord()
        )

        if graph.has_edge(source, target):
            raise ValueError(
                "Parallel edges are not supported "
                "by this demonstration graph."
            )

        graph.add_edge(
            source,
            target,
            edge_id=edge_id,
            length=length,
            speed_limit=speed,
            baseline_cost=baseline_cost,
            dynamic_cost=baseline_cost,
            congestion="Unknown"
        )

    return graph


if __name__ == "__main__":

    graph = build_graph()

    print("Road graph created successfully")
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    for source, target, data in graph.edges(data=True):

        print(
            f"{source} -> {target} | "
            f"Edge: {data['edge_id']} | "
            f"Length: {data['length']:.2f} m | "
            f"Cost: {data['baseline_cost']:.2f} s"
        )