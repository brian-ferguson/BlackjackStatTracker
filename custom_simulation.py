#!/usr/bin/env python3
"""
Custom blackjack simulation with user-defined bet spreads
"""

import csv
import os
import time
from datetime import datetime
from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks, format_percentage
import random

def generate_configurations():
    """Generate all deck/penetration combinations"""
    configurations = []
    
    # 1 deck configurations
    configurations.append((1, 0))       # No penetration
    configurations.append((1, 0.75))    # 0.75 deck penetration  
    configurations.append((1, 0.5))     # 0.5 deck penetration
    
    # 2 deck configurations
    configurations.append((2, 0))       # No penetration
    for pen in [1.75, 1.5, 1.25, 1.0]:
        configurations.append((2, pen))
    
    # 3 deck configurations
    configurations.append((3, 0))       # No penetration
    for pen in [2.75, 2.5, 2.25, 2.0, 1.75, 1.5]:
        configurations.append((3, pen))
    
    # 4 deck configurations
    configurations.append((4, 0))       # No penetration
    for pen in [3.75, 3.5, 3.25, 3.0, 2.75, 2.5, 2.25, 2.0]:
        configurations.append((4, pen))
    
    # 6 deck configurations
    configurations.append((6, 0))       # No penetration
    for pen in [5.75, 5.5, 5.25, 5.0, 4.75, 4.5, 4.25, 4.0, 3.75, 3.5, 3.25, 3.0]:
        configurations.append((6, pen))
    
    # 8 deck configurations
    configurations.append((8, 0))       # No penetration
    for pen in [7.75, 7.5, 7.25, 7.0, 6.75, 6.5, 6.25, 6.0, 5.75, 5.5, 5.25, 5.0, 4.75, 4.5, 4.25, 4.0]:
        configurations.append((8, pen))
    
    return configurations

def create_bet_spread_folder(bet_spread, num_shoes):
    """Create folder name based on bet spread and number of shoes"""
    spread_parts = []
    if bet_spread['tc_neg'] > 0:
        spread_parts.append(f"TC0-{bet_spread['tc_neg']}")
    else:
        spread_parts.append("TC0-sitout")
    
    spread_parts.append(f"TC1-{bet_spread['tc_1']}")
    spread_parts.append(f"TC2-{bet_spread['tc_2']}")
    spread_parts.append(f"TC3-{bet_spread['tc_3']}")
    spread_parts.append(f"TC4-{bet_spread['tc_4']}")
    spread_parts.append(f"TC5plus-{bet_spread['tc_5plus']}")
    
    folder_name = f"{'_'.join(spread_parts)}_{num_shoes}shoes"
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    return folder_name

