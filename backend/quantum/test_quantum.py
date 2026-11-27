import pennylane as qml
import torch

device = qml.device("default.qubit", wires=4)

@qml.qnode(device, interface="torch")
def quantum_circuit(inputs):

    qml.AngleEmbedding(
        inputs,
        wires=range(4),
        rotation="Y"
    )

    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    qml.CNOT(wires=[2, 3])

    return [
        qml.expval(qml.PauliZ(i))
        for i in range(4)
    ]

features = torch.tensor([0.2, 0.4, 0.6, 0.8])

result = quantum_circuit(features)

print("PennyLane is working successfully")
print("PyTorch version:", torch.__version__)
print("Number of qubits: 4")
print("Quantum circuit output:", result)