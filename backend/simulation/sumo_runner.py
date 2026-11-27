import argparse
import shutil

from contextlib import contextmanager

import traci

from config import (
    NETWORK_FILE,
    SUMO_CONFIG,
    SIMULATION_DURATION,
    RANDOM_SEED
)

from simulation.traffic_generator import (
    generate_traffic,
    SCENARIOS
)

@contextmanager
def sumo_session(
    gui=False,
    seed=RANDOM_SEED,
    route_file=None
):

    executable = "sumo-gui" if gui else "sumo"

    binary = shutil.which(executable)

    if binary is None:
        raise RuntimeError(
            f"{executable} not found in PATH."
        )

    if not NETWORK_FILE.exists():
        raise FileNotFoundError(
            "Generate the SUMO network first."
        )

    command = [
        binary,
        "-c", str(SUMO_CONFIG),
        "--seed", str(seed),
        "--no-step-log", "true",
        "--duration-log.disable", "true"
    ]

    if route_file is not None:
        command.extend([
            "--route-files",
            str(route_file)
        ])

    if gui:
        command.extend([
            "--start",
            "--delay", "50"
        ])

    traci.start(command)

    try:
        yield traci

    finally:
        traci.close()

def run_simulation(
    scenario="mixed",
    gui=False,
    seed=RANDOM_SEED
):

    route_file = generate_traffic(scenario)

    with sumo_session(
        gui=gui,
        seed=seed,
        route_file=route_file
    ) as connection:

        for step in range(SIMULATION_DURATION):

            connection.simulationStep()

            if (step + 1) % 30 == 0:

                vehicle_count = (
                    connection.vehicle.getIDCount()
                )

                print(
                    f"Time: {step + 1}s | "
                    f"Vehicles: {vehicle_count}"
                )

    print("Simulation completed successfully.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS),
        default="mixed"
    )

    parser.add_argument(
        "--gui",
        action="store_true"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED
    )

    args = parser.parse_args()

    run_simulation(
        scenario=args.scenario,
        gui=args.gui,
        seed=args.seed
    )