#!/usr/bin/env python3
"""
Detailed narrative simulation showing step-by-step action for each of 100 hands
"""

import random
from datetime import datetime
from advanced_blackjack_game import AdvancedBlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

def play_narrative_hand(game, shoe, true_count, running_count, remaining_decks, counter, bet_spread, hand_number):
    """Play a single hand with detailed narrative logging"""
    
    print(f"\n{'='*60}")
    print(f"HAND #{hand_number}")
    print(f"{'='*60}")
    print(f"Running Count: {running_count} | True Count: {true_count:.2f} | Remaining Decks: {remaining_decks:.2f}")
    
    if len(shoe) < 10:
        print("❌ Not enough cards in shoe for a complete hand")
        return 0, 0
    
    # Calculate bet amount
    bet_amount = game.get_bet_amount(true_count, bet_spread)
    print(f"💰 Bet Decision: TC {true_count:.2f} → ${bet_amount}")
    
    if bet_amount == 0:
        # Quick sit-out without details to focus on played hands
        cards_to_burn = min(4, len(shoe))
        for i in range(cards_to_burn):
            if shoe:
                card = shoe.pop()
                counter.add_card(card)
        return 0, 0
    
    print(f"🎯 PLAYING HAND - Betting ${bet_amount}")
    
    # Deal initial cards
    print("\n📋 DEALING INITIAL CARDS:")
    
    # Player gets first card
    player_card1 = shoe.pop()
    counter.add_card(player_card1)
    print(f"   Player card 1: {player_card1}")
    print(f"   Running count after {player_card1}: {counter.get_running_count()}")
    
    # Dealer gets up card
    dealer_up_card = shoe.pop()
    counter.add_card(dealer_up_card)
    print(f"   Dealer up card: {dealer_up_card}")
    print(f"   Running count after {dealer_up_card}: {counter.get_running_count()}")
    
    # Player gets second card
    player_card2 = shoe.pop()
    counter.add_card(player_card2)
    print(f"   Player card 2: {player_card2}")
    print(f"   Running count after {player_card2}: {counter.get_running_count()}")
    
    # Dealer gets hole card
    dealer_hole_card = shoe.pop()
    counter.add_card(dealer_hole_card)
    print(f"   Dealer hole card: {dealer_hole_card} (hidden)")
    print(f"   Running count after hole card: {counter.get_running_count()}")
    
    # Initial hands
    player_hand = [player_card1, player_card2]
    dealer_hand = [dealer_up_card, dealer_hole_card]
    
    player_total = game.hand_value(player_hand)
    dealer_total = game.hand_value(dealer_hand)
    
    print(f"\n🃏 INITIAL HANDS:")
    print(f"   Player: {' + '.join(player_hand)} = {player_total}")
    print(f"   Dealer: {dealer_up_card} + ?? = ?")
    
    # Check for blackjacks
    player_bj = game.is_blackjack(player_hand)
    dealer_bj = game.is_blackjack(dealer_hand)
    
    if player_bj:
        print("🎉 PLAYER BLACKJACK!")
    if dealer_bj:
        print("💥 DEALER BLACKJACK!")
    
    if dealer_bj and player_bj:
        print("🤝 PUSH - Both have blackjack")
        print(f"   Dealer reveals: {' + '.join(dealer_hand)} = {dealer_total}")
        return 0, bet_amount
        
    elif dealer_bj:
        print("😞 DEALER WINS with blackjack")
        print(f"   Dealer reveals: {' + '.join(dealer_hand)} = {dealer_total}")
        return -bet_amount, bet_amount
        
    elif player_bj:
        print(f"🎊 PLAYER WINS with blackjack! Pays 3:2")
        payout = bet_amount * game.rules['blackjack_pays']
        return payout, bet_amount
    
    # Play player hand
    print(f"\n👤 PLAYER'S TURN:")
    current_hand = player_hand.copy()
    total_wagered = bet_amount
    actions_taken = []
    
    while game.hand_value(current_hand) < 21:
        current_total = game.hand_value(current_hand)
        can_double = len(current_hand) == 2
        can_split = len(current_hand) == 2 and current_hand[0] == current_hand[1]
        can_surrender = len(current_hand) == 2 and game.rules['surrender_allowed']
        
        print(f"   Current hand: {' + '.join(current_hand)} = {current_total}")
        
        decision = game.basic_strategy_decision(
            current_hand, dealer_up_card, can_double, can_split, can_surrender
        )
        
        print(f"   Basic Strategy Decision: {decision.upper()}")
        actions_taken.append(decision.upper())
        
        if decision == 'hit':
            if len(shoe) == 0:
                print("   ❌ No more cards in shoe!")
                break
            new_card = shoe.pop()
            current_hand.append(new_card)
            counter.add_card(new_card)
            print(f"   🎴 Drew: {new_card}")
            print(f"   Running count after {new_card}: {counter.get_running_count()}")
            new_total = game.hand_value(current_hand)
            print(f"   New hand: {' + '.join(current_hand)} = {new_total}")
            
        elif decision == 'double':
            if len(shoe) == 0:
                print("   ❌ No more cards in shoe!")
                break
            print(f"   💰 DOUBLING DOWN - bet increases to ${bet_amount * 2}")
            new_card = shoe.pop()
            current_hand.append(new_card)
            counter.add_card(new_card)
            total_wagered = bet_amount * 2
            print(f"   🎴 Drew: {new_card}")
            print(f"   Running count after {new_card}: {counter.get_running_count()}")
            new_total = game.hand_value(current_hand)
            print(f"   Final hand: {' + '.join(current_hand)} = {new_total}")
            break
            
        elif decision == 'split':
            print(f"   ✂️ SPLITTING (simplified for logging)")
            actions_taken.append('SPLIT_SIMPLIFIED')
            break
            
        elif decision == 'surrender':
            print(f"   🏳️ SURRENDERING - lose half bet (${bet_amount * 0.5})")
            return -bet_amount * 0.5, total_wagered
            
        elif decision == 'stand':
            print(f"   ✋ STANDING with {current_total}")
            break
    
    player_final_total = game.hand_value(current_hand)
    
    # Check for player bust
    if player_final_total > 21:
        print(f"   💥 PLAYER BUSTS with {player_final_total}")
        print(f"   Actions taken: {' → '.join(actions_taken)}")
        return -total_wagered, total_wagered
    
    # Dealer's turn
    print(f"\n🏪 DEALER'S TURN:")
    print(f"   Dealer reveals hole card: {dealer_hole_card}")
    dealer_final_hand = dealer_hand.copy()
    print(f"   Dealer hand: {' + '.join(dealer_final_hand)} = {game.hand_value(dealer_final_hand)}")
    
    while True:
        dealer_total = game.hand_value(dealer_final_hand)
        
        # Dealer stands on hard 17 or higher
        if dealer_total >= 17:
            # Check soft 17 rule
            if dealer_total == 17 and game.is_soft_hand(dealer_final_hand) and game.rules['dealer_hits_soft17']:
                print(f"   Dealer has soft 17, must hit (H17 rule)")
            else:
                print(f"   🏪 DEALER STANDS with {dealer_total}")
                break
        else:
            print(f"   Dealer must hit with {dealer_total}")
        
        # Dealer hits
        if len(shoe) == 0:
            print("   ❌ No more cards in shoe!")
            break
        new_card = shoe.pop()
        dealer_final_hand.append(new_card)
        counter.add_card(new_card)
        print(f"   🎴 Dealer drew: {new_card}")
        print(f"   Running count after {new_card}: {counter.get_running_count()}")
        new_total = game.hand_value(dealer_final_hand)
        print(f"   Dealer hand: {' + '.join(dealer_final_hand)} = {new_total}")
    
    dealer_final_total = game.hand_value(dealer_final_hand)
    
    # Final comparison
    print(f"\n🏁 FINAL COMPARISON:")
    print(f"   Player: {' + '.join(current_hand)} = {player_final_total}")
    print(f"   Dealer: {' + '.join(dealer_final_hand)} = {dealer_final_total}")
    print(f"   Actions taken: {' → '.join(actions_taken)}")
    
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
        print("   🤝 PUSH (tie)")
        profit = 0
    
    print(f"   💰 Result: ${profit:+.2f} (wagered ${total_wagered})")
    
    return profit, total_wagered

