import shutil
import subprocess
import traci
import sumolib

sumo_binary = shutil.which("sumo")

if sumo_binary is None:
    raise RuntimeError(
        "SUMO executable not found. Add SUMO bin to PATH."
    )

print("SUMO executable:", sumo_binary)

result = subprocess.run(
    [sumo_binary, "--version"],
    capture_output=True,
    text=True,
    check=True
)

print(result.stdout)

print("TraCI imported successfully")
print("sumolib imported successfully")
print("SUMO setup verified")