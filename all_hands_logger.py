#!/usr/bin/env python3
"""
Print ALL hands that are actually played (with bets) in complete detail
"""

import random
from datetime import datetime
from advanced_blackjack_game import AdvancedBlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

def play_detailed_hand(game, shoe, true_count, running_count, remaining_decks, counter, bet_spread, hand_number):
    """Play a single hand with complete detailed logging - only for hands with bets"""
    
    if len(shoe) < 10:
        return 0, 0, False  # Not enough cards
    
    # Calculate bet amount
    bet_amount = game.get_bet_amount(true_count, bet_spread)
    
    if bet_amount == 0:
        # Sit out - burn cards quickly without logging
        cards_to_burn = min(4, len(shoe))
        for i in range(cards_to_burn):
            if shoe:
                card = shoe.pop()
                counter.add_card(card)
        return 0, 0, False  # False = not a played hand
    
    # This is a hand we're actually playing - log everything
    print(f"\n{'='*80}")
    print(f"PLAYED HAND #{hand_number}")
    print(f"{'='*80}")
    print(f"🎯 TRUE COUNT: {true_count:.2f} | RUNNING COUNT: {running_count} | REMAINING DECKS: {remaining_decks:.2f}")
    print(f"💰 BETTING: ${bet_amount}")
    
    # Deal initial cards with detailed logging
    print(f"\n📋 DEALING CARDS:")
    
    # Player first card
    player_card1 = shoe.pop()
    counter.add_card(player_card1)
    print(f"   Player gets: {player_card1} (Running count: {counter.get_running_count()})")
    
    # Dealer up card
    dealer_up_card = shoe.pop()
    counter.add_card(dealer_up_card)
    print(f"   Dealer shows: {dealer_up_card} (Running count: {counter.get_running_count()})")
    
    # Player second card
    player_card2 = shoe.pop()
    counter.add_card(player_card2)
    print(f"   Player gets: {player_card2} (Running count: {counter.get_running_count()})")
    
    # Dealer hole card
    dealer_hole_card = shoe.pop()
    counter.add_card(dealer_hole_card)
    print(f"   Dealer hole: {dealer_hole_card} (hidden) (Running count: {counter.get_running_count()})")
    
    # Initial hands
    player_hand = [player_card1, player_card2]
    dealer_hand = [dealer_up_card, dealer_hole_card]
    
    player_total = game.hand_value(player_hand)
    dealer_total = game.hand_value(dealer_hand)
    
    print(f"\n🃏 STARTING POSITION:")
    print(f"   Player: {player_card1} + {player_card2} = {player_total}")
    print(f"   Dealer: {dealer_up_card} + [?] = ?")
    
    # Check for blackjacks
    player_bj = game.is_blackjack(player_hand)
    dealer_bj = game.is_blackjack(dealer_hand)
    
    if player_bj or dealer_bj:
        print(f"   Dealer hole card revealed: {dealer_hole_card}")
        print(f"   Dealer total: {dealer_total}")
        
        if dealer_bj and player_bj:
            print("🤝 BOTH BLACKJACK - PUSH")
            return 0, bet_amount, True
        elif dealer_bj:
            print("💥 DEALER BLACKJACK - Player loses")
            return -bet_amount, bet_amount, True
        elif player_bj:
            print("🎉 PLAYER BLACKJACK - Pays 3:2!")
            payout = bet_amount * game.rules['blackjack_pays']
            return payout, bet_amount, True
    
    # Play player hand
    print(f"\n👤 PLAYER'S TURN:")
    current_hand = player_hand.copy()
    total_wagered = bet_amount
    actions = []
    
    while game.hand_value(current_hand) < 21:
        current_total = game.hand_value(current_hand)
        can_double = len(current_hand) == 2
        can_split = len(current_hand) == 2 and current_hand[0] == current_hand[1]
        can_surrender = len(current_hand) == 2 and game.rules['surrender_allowed']
        
        decision = game.basic_strategy_decision(
            current_hand, dealer_up_card, can_double, can_split, can_surrender
        )
        
        print(f"   Hand: {' + '.join(current_hand)} = {current_total}")
        print(f"   Decision: {decision.upper()}")
        actions.append(decision.upper())
        
        if decision == 'hit':
            if len(shoe) == 0:
                print("   ❌ No cards left!")
                break
            new_card = shoe.pop()
            current_hand.append(new_card)
            counter.add_card(new_card)
            print(f"   Drew: {new_card} (Running count: {counter.get_running_count()})")
            
        elif decision == 'double':
            if len(shoe) == 0:
                print("   ❌ No cards left!")
                break
            print(f"   💰 DOUBLING DOWN - Total bet: ${bet_amount * 2}")
            new_card = shoe.pop()
            current_hand.append(new_card)
            counter.add_card(new_card)
            total_wagered = bet_amount * 2
            print(f"   Drew: {new_card} (Running count: {counter.get_running_count()})")
            break
            
        elif decision == 'split':
            print(f"   ✂️ SPLITTING (simplified)")
            break
            
        elif decision == 'surrender':
            print(f"   🏳️ SURRENDERING")
            return -bet_amount * 0.5, total_wagered, True
            
        elif decision == 'stand':
            print(f"   ✋ STANDING")
            break
    
    player_final_total = game.hand_value(current_hand)
    print(f"   Final player hand: {' + '.join(current_hand)} = {player_final_total}")
    
    # Check for player bust
    if player_final_total > 21:
        print(f"   💥 PLAYER BUSTS!")
        print(f"   Player loses ${total_wagered}")
        return -total_wagered, total_wagered, True
    
    # Dealer's turn
    print(f"\n🏪 DEALER'S TURN:")
    print(f"   Hole card revealed: {dealer_hole_card}")
    dealer_final_hand = dealer_hand.copy()
    print(f"   Dealer starts: {' + '.join(dealer_final_hand)} = {game.hand_value(dealer_final_hand)}")
    
    while True:
        dealer_total = game.hand_value(dealer_final_hand)
        
        if dealer_total >= 17:
            if dealer_total == 17 and game.is_soft_hand(dealer_final_hand) and game.rules['dealer_hits_soft17']:
                print(f"   Dealer has soft 17 - must hit")
            else:
                print(f"   Dealer stands with {dealer_total}")
                break
        else:
            print(f"   Dealer must hit with {dealer_total}")
        
        if len(shoe) == 0:
            print("   ❌ No cards left!")
            break
        new_card = shoe.pop()
        dealer_final_hand.append(new_card)
        counter.add_card(new_card)
        print(f"   Dealer drew: {new_card} (Running count: {counter.get_running_count()})")
        print(f"   Dealer hand: {' + '.join(dealer_final_hand)} = {game.hand_value(dealer_final_hand)}")
    
    dealer_final_total = game.hand_value(dealer_final_hand)
    
    # Final comparison
    print(f"\n🏁 FINAL RESULT:")
    print(f"   Player: {' + '.join(current_hand)} = {player_final_total}")
    print(f"   Dealer: {' + '.join(dealer_final_hand)} = {dealer_final_total}")
    print(f"   Actions: {' → '.join(actions)}")
    
    # Determine winner
    if dealer_final_total > 21:
        print("   🎉 DEALER BUSTS - Player wins!")
        profit = total_wagered
    elif player_final_total > dealer_final_total:
        print("   🎉 PLAYER WINS!")
        profit = total_wagered
    elif player_final_total < dealer_final_total:
        print("   😞 DEALER WINS")
        profit = -total_wagered
    else:
        print("   🤝 PUSH (Tie)")
        profit = 0
    
    print(f"   💰 RESULT: ${profit:+.2f} (Wagered: ${total_wagered})")
    
    return profit, total_wagered, True