def run_narrative_simulation():
    """Run exactly 100 hands with detailed narrative logging"""
    
    print("🔍 DETAILED NARRATIVE SIMULATION")
    print("=" * 60)
    print("Playing exactly 100 hands with step-by-step description")
    print("Configuration: 4 decks")
    print("Bet Spread: TC≤0=$0, TC+1=$5, TC+2=$10, TC+3=$15, TC+4=$25, TC+5+=$25")
    print("=" * 60)
    
    # Initialize components
    game = AdvancedBlackjackGame()
    
    bet_spread = {
        'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
    }
    
    # Statistics tracking
    total_profit = 0
    total_wagered = 0
    hands_played = 0
    hands_with_bets = 0
    shoe_number = 1
    
    # Create initial shoe
    shoe = create_deck(4)  # 4 decks
    random.shuffle(shoe)
    counter = HighLowCounter()
    
    print(f"🎰 Starting with fresh 4-deck shoe (208 cards)")
    
    # Play exactly 100 hands
    while hands_played < 100:
        # Check if we need a new shoe
        if len(shoe) < 10:
            shoe = create_deck(4)
            random.shuffle(shoe)
            counter.reset()
            shoe_number += 1
            print(f"\n🔄 NEW SHOE #{shoe_number} - Reshuffling 4 decks (208 cards)")
        
        hands_played += 1
        remaining_cards = len(shoe)
        remaining_decks = calculate_remaining_decks(remaining_cards)
        running_count = counter.get_running_count()
        true_count = counter.get_true_count_precise(remaining_decks)
        
        # Play hand with detailed narrative
        profit, wagered = play_narrative_hand(
            game, shoe, true_count, running_count, remaining_decks, 
            counter, bet_spread, hands_played
        )
        
        total_profit += profit
        total_wagered += wagered
        if wagered > 0:
            hands_with_bets += 1
    
    # Final summary
    print(f"\n{'='*80}")
    print("SIMULATION COMPLETED!")
    print(f"{'='*80}")
    print(f"Total hands: {hands_played}")
    print(f"Hands with bets: {hands_with_bets}")
    print(f"Hands sitting out: {hands_played - hands_with_bets}")
    print(f"Total profit: ${total_profit:.2f}")
    print(f"Total wagered: ${total_wagered:.2f}")
    
    if total_wagered > 0:
        overall_edge = (total_profit / total_wagered) * 100
        avg_bet = total_wagered / hands_with_bets
        print(f"Overall edge: {overall_edge:.4f}%")
        print(f"Average bet size: ${avg_bet:.2f}")
    else:
        print("No bets placed during simulation")

if __name__ == "__main__":
    run_narrative_simulation()