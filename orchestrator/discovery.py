# Aether Discovery Orchestrator

Simple CLI for running discovery experiments.

import argparse
from simulations.biology_predator_prey import run_simulation as run_biology
from simulations.cosmology_expanding_universe import run_simulation as run_cosmology

def main():
    parser = argparse.ArgumentParser(description='Aether Live Discovery Engine')
    parser.add_argument('--example', choices=['biology-predator-prey', 'cosmology-expanding-universe'], default='biology-predator-prey', help='Choose experiment')
    args = parser.parse_args()

    print('Aether Discovery Engine starting...')
    if args.example == 'biology-predator-prey':
        run_biology()
    elif args.example == 'cosmology-expanding-universe':
        run_cosmology()
    print('Discovery complete. What next?')

if __name__ == '__main__':
    main()