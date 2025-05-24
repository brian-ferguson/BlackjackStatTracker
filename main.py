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

def run_simulation(num_hands=1000000, num_processes=None):
    """Run the complete simulation suite"""
    print("Starting Blackjack High-Low Card Counting Simulation")
    print(f"Simulating {num_hands:,} hands per configuration")
    print("=" * 60)
    
    # Define simulation parameters
    deck_counts = [1, 2, 3, 4, 6, 8]
    penetrations = [5.5, 5.25, 5.0, 4.75, 4.5, 4.25, 4.0, 3.75, 3.5]
    
    # Create simulator
    simulator = BlackjackSimulator(num_processes=num_processes)
    
    # Run simulations
    try:
        results = simulator.run_full_simulation(deck_counts, penetrations, num_hands)
        
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

def run_web_interface():
    """Run the web interface"""
    print("Starting Blackjack Simulation Web Interface")
    print("Navigate to http://localhost:5000 to access the application")
    
    app = create_web_app()
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
