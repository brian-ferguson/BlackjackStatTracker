#!/usr/bin/env python3
"""
Comprehensive audit of blackjack game logic to identify why edges are too low
"""

from advanced_blackjack_game import AdvancedBlackjackGame
from card_counting import HighLowCounter
from utils import create_deck
import random

def test_card_counting():
    """Test Hi-Lo card counting accuracy"""
    print("🔍 TESTING CARD COUNTING:")
    print("-" * 40)
    
    counter = HighLowCounter()
    
    # Test known cards
    test_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    expected_values = [1, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, -1, -1]
    
    print("Card | Expected | Actual | ✓")
    print("-" * 30)
    
    all_correct = True
    for card, expected in zip(test_cards, expected_values):
        counter.reset()
        counter.add_card(card)
        actual = counter.get_running_count()
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_correct = False
        print(f"{card:4s} | {expected:8d} | {actual:6d} | {status}")
    
    print(f"\nCard counting: {'✅ PASS' if all_correct else '❌ FAIL'}")
    return all_correct

def test_hand_values():
    """Test hand value calculations"""
    print("\n🔍 TESTING HAND VALUE CALCULATIONS:")
    print("-" * 40)
    
    game = AdvancedBlackjackGame()
    
    test_hands = [
        (['A', 'K'], 21, "Blackjack"),
        (['A', '6'], 17, "Soft 17"),
        (['A', 'A'], 12, "Pair of Aces"),
        (['10', '6'], 16, "Hard 16"),
        (['A', '5', '5'], 21, "A-5-5"),
        (['A', 'A', '9'], 21, "A-A-9"),
        (['A', 'A', 'A', '8'], 21, "Four Aces + 8"),
        (['K', 'Q'], 20, "Face cards"),
    ]
    
    all_correct = True
    print("Hand      | Expected | Actual | ✓")
    print("-" * 35)
    
    for hand, expected, description in test_hands:
        actual = game.hand_value(hand)
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_correct = False
        hand_str = "-".join(hand)
        print(f"{hand_str:9s} | {expected:8d} | {actual:6d} | {status}")
    
    print(f"\nHand values: {'✅ PASS' if all_correct else '❌ FAIL'}")
    return all_correct

def test_basic_strategy():
    """Test basic strategy decisions"""
    print("\n🔍 TESTING BASIC STRATEGY:")
    print("-" * 40)
    
    game = AdvancedBlackjackGame()
    
    # Test key basic strategy decisions
    test_cases = [
        (['5', '5'], '6', 'double', "Double 10 vs 6"),
        (['A', 'A'], '7', 'split', "Split Aces vs 7"),
        (['8', '8'], '10', 'split', "Split 8s vs 10"),
        (['10', '6'], '10', 'hit', "Hit 16 vs 10"),
        (['10', '7'], '6', 'stand', "Stand 17 vs 6"),
        (['A', '6'], '6', 'double', "Double soft 17 vs 6"),
        (['9', '2'], '2', 'double', "Double 11 vs 2"),
        (['10', '2'], 'A', 'hit', "Hit 12 vs A"),
    ]
    
    all_correct = True
    print("Hand    | Dealer | Expected | Actual   | ✓")
    print("-" * 45)
    
    for player_hand, dealer_card, expected, description in test_cases:
        actual = game.basic_strategy_decision(
            player_hand, dealer_card, 
            can_double=True, 
            can_split=(player_hand[0] == player_hand[1])
        )
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_correct = False
        hand_str = "-".join(player_hand)
        print(f"{hand_str:7s} | {dealer_card:6s} | {expected:8s} | {actual:8s} | {status}")
    
    print(f"\nBasic strategy: {'✅ PASS' if all_correct else '❌ FAIL'}")
    return all_correct

def test_bet_spread():
    """Test bet spread implementation"""
    print("\n🔍 TESTING BET SPREAD:")
    print("-" * 40)
    
    game = AdvancedBlackjackGame()
    
    bet_spread = {
        'tc_neg': 0,
        'tc_1': 5,
        'tc_2': 10,
        'tc_3': 15,
        'tc_4': 25,
        'tc_5plus': 25
    }
    
    test_counts = [
        (-2, 0, "Negative count"),
        (0, 0, "Zero count"),
        (1, 5, "TC +1"),
        (2, 10, "TC +2"),
        (3, 15, "TC +3"),
        (4, 25, "TC +4"),
        (5, 25, "TC +5"),
        (8, 25, "TC +8"),
    ]
    
    all_correct = True
    print("True Count | Expected | Actual | ✓")
    print("-" * 35)
    
    for tc, expected, description in test_counts:
        actual = game.get_bet_amount(tc, bet_spread)
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_correct = False
        print(f"{tc:10d} | {expected:8d} | {actual:6d} | {status}")
    
    print(f"\nBet spread: {'✅ PASS' if all_correct else '❌ FAIL'}")
    return all_correct

