#!/usr/bin/env python3
"""
Run 100,000 shoes simulation for 2-deck with optimal rules
"""

import time
from custom_simulation import simulate_configuration_custom

def run_large_simulation():
    """Run 100,000 shoes for 2-deck with surrender and S17"""
    
    print("🎰 RUNNING LARGE-SCALE SIMULATION")
    print("=" * 60)
    print("Configuration: 2 decks, 10,000 shoes")
    print("Rules: Surrender allowed, Dealer stands on soft 17")
    print("Bet Spread: TC≤0=$0, TC+1=$5, TC+2=$10, TC+3=$15, TC+4=$25, TC+5+=$25")
    print("=" * 60)
    
    # Standard bet spread
    bet_spread = {
        'tc_neg': 0,    # Sit out TC ≤ 0
        'tc_1': 5,      # $5 at TC +1
        'tc_2': 10,     # $10 at TC +2
        'tc_3': 15,     # $15 at TC +3
        'tc_4': 25,     # $25 at TC +4
        'tc_5plus': 25  # $25 at TC +5+
    }
    
    # Optimal table rules (already set in advanced_blackjack_game.py)
    table_rules = {
        'dealer_hits_soft17': False,  # Dealer stands on soft 17
        'surrender_allowed': True,    # Surrender allowed
        'double_after_split': True,
        'split_aces': True,
        'blackjack_pays': 1.5
    }
    
    print("🚀 Starting simulation...")
    start_time = time.time()
    
    # Run the simulation
    true_count_stats, total_hands = simulate_configuration_custom(
        deck_count=2,
        penetration=0,  # No penetration limit
        num_shoes=10000,
        bet_spread=bet_spread,
        table_rules=table_rules
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n✅ Simulation completed in {elapsed_time:.1f} seconds!")
    print(f"📊 Total hands played: {total_hands:,}")
    
    # Calculate overall edge for played hands only
    total_profit_played = 0
    total_wagered_played = 0
    hands_played = 0
    
    for tc, stats in true_count_stats.items():
        # Only include hands where we actually bet
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
        
        if bet_size > 0 and stats['total_wagered'] > 0:
            total_profit_played += stats['total_profit']
            total_wagered_played += stats['total_wagered']
            hands_played += stats['frequency']
    
    overall_edge = (total_profit_played / total_wagered_played) * 100 if total_wagered_played > 0 else 0
    
    print(f"\n🎯 OVERALL RESULTS:")
    print("=" * 60)
    print(f"Average Edge (Played Hands Only): {overall_edge:.4f}%")
    print(f"Total Profit: ${total_profit_played:,.2f}")
    print(f"Total Wagered: ${total_wagered_played:,.2f}")
    print(f"Hands Played: {hands_played:,}")
    print(f"Average Bet Size: ${total_wagered_played/hands_played:.2f}")
    
    print(f"\n📈 EDGE BY TRUE COUNT:")
    print("=" * 60)
    print("True Count | Edge %    | Hands     | Profit      | Wagered")
    print("-" * 60)
    
    # Show edge for all true counts where we bet
    for tc in range(1, 11):
        if tc in true_count_stats and true_count_stats[tc]['frequency'] > 0:
            stats = true_count_stats[tc]
            edge = (stats['total_profit'] / stats['total_wagered']) * 100 if stats['total_wagered'] > 0 else 0
            frequency = stats['frequency']
            total_profit = stats['total_profit']
            total_wagered = stats['total_wagered']
            
            print(f"TC +{tc:2d}      | {edge:8.4f} | {frequency:9,} | ${total_profit:10,.2f} | ${total_wagered:10,.2f}")
    
    print("-" * 60)
    print(f"TOTAL      | {overall_edge:8.4f} | {hands_played:9,} | ${total_profit_played:10,.2f} | ${total_wagered_played:10,.2f}")
    
    # Show expected values
    print(f"\n💰 HOURLY EXPECTED VALUE:")
    print("=" * 60)
    avg_bet = total_wagered_played / hands_played
    hands_per_hour = 80  # Typical blackjack
    hourly_ev = (overall_edge / 100) * avg_bet * hands_per_hour
    print(f"Average bet size: ${avg_bet:.2f}")
    print(f"Hands per hour: {hands_per_hour}")
    print(f"Expected hourly EV: ${hourly_ev:.2f}")
    
    # Show comparison to theoretical Hi-Lo expectations
    print(f"\n📚 COMPARISON TO THEORETICAL HI-LO:")
    print("=" * 60)
    theoretical_edges = {
        1: 0.0, 2: 0.5, 3: 1.0, 4: 1.5, 5: 2.0, 6: 2.5, 7: 3.0, 8: 3.5, 9: 4.0, 10: 4.5
    }
    
    print("TC | Simulated | Theoretical | Difference")
    print("-" * 40)
    for tc in range(1, 8):
        if tc in true_count_stats and true_count_stats[tc]['frequency'] > 0:
            stats = true_count_stats[tc]
            sim_edge = (stats['total_profit'] / stats['total_wagered']) * 100
            theo_edge = theoretical_edges.get(tc, 0)
            diff = sim_edge - theo_edge
            status = "✓" if abs(diff) < 0.5 else "⚠"
            print(f"{tc:2d} | {sim_edge:8.4f}% | {theo_edge:10.1f}% | {diff:+7.3f}% {status}")
    
    return true_count_stats, total_hands, overall_edge

if __name__ == "__main__":
    run_large_simulation()