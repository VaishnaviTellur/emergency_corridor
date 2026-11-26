import argparse
import xml.etree.ElementTree as ET

from config import ROUTES_FILE, SIMULATION_DURATION

ROUTES = {
    "route_A": "ENTRY SA AB BH EXIT",
    "route_B": "ENTRY SC CD DH EXIT",
    "route_C": "ENTRY SE EF FH EXIT"
}

# Requested traffic demand in vehicles per hour.
SCENARIOS = {
    "low": (250, 250, 250),
    "medium": (700, 700, 700),
    "high": (1400, 1400, 1400),
    "mixed": (250, 2000, 700),
    "upper_busy": (2000, 250, 700),
    "lower_busy": (700, 250, 2000)
}

def generate_traffic(
    scenario="mixed",
    output_file=ROUTES_FILE
):

    if scenario not in SCENARIOS:
        raise ValueError(
            f"Invalid scenario: {scenario}"
        )

    root = ET.Element("routes")

    ET.SubElement(
        root,
        "vType",
        {
            "id": "car",
            "vClass": "passenger",
            "accel": "2.6",
            "decel": "4.5",
            "sigma": "0.5",
            "length": "5.0",
            "minGap": "2.5",
            "maxSpeed": "16.67",
            "speedFactor": "1.0",
            "speedDev": "0.1"
        }
    )

    ET.SubElement(
        root,
        "vType",
        {
            "id": "ambulance",
            "vClass": "emergency",
            "accel": "2.6",
            "decel": "4.5",
            "length": "5.5",
            "minGap": "2.5",
            "maxSpeed": "16.67"
        }
    )

    for route_id, edges in ROUTES.items():

        ET.SubElement(
            root,
            "route",
            {
                "id": route_id,
                "edges": edges
            }
        )

    rates = SCENARIOS[scenario]

    for index, route_id in enumerate(ROUTES):

        ET.SubElement(
            root,
            "flow",
            {
                "id": f"flow_{index}",
                "type": "car",
                "route": route_id,
                "begin": "0",
                "end": str(SIMULATION_DURATION),
                "vehsPerHour": str(rates[index]),
                "departLane": "best",
                "departSpeed": "max"
            }
        )

    tree = ET.ElementTree(root)

    ET.indent(tree, space="    ")

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"Traffic scenario: {scenario}")
    print(f"Traffic demand: {rates}")
    print(f"Routes saved to: {output_file}")

    return output_file

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS),
        default="mixed"
    )

    args = parser.parse_args()

    generate_traffic(args.scenario)