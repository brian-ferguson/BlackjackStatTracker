#!/usr/bin/env python3
"""
Test single configuration with 1000 shoes to verify output
"""

from blackjack_simulator import BlackjackSimulator

def test_single_configuration():
    """Test one configuration with 1000 shoes"""
    
    simulator = BlackjackSimulator()
    
    # Test 1 deck, no penetration, 1000 shoes
    print("Testing 1 deck, no penetration, 1000 shoes...")
    result = simulator._simulate_configuration(1, 0, 1000)
    simulator._save_penetration_results(1, 0, result)
    
    print("Test completed!")
    
    # Show first few lines of output
    filename = 'simulation_results/1decks-nopenetration.csv'
    print(f"\nFirst 15 lines of {filename}:")
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f.readlines()[:15]):
                print(f"{i+1:2d}: {line.strip()}")
    except FileNotFoundError:
        print("File not found")

if __name__ == "__main__":
    test_single_configuration()