import shutil
import subprocess

from config import (
    NODES_FILE,
    EDGES_FILE,
    NETWORK_FILE
)

def build_network():

    netconvert = shutil.which("netconvert")

    if netconvert is None:
        raise RuntimeError(
            "netconvert not found. Add SUMO bin to PATH."
        )

    command = [
        netconvert,
        "--node-files", str(NODES_FILE),
        "--edge-files", str(EDGES_FILE),
        "--output-file", str(NETWORK_FILE),
        "--no-turnarounds", "true"
    ]

    subprocess.run(command, check=True)

    print("\nSUMO network generated successfully.")
    print("Network file:", NETWORK_FILE)

    return NETWORK_FILE

if __name__ == "__main__":
    build_network()