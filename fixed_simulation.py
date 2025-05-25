#!/usr/bin/env python3
"""
Fixed simulation that outputs edge calculations for risk of ruin analysis
"""

import random
import csv
import os
from datetime import datetime
from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

def run_fixed_simulation(deck_count=1, penetration=0, num_shoes=100):
    """Run simulation with proper edge output"""
    
    game = BlackjackGame()
    counter = HighLowCounter()
    
    print(f"Running {num_shoes} shoes: {deck_count} deck(s), penetration {penetration}")
    
    true_count_stats = {}
    total_hands = 0
    
    for shoe_num in range(num_shoes):
        if shoe_num % 20 == 0:
            print(f"  Shoe {shoe_num + 1}/{num_shoes}")
            
        shoe = create_deck(deck_count)
        random.shuffle(shoe)
        counter.reset()
        
        # Calculate cards to play based on penetration
        total_cards = deck_count * 52
        if penetration == 0:
            cards_to_play = total_cards
        else:
            cards_to_play = int(penetration * 52)
        
        cards_dealt = 0
        while len(shoe) >= 10 and cards_dealt < cards_to_play:
            remaining_decks = calculate_remaining_decks(len(shoe))
            true_count = round(counter.get_true_count_precise(remaining_decks))
            
            if -10 <= true_count <= 10:
                profit, bet = game.play_hand(shoe, true_count, counter)
                cards_dealt = total_cards - len(shoe)
                
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
    
    # Save results with edge calculations
    os.makedirs('simulation_results', exist_ok=True)
    
    if penetration == 0:
        filename = f"simulation_results/{deck_count}decks-nopenetration.csv"
        penetration_desc = "No penetration (all cards played)"
    else:
        filename = f"simulation_results/{deck_count}decks-{penetration}penetration.csv"
        penetration_desc = f"{penetration} deck penetration"
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header with metadata
        writer.writerow(['# Blackjack High-Low Simulation Results with Player Edge Analysis'])
        writer.writerow([f'# Deck Count: {deck_count}'])
        writer.writerow([f'# Penetration: {penetration_desc}'])
        writer.writerow([f'# Total Shoes: {num_shoes:,}'])
        writer.writerow([f'# Total Hands: {total_hands:,}'])
        writer.writerow(['# Fixed Bet Amount: $10 per hand'])
        writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        # Column headers - THIS IS WHAT YOU NEED FOR RISK OF RUIN
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
                    f"{edge:.6f}",  # PLAYER EDGE FOR RISK ANALYSIS
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
    return filename

if __name__ == "__main__":
    # Test with small simulation
    result_file = run_fixed_simulation(1, 0, 50)
    
    print(f"\nShowing output format:")
    with open(result_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line.strip()}")