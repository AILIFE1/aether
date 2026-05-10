# Aether Discovery Orchestrator

Simple CLI for running discovery experiments.

import argparse
from simulations.biology_predator_prey import run_simulation

def main():
    parser = argparse.ArgumentParser(description='Aether Live Discovery Engine')
    parser.add_argument('--example', choices=['biology-predator-prey'], default='biology-predator-prey', help='Choose experiment')
    args = parser.parse_args()

    print('🚀 Aether Discovery Engine starting...')
    if args.example == 'biology-predator-prey':
        run_simulation()
    print('✅ Discovery complete. What next?')

if __name__ == '__main__':
    main()
