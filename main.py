#!/usr/bin/env python3
"""
Blackjack High-Low Card Counting Simulation
Main entry point for the simulation application
"""

import sys
import os
from blackjack_simulator import BlackjackSimulator
from analysis import SimulationAnalyzer
from web_interface import create_web_app
import argparse

def main():
    parser = argparse.ArgumentParser(description='Blackjack High-Low Card Counting Simulation')
    parser.add_argument('--mode', choices=['simulate', 'web'], default='web',
                       help='Run mode: simulate for command line or web for web interface')
    parser.add_argument('--hands', type=int, default=1000000,
                       help='Number of hands to simulate per configuration')
    parser.add_argument('--processes', type=int, default=None,
                       help='Number of processes for parallel execution')
    
    args = parser.parse_args()
    
    if args.mode == 'simulate':
        run_simulation(args.hands, args.processes)
    else:
        run_web_interface()

def run_simulation(num_shoes=1000000, num_processes=None):
    """Run the complete simulation suite"""
    print("Starting Blackjack High-Low Card Counting Simulation")
    print(f"Simulating {num_shoes:,} shoes per configuration")
    print("=" * 60)
    
    # Generate all deck/penetration combinations
    configurations = generate_penetration_configurations()
    
    print(f"Total configurations to simulate: {len(configurations)}")
    print("\nConfigurations:")
    for config in configurations:
        deck_count, penetration = config
        if penetration == 0:
            print(f"  {deck_count}decks-nopenetration")
        else:
            print(f"  {deck_count}decks-{penetration}penetration")
    print("=" * 60)
    
    # Create simulator
    simulator = BlackjackSimulator(num_processes=num_processes)
    
    # Run simulations
    try:
        results = simulator.run_penetration_simulation(configurations, num_shoes)
        
        # Analyze results
        analyzer = SimulationAnalyzer(results)
        analyzer.generate_analysis_report()
        
        print("\nSimulation completed successfully!")
        print("Results saved to CSV files and analysis report generated.")
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during simulation: {e}")
        sys.exit(1)

def generate_penetration_configurations():
    """Generate all deck/penetration combinations according to specifications"""
    deck_counts = [1, 2, 3, 4, 6, 8]
    configurations = []
    
    for deck_count in deck_counts:
        # Start with no penetration (all cards played)
        configurations.append((deck_count, 0))
        
        # Generate penetrations going down by 0.25 until reaching half the deck count
        current_penetration = deck_count - 0.25
        min_penetration = deck_count / 2
        
        while current_penetration >= min_penetration:
            configurations.append((deck_count, current_penetration))
            current_penetration -= 0.25
    
    return configurations

def run_web_interface():
    """Run the web interface"""
    print("Starting Blackjack Simulation Web Interface")
    print("Navigate to http://localhost:5000 to access the application")
    
    app = create_web_app()
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
