#!/usr/bin/env python3
"""
Run 4-deck simulation with 10,000 shoes and calculate average edge for played hands only
"""

import os
import csv
from datetime import datetime
from custom_simulation import simulate_configuration_custom
import time

def calculate_average_edge_played_only(true_count_stats, bet_spread):
    """Calculate average edge considering only true counts where we actually bet"""
    total_profit = 0
    total_wagered = 0
    
    for tc, stats in true_count_stats.items():
        # Only include true counts where we actually place bets (bet > 0)
        bet_size = 0
        if tc <= 0:
            bet_size = bet_spread.get('tc_neg', 0)
        elif tc == 1:
            bet_size = bet_spread.get('tc_1', 5)
        elif tc == 2:
            bet_size = bet_spread.get('tc_2', 10)
        elif tc == 3:
            bet_size = bet_spread.get('tc_3', 15)
        elif tc == 4:
            bet_size = bet_spread.get('tc_4', 25)
        else:  # tc >= 5
            bet_size = bet_spread.get('tc_5plus', 25)
        
        # Only count if we actually bet on this true count
        if bet_size > 0 and stats['total_wagered'] > 0:
            total_profit += stats['total_profit']
            total_wagered += stats['total_wagered']
    
    return (total_profit / total_wagered) if total_wagered > 0 else 0

def run_4deck_simulation():
    """Run 4-deck simulation with 10,000 shoes"""
    
    # Standard bet spread
    bet_spread = {
        'tc_neg': 0,    # Sit out TC <= 0
        'tc_1': 5,      # $5 at TC +1
        'tc_2': 10,     # $10 at TC +2
        'tc_3': 15,     # $15 at TC +3
        'tc_4': 25,     # $25 at TC +4
        'tc_5plus': 25  # $25 at TC +5+
    }
    
    print("🎰 Running 4-deck simulation with 10,000 shoes...")
    print("📊 Bet Spread: TC≤0=$0, TC+1=$5, TC+2=$10, TC+3=$15, TC+4=$25, TC+5+=$25")
    print("🃏 Configuration: 4 decks, no penetration")
    print()
    
    start_time = time.time()
    
    # Run the simulation
    true_count_stats, total_hands = simulate_configuration_custom(
        deck_count=4, 
        penetration=0,  # No penetration 
        num_shoes=10000, 
        bet_spread=bet_spread
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"✅ Simulation completed in {elapsed_time:.1f} seconds!")
    print(f"📈 Total hands played: {total_hands:,}")
    print()
    
    # Calculate average edge for played hands only
    average_edge_played = calculate_average_edge_played_only(true_count_stats, bet_spread)
    
    print("📊 RESULTS SUMMARY:")
    print("=" * 60)
    print(f"Average Edge (Played Hands Only): {average_edge_played*100:.4f}%")
    print()
    
    print("📋 Edge Per True Count (Only Counts Where We Bet):")
    print("-" * 50)
    print("TC    | Edge %   | Hands  | Total Profit | Total Wagered")
    print("-" * 50)
    
    total_profit_all = 0
    total_wagered_all = 0
    
    for tc in range(1, 11):  # Only show TC +1 through +10 (where we bet)
        if tc in true_count_stats and true_count_stats[tc]['frequency'] > 0:
            stats = true_count_stats[tc]
            edge = (stats['total_profit'] / stats['total_wagered']) if stats['total_wagered'] > 0 else 0
            frequency = stats['frequency']
            total_profit = stats['total_profit']
            total_wagered = stats['total_wagered']
            
            total_profit_all += total_profit
            total_wagered_all += total_wagered
            
            print(f"TC+{tc:2d} | {edge*100:7.3f} | {frequency:6,} | ${total_profit:10,.2f} | ${total_wagered:11,.2f}")
    
    print("-" * 50)
    print(f"TOTAL | {(total_profit_all/total_wagered_all)*100:7.3f} | {sum(stats['frequency'] for tc, stats in true_count_stats.items() if tc > 0):6,} | ${total_profit_all:10,.2f} | ${total_wagered_all:11,.2f}")
    print()
    
    # Save detailed results to CSV
    filename = f"4deck_10k_shoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header information
        writer.writerow(['# 4-Deck Blackjack Simulation Results (10,000 Shoes)'])
        writer.writerow([f'# Average Edge (Played Hands Only): {average_edge_played*100:.4f}%'])
        writer.writerow([f'# Total Hands Played: {total_hands:,}'])
        writer.writerow([f'# Bet Spread: TC≤0=$0, TC+1=$5, TC+2=$10, TC+3=$15, TC+4=$25, TC+5+=$25'])
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
    
    print(f"💾 Detailed results saved to: {filename}")
    print()
    
    # Hourly EV calculation
    hands_per_hour = 80  # Typical blackjack hands per hour
    hourly_ev = average_edge_played * total_wagered_all / total_hands * hands_per_hour
    
    print("💰 HOURLY EXPECTED VALUE:")
    print(f"Assuming {hands_per_hour} hands per hour:")
    print(f"Expected hourly profit: ${hourly_ev:.2f}")
    print(f"Based on average bet size: ${total_wagered_all/sum(stats['frequency'] for tc, stats in true_count_stats.items() if tc > 0):.2f}")

if __name__ == "__main__":
    run_4deck_simulation()