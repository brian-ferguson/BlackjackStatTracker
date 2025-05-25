#!/usr/bin/env python3
"""
Reliable simulation that works locally without multiprocessing issues
"""

import random
import csv
import os
from datetime import datetime
from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

def generate_configurations():
    """Generate all 54 deck/penetration combinations"""
    deck_counts = [1, 2, 3, 4, 6, 8]
    configurations = []
    
    for deck_count in deck_counts:
        # No penetration
        configurations.append((deck_count, 0))
        
        # Penetrations going down by 0.25 until reaching half the deck count
        current_penetration = deck_count - 0.25
        while current_penetration >= deck_count / 2:
            configurations.append((deck_count, current_penetration))
            current_penetration -= 0.25
    
    return configurations

def simulate_configuration(deck_count, penetration, num_shoes):
    """Simulate one configuration without multiprocessing"""
    
    game = BlackjackGame()
    counter = HighLowCounter()
    
    true_count_stats = {}
    total_hands = 0
    
    print(f"Running {deck_count} deck(s), penetration {penetration}, {num_shoes:,} shoes...")
    
    for shoe_num in range(num_shoes):
        if shoe_num % (num_shoes // 10) == 0 and shoe_num > 0:
            progress = (shoe_num / num_shoes) * 100
            print(f"  Progress: {progress:.0f}% ({shoe_num:,}/{num_shoes:,} shoes)")
        
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
    
    # Save results
    os.makedirs('simulation_results', exist_ok=True)
    
    if penetration == 0:
        filename = f"simulation_results/{deck_count}decks-nopenetration.csv"
        penetration_desc = "No penetration (all cards played)"
    else:
        filename = f"simulation_results/{deck_count}decks-{penetration}penetration.csv"
        penetration_desc = f"{penetration} deck penetration"
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['# Blackjack High-Low Simulation Results with Player Edge Analysis'])
        writer.writerow([f'# Deck Count: {deck_count}'])
        writer.writerow([f'# Penetration: {penetration_desc}'])
        writer.writerow([f'# Total Shoes: {num_shoes:,}'])
        writer.writerow([f'# Total Hands: {total_hands:,}'])
        writer.writerow(['# Fixed Bet Amount: $10 per hand'])
        writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        # Column headers
        writer.writerow(['True Count', 'Frequency', 'Percentage', 'Player Edge', 'Total Profit', 'Total Wagered'])
        
        # Data
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
    
    print(f"  Completed! Total hands: {total_hands:,}")
    print(f"  Saved to {filename}")
    return filename

def run_full_simulation(num_shoes):
    """Run complete simulation for all configurations"""
    
    configurations = generate_configurations()
    print(f"Starting simulation with {num_shoes:,} shoes per configuration")
    print(f"Total configurations: {len(configurations)}")
    print("=" * 60)
    
    for i, (deck_count, penetration) in enumerate(configurations, 1):
        print(f"\nConfiguration {i}/{len(configurations)}:")
        simulate_configuration(deck_count, penetration, num_shoes)
    
    print(f"\n{'='*60}")
    print("All simulations completed!")
    print(f"Results saved to simulation_results/ folder")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        num_shoes = int(sys.argv[1])
    else:
        num_shoes = 1000
    
    run_full_simulation(num_shoes)