# Aether Discovery Orchestrator

Simple CLI for running discovery experiments.


import argparse
from simulations.biology_predator_prey import run_simulation as run_biology
from simulations.cosmology_expanding_universe import run_simulation as run_cosmology
from simulations.physics_double_slit import run_simulation as run_physics
from simulations.black_hole_accretion import run_simulation as run_black_hole

def main():
    parser = argparse.ArgumentParser(description='Aether Live Discovery Engine')
    parser.add_argument('--example', choices=[
        'biology-predator-prey',
        'cosmology-expanding-universe',
        'physics-double-slit',
        'black-hole-accretion'
    ], default='biology-predator-prey', help='Choose experiment')
    args = parser.parse_args()

    print('🚀 Aether Discovery Engine starting...')
    if args.example == 'biology-predator-prey':
        run_biology()
    elif args.example == 'cosmology-expanding-universe':
        run_cosmology()
    elif args.example == 'physics-double-slit':
        run_physics()
    elif args.example == 'black-hole-accretion':
        run_black_hole()
    print('\n✅ Discovery complete. What next?')

if __name__ == '__main__':
    main()