def test_dealer_logic():
    """Test dealer playing logic"""
    print("\n🔍 TESTING DEALER LOGIC:")
    print("-" * 40)
    
    game = AdvancedBlackjackGame()
    counter = HighLowCounter()
    
    # Create test scenarios
    test_cases = [
        (['K', '6'], "Should hit 16"),
        (['10', '7'], "Should stand on 17"),
        (['A', '6'], "Should hit soft 17 (if H17 rule)"),
        (['A', '6', 'K'], "Should stand on hard 17"),
        (['5', 'A'], "Should hit soft 16"),
    ]
    
    print("Dealer Hand | Action Taken")
    print("-" * 30)
    
    for initial_hand, description in test_cases:
        # Create a fresh shoe for each test
        shoe = create_deck(1)
        random.shuffle(shoe)
        
        # Remove initial cards from shoe
        for card in initial_hand:
            if card in shoe:
                shoe.remove(card)
        
        dealer_hand = initial_hand.copy()
        initial_value = game.hand_value(dealer_hand)
        
        game.play_dealer_hand(dealer_hand, shoe, counter)
        final_value = game.hand_value(dealer_hand)
        
        action = "hit" if len(dealer_hand) > len(initial_hand) else "stand"
        hand_str = "-".join(initial_hand)
        print(f"{hand_str:11s} | {action} ({initial_value}→{final_value})")
    
    print("Dealer logic: ✅ Manual review needed")

def test_payouts():
    """Test payout calculations"""
    print("\n🔍 TESTING PAYOUTS:")
    print("-" * 40)
    
    game = AdvancedBlackjackGame()
    
    # Test scenarios with known outcomes
    print("Scenario | Expected | Details")
    print("-" * 40)
    print("Blackjack| 1.5x bet | Should pay 3:2")
    print("Win      | 1.0x bet | Regular win")
    print("Push     | 0.0x bet | Tie")
    print("Loss     | -1.0x bet| Player loses")
    print("Double W | 2.0x bet | Double down win")
    
    # Verify blackjack payout setting
    payout = game.rules['blackjack_pays']
    print(f"\nBlackjack payout setting: {payout} {'✅ CORRECT (3:2)' if payout == 1.5 else '❌ WRONG'}")

def test_full_hand():
    """Test a complete hand with detailed logging"""
    print("\n🔍 TESTING COMPLETE HAND:")
    print("-" * 40)
    
    game = AdvancedBlackjackGame()
    counter = HighLowCounter()
    
    bet_spread = {
        'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
    }
    
    # Create a controlled deck
    shoe = ['K', 'A', '6', '10', '5', '3', '7', '8', '9', '2'] * 4
    random.shuffle(shoe)
    
    print("Playing one complete hand with detailed tracking...")
    
    initial_count = counter.get_running_count()
    true_count = 2.0  # Simulate positive count
    
    print(f"Initial running count: {initial_count}")
    print(f"True count: {true_count}")
    
    bet_amount = game.get_bet_amount(true_count, bet_spread)
    print(f"Bet amount for TC +{true_count}: ${bet_amount}")
    
    if len(shoe) >= 10:
        result, wagered = game.play_hand(shoe, true_count, counter, bet_spread)
        print(f"Hand result: Profit=${result}, Wagered=${wagered}")
        print(f"Final running count: {counter.get_running_count()}")
    
    print("Complete hand: ✅ Manual review of output")

def run_full_audit():
    """Run complete game logic audit"""
    print("🔍 BLACKJACK GAME LOGIC AUDIT")
    print("=" * 50)
    
    tests = [
        test_card_counting(),
        test_hand_values(),
        test_basic_strategy(),
        test_bet_spread(),
    ]
    
    test_dealer_logic()
    test_payouts()
    test_full_hand()
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 50)
    print(f"AUDIT SUMMARY: {passed}/{total} automated tests passed")
    
    if passed == total:
        print("✅ All automated tests PASSED - Game logic appears sound")
        print("💡 Low edges may be due to:")
        print("   - Insufficient penetration")
        print("   - Sample size variations")
        print("   - Table rules settings")
    else:
        print("❌ Some tests FAILED - Issues found in game logic")
        print("🔧 Fix failing components before running simulations")

if __name__ == "__main__":
    run_full_audit()