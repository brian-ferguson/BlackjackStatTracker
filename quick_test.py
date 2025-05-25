#!/usr/bin/env python3
"""
Quick test of the blackjack simulation with corrected basic strategy
"""

import random
from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks
import pandas as pd
import os

def run_quick_test():
    """Run a small test simulation to verify the basic strategy works"""
    
    game = BlackjackGame()
    counter = HighLowCounter()
    
    print("Running quick test: 1 deck, 10 shoes...")
    true_count_stats = {}
    
    for shoe_num in range(10):
        if shoe_num % 5 == 0:
            print(f"  Shoe {shoe_num + 1}/10")
            
        shoe = create_deck(1)
        random.shuffle(shoe)
        counter.reset()
        
        # Play through the shoe
        hands_this_shoe = 0
        while len(shoe) >= 10 and hands_this_shoe < 20:  # Limit hands per shoe
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
                    hands_this_shoe += 1
    
    print("Test completed! Creating results...")
    
    # Create results DataFrame
    results = []
    for tc in range(-10, 11):
        if tc in true_count_stats:
            stats = true_count_stats[tc]
            edge = (stats['total_profit'] / stats['total_wagered']) * 100 if stats['total_wagered'] > 0 else 0
            results.append({
                'true_count': tc,
                'frequency': stats['frequency'],
                'edge_percent': round(edge, 4),
                'total_profit': stats['total_profit'],
                'total_wagered': stats['total_wagered']
            })
        else:
            results.append({
                'true_count': tc,
                'frequency': 0,
                'edge_percent': 0,
                'total_profit': 0,
                'total_wagered': 0
            })
    
    df = pd.DataFrame(results)
    
    # Create output directory
    os.makedirs('simulation_results', exist_ok=True)
    
    # Save results
    output_file = 'simulation_results/quick_test_1deck.csv'
    df.to_csv(output_file, index=False)
    
    print(f"Results saved to {output_file}")
    print("\nSample results:")
    print(df[df['frequency'] > 0].head(15).to_string(index=False))
    
    return df

if __name__ == "__main__":
    run_quick_test()