def run_all_hands_simulation():
    """Run 100 hands and show ALL hands that are actually played"""
    
    print("🎰 COMPLETE HAND-BY-HAND SIMULATION")
    print("=" * 80)
    print("Showing EVERY hand that is actually played (with bets)")
    print("Configuration: 4 decks, Hi-Lo counting")
    print("Bet Spread: TC≤0=$0, TC+1=$5, TC+2=$10, TC+3=$15, TC+4=$25, TC+5+=$25")
    print("=" * 80)
    
    # Initialize
    game = AdvancedBlackjackGame()
    bet_spread = {
        'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
    }
    
    # Stats
    total_profit = 0
    total_wagered = 0
    hands_completed = 0
    hands_played = 0
    shoe_number = 1
    
    # Create initial shoe
    shoe = create_deck(4)
    random.shuffle(shoe)
    counter = HighLowCounter()
    
    print(f"🎲 Starting with fresh 4-deck shoe...")
    
    # Play exactly 100 hands
    while hands_completed < 100:
        # Check for new shoe
        if len(shoe) < 10:
            shoe = create_deck(4)
            random.shuffle(shoe)
            counter.reset()
            shoe_number += 1
            print(f"\n🔄 NEW SHOE #{shoe_number} - Reshuffling...")
        
        hands_completed += 1
        remaining_cards = len(shoe)
        remaining_decks = calculate_remaining_decks(remaining_cards)
        running_count = counter.get_running_count()
        true_count = counter.get_true_count_precise(remaining_decks)
        
        # Play hand
        profit, wagered, was_played = play_detailed_hand(
            game, shoe, true_count, running_count, remaining_decks, 
            counter, bet_spread, hands_completed
        )
        
        total_profit += profit
        total_wagered += wagered
        if was_played:
            hands_played += 1
    
    # Final summary
    print(f"\n{'='*80}")
    print("SIMULATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total hands dealt: {hands_completed}")
    print(f"Hands actually played: {hands_played}")
    print(f"Hands sitting out: {hands_completed - hands_played}")
    print(f"Total profit: ${total_profit:.2f}")
    print(f"Total wagered: ${total_wagered:.2f}")
    
    if total_wagered > 0:
        edge = (total_profit / total_wagered) * 100
        avg_bet = total_wagered / hands_played
        print(f"Overall edge: {edge:.4f}%")
        print(f"Average bet: ${avg_bet:.2f}")
    
    print(f"\nAll {hands_played} played hands shown above in complete detail!")

if __name__ == "__main__":
    run_all_hands_simulation()