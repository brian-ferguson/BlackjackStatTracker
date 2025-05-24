#!/usr/bin/env python3
"""
Test script to show all configurations that will be generated
"""

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

def main():
    print("Blackjack High-Low Simulation Configuration List")
    print("=" * 60)
    
    configurations = generate_penetration_configurations()
    
    print(f"Total configurations: {len(configurations)}")
    print("\nFiles that will be generated:")
    print("-" * 40)
    
    for deck_count, penetration in configurations:
        if penetration == 0:
            filename = f"{deck_count}decks-nopenetration.csv"
            description = f"{deck_count} decks, all cards played"
        else:
            filename = f"{deck_count}decks-{penetration}penetration.csv"
            description = f"{deck_count} decks, {penetration} deck penetration ({penetration/deck_count*100:.1f}% of cards played)"
        
        print(f"{filename:<35} - {description}")
    
    print("\nEach file will contain true count distributions from -10 to +10")
    print("with percentages based on 1,000,000 simulated hands per configuration.")

if __name__ == "__main__":
    main()