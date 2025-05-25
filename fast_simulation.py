#!/usr/bin/env python3
"""
Fast, efficient simulation with clear progress tracking
"""

import random
import csv
import os
import time
from datetime import datetime
from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

def simulate_configuration_fast(deck_count, penetration, num_shoes):
    """Fast simulation with progress tracking"""
    
    start_time = time.time()
    game = BlackjackGame()
    counter = HighLowCounter()
    
    true_count_stats = {}
    total_hands = 0
    
    print(f"  Running {deck_count} deck(s), penetration {penetration}, {num_shoes:,} shoes...")
    
    # Progress tracking
    progress_interval = max(1, num_shoes // 20)  # Show progress every 5%
    
    for shoe_num in range(num_shoes):
        # Show progress
        if shoe_num % progress_interval == 0 or shoe_num == num_shoes - 1:
            progress = ((shoe_num + 1) / num_shoes) * 100
            elapsed = time.time() - start_time
            if shoe_num > 0:
                rate = shoe_num / elapsed
                eta = (num_shoes - shoe_num) / rate if rate > 0 else 0
                print(f"    Progress: {progress:.1f}% ({shoe_num + 1:,}/{num_shoes:,}) - ETA: {eta:.0f}s")
            else:
                print(f"    Progress: {progress:.1f}% ({shoe_num + 1:,}/{num_shoes:,})")
        
        # Create and shuffle deck
        shoe = create_deck(deck_count)
        random.shuffle(shoe)
        counter.reset()
        
        # Calculate penetration
        total_cards = deck_count * 52
        if penetration == 0:
            cards_to_play = total_cards - 5  # Leave a few cards
        else:
            cards_to_play = int(penetration * 52)
        
        cards_dealt = 0
        hands_this_shoe = 0
        
        # Play through the shoe efficiently
        while len(shoe) >= 10 and cards_dealt < cards_to_play and hands_this_shoe < 50:
            remaining_decks = calculate_remaining_decks(len(shoe))
            if remaining_decks <= 0:
                break
                
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
                    hands_this_shoe += 1
            else:
                # Skip extreme counts but still deal some cards
                if len(shoe) >= 4:
                    for _ in range(2):
                        if shoe:
                            card = shoe.pop()
                            counter.add_card(card)
                cards_dealt = total_cards - len(shoe)
    
    elapsed = time.time() - start_time
    print(f"    Completed in {elapsed:.1f}s! Total hands: {total_hands:,}")
    
    return true_count_stats, total_hands

def save_results_fast(deck_count, penetration, num_shoes, true_count_stats, total_hands):
    """Save results quickly"""
    
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
        writer.writerow(['# Bet Spread: TC≤0 sit out, TC1=$5, TC2=$10, TC3=$15, TC4+=$25'])
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
    
    print(f"  Saved to {filename}")
    return filename

def run_fast_simulation(num_shoes):
    """Run fast simulation with clear progress"""
    
    # Generate all configurations
    deck_counts = [1, 2, 3, 4, 6, 8]
    configurations = []
    
    for deck_count in deck_counts:
        configurations.append((deck_count, 0))  # No penetration
        current_penetration = deck_count - 0.25
        while current_penetration >= deck_count / 2:
            configurations.append((deck_count, current_penetration))
            current_penetration -= 0.25
    
    print(f"Fast Simulation: {num_shoes:,} shoes per configuration")
    print(f"Total configurations: {len(configurations)}")
    print("=" * 60)
    
    overall_start = time.time()
    
    for i, (deck_count, penetration) in enumerate(configurations, 1):
        print(f"\nConfiguration {i}/{len(configurations)}:")
        
        stats, total_hands = simulate_configuration_fast(deck_count, penetration, num_shoes)
        save_results_fast(deck_count, penetration, num_shoes, stats, total_hands)
        
        # Show overall progress
        overall_progress = (i / len(configurations)) * 100
        elapsed = time.time() - overall_start
        if i > 1:
            rate = i / elapsed
            eta = (len(configurations) - i) / rate if rate > 0 else 0
            print(f"  Overall progress: {overall_progress:.1f}% ({i}/{len(configurations)}) - ETA: {eta/60:.1f} min")
    
    total_time = time.time() - overall_start
    print(f"\n{'='*60}")
    print(f"All simulations completed in {total_time/60:.1f} minutes!")
    print("Results saved to simulation_results/ folder")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        num_shoes = int(sys.argv[1])
    else:
        num_shoes = 1000
    
    run_fast_simulation(num_shoes)