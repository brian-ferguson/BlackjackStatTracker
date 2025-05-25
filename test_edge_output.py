#!/usr/bin/env python3
"""
Test to verify edge calculations are working and show proper CSV output
"""

import random
import csv
import os
from datetime import datetime
from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

def test_edge_calculation():
    """Test edge calculation with a small simulation"""
    
    game = BlackjackGame()
    counter = HighLowCounter()
    
    print("Testing edge calculation with 20 shoes...")
    
    # Track results by true count
    true_count_stats = {}
    total_hands = 0
    
    for shoe_num in range(20):
        shoe = create_deck(1)
        random.shuffle(shoe)
        counter.reset()
        
        while len(shoe) >= 10:
            remaining_decks = calculate_remaining_decks(len(shoe))
            true_count = round(counter.get_true_count_precise(remaining_decks))
            
            if -10 <= true_count <= 10:
                profit, bet = game.play_hand(shoe, true_count, counter)
                
                if bet > 0:
                    if true_count not in true_count_stats:
                        true_count_stats[true_count] = {
                            'frequency': 0,
                            'total_profit': 0.0,
                            'total_wagered': 0.0
                        }
                    
                    true_count_stats[true_count]['frequency'] += 1
                    true_count_stats[true_count]['total_profit'] += profit
                    true_count_stats[true_count]['total_wagered'] += bet
                    total_hands += 1
    
    print(f"Completed! Total hands: {total_hands}")
    
    # Create output directory
    os.makedirs('simulation_results', exist_ok=True)
    
    # Write CSV with edge calculations
    filename = 'simulation_results/test_edge_output.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['# Blackjack High-Low Simulation Results with Player Edge Analysis'])
        writer.writerow(['# Deck Count: 1'])
        writer.writerow(['# Penetration: No penetration (all cards played)'])
        writer.writerow([f'# Total Shoes: 20'])
        writer.writerow([f'# Total Hands: {total_hands:,}'])
        writer.writerow(['# Fixed Bet Amount: $10 per hand'])
        writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        # Column headers
        writer.writerow(['True Count', 'Frequency', 'Percentage', 'Player Edge', 'Total Profit', 'Total Wagered'])
        
        # Write data for each true count
        for true_count in range(-10, 11):
            if true_count in true_count_stats:
                stats = true_count_stats[true_count]
                frequency = stats['frequency']
                percentage = (frequency / total_hands) * 100 if total_hands > 0 else 0
                edge = (stats['total_profit'] / stats['total_wagered']) if stats['total_wagered'] > 0 else 0.0
                
                writer.writerow([
                    true_count,
                    frequency,
                    f"{percentage:.6f}",
                    f"{edge:.6f}",
                    f"{stats['total_profit']:.2f}",
                    f"{stats['total_wagered']:.2f}"
                ])
            else:
                writer.writerow([
                    true_count,
                    0,
                    "0.000000",
                    "0.000000", 
                    "0.00",
                    "0.00"
                ])
    
    print(f"Results saved to {filename}")
    
    # Show first few lines
    print("\nFirst 15 lines of output:")
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line.strip()}")
    
    # Show edge data for counts with hands played
    print(f"\nEdge data for true counts with hands played:")
    for tc in sorted(true_count_stats.keys()):
        stats = true_count_stats[tc]
        edge = (stats['total_profit'] / stats['total_wagered']) * 100 if stats['total_wagered'] > 0 else 0
        print(f"TC {tc:+2d}: {stats['frequency']:3d} hands, Edge: {edge:+6.2f}%")

if __name__ == "__main__":
    test_edge_calculation()