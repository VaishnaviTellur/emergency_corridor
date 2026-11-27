import networkx as nx

graph = nx.DiGraph()

graph.add_weighted_edges_from([
    ("A", "B", 10),
    ("B", "D", 10),
    ("A", "C", 15),
    ("C", "D", 15)
])

route = nx.astar_path(
    graph,
    source="A",
    target="D",
    weight="weight"
)

cost = nx.astar_path_length(
    graph,
    source="A",
    target="D",
    weight="weight"
)

print("NetworkX is working successfully")
print("Selected route:", route)
print("Total route cost:", cost)