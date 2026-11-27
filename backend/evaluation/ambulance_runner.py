import tempfile

from pathlib import Path

from config import (
    SUMO_DIR,
    SIMULATION_DURATION,
    RANDOM_SEED
)

from simulation.sumo_runner import sumo_session

from simulation.traffic_generator import (
    generate_traffic
)


def measure_travel_time(
    edges,
    scenario="mixed",
    seed=RANDOM_SEED,
    departure_time=240,
    gui=False
):

    if not edges:
        raise ValueError("Route cannot be empty.")

    if not 0 <= departure_time < SIMULATION_DURATION:
        raise ValueError("Invalid departure time.")

    ambulance_id = "research_ambulance"

    complete_route = [
        "ENTRY",
        *edges,
        "EXIT"
    ]

    actual_departure = None
    arrival_time = None
    waiting_time = 0.0
    time_loss = None

    with tempfile.TemporaryDirectory(
        dir=SUMO_DIR
    ) as temporary_directory:

        route_file = (
            Path(temporary_directory)
            / "evaluation.rou.xml"
        )

        generate_traffic(
            scenario=scenario,
            output_file=route_file
        )

        with sumo_session(
            gui=gui,
            seed=seed,
            route_file=route_file
        ) as connection:

            for _ in range(departure_time):

                connection.simulationStep()

            requested_departure = float(
                connection.simulation.getTime()
            )

            connection.route.add(
                "ambulance_route",
                complete_route
            )

            connection.vehicle.add(
                vehID=ambulance_id,
                routeID="ambulance_route",
                typeID="ambulance",
                depart="now",
                departLane="best",
                departSpeed="max"
            )

            while (
                connection.simulation.getTime()
                < SIMULATION_DURATION
            ):

                connection.simulationStep()

                current_time = float(
                    connection.simulation.getTime()
                )

                departed = (
                    connection.simulation
                    .getDepartedIDList()
                )

                arrived = (
                    connection.simulation
                    .getArrivedIDList()
                )

                if ambulance_id in departed:

                    actual_departure = float(
                        connection.vehicle.getDeparture(
                            ambulance_id
                        )
                    )

                if ambulance_id in arrived:

                    arrival_time = current_time
                    break

                if ambulance_id in (
                    connection.vehicle.getIDList()
                ):

                    speed = connection.vehicle.getSpeed(
                        ambulance_id
                    )

                    if speed < 0.1:
                        waiting_time += 1.0

                    time_loss = (
                        connection.vehicle.getTimeLoss(
                            ambulance_id
                        )
                    )

    completed = (
        arrival_time is not None
        and actual_departure is not None
    )

    return {
        "completed": completed,
        "route": complete_route,
        "requested_departure": requested_departure,
        "actual_departure": actual_departure,
        "arrival_time": arrival_time,

        "travel_time": (
            round(
                arrival_time - requested_departure,
                2
            )
            if completed else None
        ),

        "driving_time": (
            round(
                arrival_time - actual_departure,
                2
            )
            if completed else None
        ),

        "insertion_delay": (
            round(
                actual_departure - requested_departure,
                2
            )
            if actual_departure is not None else None
        ),

        "waiting_time": waiting_time,
        "last_observed_time_loss": time_loss,

        "status": (
            "Arrived"
            if completed
            else "Not arrived before simulation ended"
        )
    }