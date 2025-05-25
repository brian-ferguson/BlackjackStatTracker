#!/usr/bin/env python3
"""
Quick test of the bet spreading functionality
"""

from blackjack_game import BlackjackGame
from card_counting import HighLowCounter
from utils import create_deck
import random

def test_bet_spread():
    """Test the bet spreading logic"""
    
    game = BlackjackGame()
    
    print("Testing bet spreading:")
    for tc in range(-5, 11):
        bet = game.get_bet_amount(tc)
        print(f"True Count {tc:+2d}: ${bet}")
    
    print("\nTesting single hand simulation:")
    counter = HighLowCounter()
    shoe = create_deck(1)
    random.shuffle(shoe)
    
    # Test a few hands
    for i in range(5):
        if len(shoe) < 10:
            break
            
        remaining_decks = len(shoe) / 52
        true_count = round(counter.get_true_count_precise(remaining_decks))
        
        print(f"\nHand {i+1}: TC {true_count}, Cards remaining: {len(shoe)}")
        
        profit, bet = game.play_hand(shoe, true_count, counter)
        print(f"  Result: Profit=${profit}, Bet=${bet}")
        
        if bet == 0:
            print(f"  Sat out (TC {true_count} ≤ 0)")

if __name__ == "__main__":
    test_bet_spread()