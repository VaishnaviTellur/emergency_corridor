from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SUMO_DIR = BASE_DIR / "sumo"
DATASET_DIR = BASE_DIR / "datasets"
MODEL_DIR = BASE_DIR / "models"

NETWORK_FILE = SUMO_DIR / "network.net.xml"
NODES_FILE = SUMO_DIR / "nodes.nod.xml"
EDGES_FILE = SUMO_DIR / "edges.edg.xml"
ROUTES_FILE = SUMO_DIR / "traffic.rou.xml"
SUMO_CONFIG = SUMO_DIR / "simulation.sumocfg"

DATASET_FILE = DATASET_DIR / "traffic_data.csv"

MODEL_FILE = MODEL_DIR / "vqc_model.pt"
SCALER_FILE = MODEL_DIR / "scaler.joblib"
METRICS_FILE = MODEL_DIR / "metrics.json"

FEATURE_COLUMNS = [
    "density",
    "average_speed",
    "queue_length",
    "occupancy"
]

CLASS_NAMES = ["Low", "Medium", "High"]

N_QUBITS = 4
N_LAYERS = 2
RANDOM_SEED = 42

SIMULATION_DURATION = 600
WARMUP_STEPS = 120
SAMPLE_INTERVAL = 15

ROUTING_EDGES = [
    "SA", "AB", "BH",
    "SC", "CD", "DH",
    "SE", "EF", "FH"
]

for directory in [SUMO_DIR, DATASET_DIR, MODEL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)