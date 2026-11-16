import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import ZGate
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# ==========================================
# EDIT THESE VALUES DIRECTLY
# ==========================================
TARGET_STATES = ["01"]  # Examples: ["00"], ["11"], ["01", "10"], or ["101"]
SHOTS = 1024
NOISE_LEVELS = [0.0, 0.01, 0.05, 0.1]
# ==========================================


def build_and_run_grover(targets, shots, noise_level):
    num_qubits = len(targets[0])
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))

    iterations = math.floor(
        (math.pi / 4) * math.sqrt((2**num_qubits) / len(targets))
    )

    for _ in range(iterations):
        # Oracle
        for target in targets:
            rev = target[::-1]
            for i, bit in enumerate(rev):
                if bit == "0":
                    qc.x(i)
            qc.append(ZGate().control(num_qubits - 1), range(num_qubits))
            for i, bit in enumerate(rev):
                if bit == "0":
                    qc.x(i)

        # Diffuser
        qc.h(range(num_qubits))
        qc.x(range(num_qubits))
        qc.append(ZGate().control(num_qubits - 1), range(num_qubits))
        qc.x(range(num_qubits))
        qc.h(range(num_qubits))

    qc.measure_all()

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(
        depolarizing_error(noise_level, 1), ["sx", "x"]
    )
    noise_model.add_all_qubit_quantum_error(
        depolarizing_error(noise_level, 2), ["cx"]
    )
    simulator = AerSimulator(noise_model=noise_model)
    circuit = transpile(qc, simulator)
    result = simulator.run(circuit, shots=shots).result()
    return result.get_counts()


if __name__ == "__main__":
    print("Target:", TARGET_STATES)
    for noise_level in NOISE_LEVELS:
        counts = build_and_run_grover(TARGET_STATES, SHOTS, noise_level)
        matches = sum(counts.get(target, 0) for target in TARGET_STATES)
        match_rate = matches / SHOTS * 100
        print(
            f"Noise {noise_level:.0%}: "
            f"{matches}/{SHOTS} target matches ({match_rate:.1f}%)"
        )
        print("Results:", counts)