def simulate_configuration_custom(deck_count, penetration, num_shoes, bet_spread, progress_callback=None):
    """Simulate one configuration with custom bet spread"""
    game = BlackjackGame()
    
    # Update bet spread in game
    game.base_bet = 5  # Base bet amount
    game.bet_spread = bet_spread
    
    # Override get_bet_amount method with custom spread
    def custom_get_bet_amount(true_count):
        tc = round(true_count)
        if tc <= 0:
            return bet_spread['tc_neg']
        elif tc == 1:
            return bet_spread['tc_1']
        elif tc == 2:
            return bet_spread['tc_2']
        elif tc == 3:
            return bet_spread['tc_3']
        elif tc == 4:
            return bet_spread['tc_4']
        else:  # tc >= 5
            return bet_spread['tc_5plus']
    
    game.get_bet_amount = custom_get_bet_amount
    
    # Statistics tracking
    true_count_stats = {}
    total_hands = 0
    
    for shoe_num in range(num_shoes):
        if progress_callback and shoe_num % max(1, num_shoes // 20) == 0:
            progress = (shoe_num / num_shoes) * 100
            progress_callback(progress)
        
        # Create and shuffle new shoe
        shoe = create_deck(deck_count)
        random.shuffle(shoe)
        
        # Calculate penetration (cards to deal before reshuffling)
        total_cards = len(shoe)
        if penetration > 0:
            cards_to_deal = int(penetration * 52)
        else:
            cards_to_deal = total_cards  # No penetration limit
        
        # Reset counter for new shoe
        counter = HighLowCounter()
        cards_dealt = 0
        
        # Play hands until penetration reached
        while cards_dealt < cards_to_deal and len(shoe) >= 10:
            remaining_cards = len(shoe)
            remaining_decks = calculate_remaining_decks(remaining_cards)
            true_count = counter.get_true_count_precise(remaining_decks)
            
            # Play hand
            cards_before = len(shoe)
            profit, bet = game.play_hand(shoe, true_count, counter)
            cards_after = len(shoe)
            cards_dealt += (cards_before - cards_after)
            
            if bet > 0:  # Only count hands where we actually played
                tc_rounded = round(true_count)
                if tc_rounded not in true_count_stats:
                    true_count_stats[tc_rounded] = {
                        'frequency': 0,
                        'total_profit': 0.0,
                        'total_wagered': 0.0
                    }
                
                true_count_stats[tc_rounded]['frequency'] += 1
                true_count_stats[tc_rounded]['total_profit'] += profit
                true_count_stats[tc_rounded]['total_wagered'] += bet
                total_hands += 1
    
    if progress_callback:
        progress_callback(100)
    
    return true_count_stats, total_hands

def save_results_custom(deck_count, penetration, num_shoes, true_count_stats, total_hands, folder_name, bet_spread):
    """Save results to custom folder"""
    # Create filename
    if penetration == 0:
        penetration_desc = "nopenetration"
    else:
        penetration_desc = f"{penetration}penetration"
    
    filename = f"{deck_count}decks-{penetration_desc}.csv"
    filepath = os.path.join(folder_name, filename)
    
    # Prepare bet spread description
    bet_desc = f"TC<=0=${bet_spread['tc_neg']}, TC1=${bet_spread['tc_1']}, TC2=${bet_spread['tc_2']}, TC3=${bet_spread['tc_3']}, TC4=${bet_spread['tc_4']}, TC5+=${bet_spread['tc_5plus']}"
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header information
        writer.writerow(['# Blackjack High-Low Simulation Results with Custom Bet Spread'])
        writer.writerow([f'# Deck Count: {deck_count}'])
        writer.writerow([f'# Penetration: {penetration_desc}'])
        writer.writerow([f'# Total Shoes: {num_shoes:,}'])
        writer.writerow([f'# Total Hands: {total_hands:,}'])
        writer.writerow([f'# Bet Spread: {bet_desc}'])
        writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        # Column headers
        writer.writerow(['True Count', 'Frequency', 'Percentage', 'Player Edge', 'Total Profit', 'Total Wagered'])
        
        # Write data for all true counts from -10 to +10
        for tc in range(-10, 11):
            if tc in true_count_stats and true_count_stats[tc]['frequency'] > 0:
                stats = true_count_stats[tc]
                frequency = stats['frequency']
                percentage = (frequency / total_hands) * 100 if total_hands > 0 else 0
                total_profit = stats['total_profit']
                total_wagered = stats['total_wagered']
                edge = (total_profit / total_wagered) if total_wagered > 0 else 0
                
                writer.writerow([
                    tc, frequency, f"{percentage:.6f}", f"{edge:.6f}",
                    f"{total_profit:.2f}", f"{total_wagered:.2f}"
                ])
            else:
                writer.writerow([tc, 0, "0.000000", "0.000000", "0.00", "0.00"])

def run_custom_simulation(bet_spread, num_shoes, progress_callback=None):
    """Run custom simulation with specified bet spread"""
    configurations = generate_configurations()
    total_configs = len(configurations)
    
    # Create results folder
    folder_name = create_bet_spread_folder(bet_spread, num_shoes)
    
    print(f"Custom Simulation: {num_shoes:,} shoes per configuration")
    print(f"Bet Spread: TC<=0=${bet_spread['tc_neg']}, TC1=${bet_spread['tc_1']}, TC2=${bet_spread['tc_2']}, TC3=${bet_spread['tc_3']}, TC4=${bet_spread['tc_4']}, TC5+=${bet_spread['tc_5plus']}")
    print(f"Total configurations: {total_configs}")
    print(f"Results will be saved to: {folder_name}")
    print("=" * 60)
    
    start_time = time.time()
    
    for i, (deck_count, penetration) in enumerate(configurations, 1):
        config_start = time.time()
        
        if penetration == 0:
            penetration_desc = "no penetration"
        else:
            penetration_desc = f"penetration {penetration}"
        
        print(f"\nConfiguration {i}/{total_configs}:")
        print(f"  Running {deck_count} deck(s), {penetration_desc}, {num_shoes:,} shoes...")
        
        def config_progress(progress):
            print(f"    Progress: {progress:.1f}% ({int(progress * num_shoes / 100)}/{num_shoes:,})")
        
        stats, total_hands = simulate_configuration_custom(
            deck_count, penetration, num_shoes, bet_spread, config_progress
        )
        
        config_time = time.time() - config_start
        print(f"    Completed in {config_time:.1f}s! Total hands: {total_hands:,}")
        
        # Save results
        save_results_custom(deck_count, penetration, num_shoes, stats, total_hands, folder_name, bet_spread)
        
        if penetration == 0:
            filename = f"{deck_count}decks-nopenetration.csv"
        else:
            filename = f"{deck_count}decks-{penetration}penetration.csv"
        print(f"  Saved to {folder_name}/{filename}")
        
        # Overall progress
        overall_progress = (i / total_configs) * 100
        remaining_time = ((time.time() - start_time) / i) * (total_configs - i) / 60
        print(f"  Overall progress: {overall_progress:.1f}% ({i}/{total_configs}) - ETA: {remaining_time:.1f} min")
        
        if progress_callback:
            progress_callback(i, total_configs, f"Completed {deck_count} decks, {penetration_desc}")
    
    total_time = (time.time() - start_time) / 60
    print("=" * 60)
    print(f"All simulations completed in {total_time:.1f} minutes!")
    print(f"Results saved to {folder_name}/ folder")
    
    return folder_name

if __name__ == "__main__":
    # Default bet spread
    default_spread = {
        'tc_neg': 0,
        'tc_1': 5,
        'tc_2': 10,
        'tc_3': 15,
        'tc_4': 25,
        'tc_5plus': 25
    }
    
    # Run simulation
    run_custom_simulation(default_spread, 100000)