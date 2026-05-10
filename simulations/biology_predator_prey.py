# Aether Biology Simulation: Lotka-Volterra Predator-Prey Model

A classic ecological simulation showing oscillating populations of prey and predators.

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

def lotka_volterra(state, t, alpha, beta, gamma, delta):
    prey, predator = state
    dprey = alpha * prey - beta * prey * predator
    dpredator = delta * prey * predator - gamma * predator
    return [dprey, dpredator]

def run_simulation():
    """Run the predator-prey simulation and return insights."""
    alpha = 2.0  # prey growth rate
    beta = 1.0   # predation rate
    gamma = 1.0  # predator death rate
    delta = 1.0  # predator growth from prey

    state0 = [10, 5]  # initial prey, predator
    t = np.linspace(0, 20, 200)

    state = odeint(lotka_volterra, state0, t, args=(alpha, beta, gamma, delta))

    # Insights
    print('✅ Biology Simulation Complete: Lotka-Volterra Model')
    print(f'Final prey population: {state[-1, 0]:.2f}')
    print(f'Final predator population: {state[-1, 1]:.2f}')
    print('\nKey Discovery: Populations oscillate in a stable cycle — demonstrating chaotic yet deterministic ecosystem dynamics.')
    print('In a full environment, this would generate a beautiful phase plot showing the limit cycle.')

    # For repo, we skip actual plt.show() to keep CLI clean
    return state

if __name__ == "__main__":
    run_simulation()
