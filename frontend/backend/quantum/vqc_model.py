import pennylane as qml

import torch
from torch import nn

from config import (
    N_QUBITS,
    N_LAYERS,
    CLASS_NAMES
)

device = qml.device(
    "default.qubit",
    wires=N_QUBITS
)

@qml.qnode(
    device,
    interface="torch",
    diff_method="backprop"
)
def quantum_circuit(inputs, weights):

    qml.AngleEmbedding(
        features=inputs,
        wires=range(N_QUBITS),
        rotation="Y"
    )

    qml.StronglyEntanglingLayers(
        weights=weights,
        wires=range(N_QUBITS)
    )

    return [
        qml.expval(qml.PauliZ(wire))
        for wire in range(N_QUBITS)
    ]

class VQCModel(nn.Module):

    def __init__(self):

        super().__init__()

        weight_shapes = {
            "weights": (
                N_LAYERS,
                N_QUBITS,
                3
            )
        }

        self.quantum_layer = qml.qnn.TorchLayer(
            quantum_circuit,
            weight_shapes
        )

        self.output_layer = nn.Linear(
            N_QUBITS,
            len(CLASS_NAMES)
        )

    def forward(self, inputs):

        quantum_output = self.quantum_layer(
            inputs
        )

        logits = self.output_layer(
            quantum_output
        )

        return logits

if __name__ == "__main__":

    model = VQCModel()

    sample = torch.rand(5, N_QUBITS)

    output = model(sample)

    print(model)

    print("\nInput shape:", sample.shape)
    print("Output shape:", output.shape)

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    print("Trainable parameters:", parameter_count)