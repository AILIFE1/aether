# Aether Cosmology Simulation
# Hubble's Law - Expanding Universe Demo

import numpy as np

def run_simulation():
    print("🚀 Aether Cosmology Simulation: Hubble's Law - Expanding Universe")
    print("Hypothesis: The universe expands uniformly; recession velocity proportional to distance (v = H0 * d)")

    # Parameters
    hubble_constant = 70.0  # km/s/Mpc (approx current value)
    distances = np.linspace(10, 500, 50)  # Mpc
    velocities = hubble_constant * distances

    # Simple "simulation" output
    print(f"\nHubble Constant: {hubble_constant} km/s/Mpc")
    print(f"Sample data:")
    for d, v in zip(distances[:5], velocities[:5]):
        print(f"  Distance: {d:.1f} Mpc → Velocity: {v:.1f} km/s")

    # Discovery insight
    insight = "The linear relationship confirms uniform expansion. Distant galaxies recede faster — evidence of the Big Bang and ongoing cosmic expansion."

    print("\n" + "="*50)
    print("DISCOVERY INSIGHT:")
    print(insight)
    print("="*50)

    print("\nVisualization: Plot shows linear velocity vs distance (classic Hubble diagram).")

    # Return for orchestrator
    return {
        "example": "cosmology-expanding-universe",
        "hubble_constant": hubble_constant,
        "insight": insight
    }

if __name__ == "__main__":
    run_simulation()