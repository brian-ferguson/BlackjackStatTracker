#!/usr/bin/env python3
"""
Detailed blackjack simulation with comprehensive logging of all player actions,
cards dealt, and outcomes for analysis
"""

import csv
import random
from datetime import datetime
from advanced_blackjack_game import AdvancedBlackjackGame
from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

class DetailedGameLogger:
    """Logs every aspect of blackjack hands for detailed analysis"""
    
    def __init__(self):
        self.log_data = []
        self.hand_counter = 0
        
    def log_hand(self, hand_data):
        """Log detailed information about a single hand"""
        self.hand_counter += 1
        hand_data['hand_number'] = self.hand_counter
        self.log_data.append(hand_data)
    
    def save_to_csv(self, filename):
        """Save all logged data to CSV file"""
        if not self.log_data:
            print("No data to save")
            return
            
        fieldnames = [
            'hand_number', 'shoe_number', 'true_count', 'running_count', 'remaining_decks',
            'bet_amount', 'player_cards', 'dealer_up_card', 'dealer_hole_card',
            'player_initial_total', 'dealer_initial_total', 'player_blackjack', 'dealer_blackjack',
            'player_actions', 'player_final_cards', 'dealer_final_cards',
            'player_final_total', 'dealer_final_total', 'outcome', 'profit', 'total_wagered'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.log_data)
        
        print(f"Detailed log saved to {filename}")

def play_logged_hand(game, shoe, true_count, running_count, remaining_decks, counter, bet_spread, logger, shoe_number):
    """Play a single hand with detailed logging"""
    
    if len(shoe) < 10:
        return 0, 0
    
    # Calculate bet amount
    bet_amount = game.get_bet_amount(true_count, bet_spread)
    if bet_amount == 0:
        # Sit out but burn cards
        cards_to_burn = min(4, len(shoe))
        burned_cards = []
        for _ in range(cards_to_burn):
            if shoe:
                card = shoe.pop()
                counter.add_card(card)
                burned_cards.append(card)
        
        # Log sit-out decision
        logger.log_hand({
            'shoe_number': shoe_number,
            'true_count': round(true_count, 2),
            'running_count': running_count,
            'remaining_decks': round(remaining_decks, 2),
            'bet_amount': 0,
            'player_cards': 'SIT_OUT',
            'dealer_up_card': 'N/A',
            'dealer_hole_card': 'N/A',
            'player_initial_total': 0,
            'dealer_initial_total': 0,
            'player_blackjack': False,
            'dealer_blackjack': False,
            'player_actions': 'SIT_OUT',
            'player_final_cards': f'BURNED: {"-".join(burned_cards)}',
            'dealer_final_cards': 'N/A',
            'player_final_total': 0,
            'dealer_final_total': 0,
            'outcome': 'SIT_OUT',
            'profit': 0,
            'total_wagered': 0
        })
        return 0, 0
    
    # Deal initial cards
    player_cards = []
    dealer_cards = []
    
    # Deal player cards
    player_cards.append(shoe.pop())
    counter.add_card(player_cards[-1])
    player_cards.append(shoe.pop())
    counter.add_card(player_cards[-1])
    
    # Deal dealer cards
    dealer_up_card = shoe.pop()
    dealer_cards.append(dealer_up_card)
    counter.add_card(dealer_up_card)
    
    dealer_hole_card = shoe.pop()
    dealer_cards.append(dealer_hole_card)
    counter.add_card(dealer_hole_card)
    
    # Calculate initial totals
    player_initial_total = game.hand_value(player_cards)
    dealer_initial_total = game.hand_value(dealer_cards)
    
    # Check for blackjacks
    player_bj = game.is_blackjack(player_cards)
    dealer_bj = game.is_blackjack(dealer_cards)
    
    # Initialize hand log data
    hand_data = {
        'shoe_number': shoe_number,
        'true_count': round(true_count, 2),
        'running_count': running_count,
        'remaining_decks': round(remaining_decks, 2),
        'bet_amount': bet_amount,
        'player_cards': '-'.join(player_cards),
        'dealer_up_card': dealer_up_card,
        'dealer_hole_card': dealer_hole_card,
        'player_initial_total': player_initial_total,
        'dealer_initial_total': dealer_initial_total,
        'player_blackjack': player_bj,
        'dealer_blackjack': dealer_bj,
        'player_actions': [],
        'player_final_cards': '',
        'dealer_final_cards': '',
        'player_final_total': 0,
        'dealer_final_total': 0,
        'outcome': '',
        'profit': 0,
        'total_wagered': bet_amount
    }
    
    # Handle blackjacks
    if dealer_bj and player_bj:
        hand_data['player_actions'] = 'PUSH_BLACKJACK'
        hand_data['player_final_cards'] = '-'.join(player_cards)
        hand_data['dealer_final_cards'] = '-'.join(dealer_cards)
        hand_data['player_final_total'] = player_initial_total
        hand_data['dealer_final_total'] = dealer_initial_total
        hand_data['outcome'] = 'PUSH'
        hand_data['profit'] = 0
        logger.log_hand(hand_data)
        return 0, bet_amount
        
    elif dealer_bj:
        hand_data['player_actions'] = 'LOSE_TO_DEALER_BJ'
        hand_data['player_final_cards'] = '-'.join(player_cards)
        hand_data['dealer_final_cards'] = '-'.join(dealer_cards)
        hand_data['player_final_total'] = player_initial_total
        hand_data['dealer_final_total'] = dealer_initial_total
        hand_data['outcome'] = 'DEALER_BLACKJACK'
        hand_data['profit'] = -bet_amount
        logger.log_hand(hand_data)
        return -bet_amount, bet_amount
        
    elif player_bj:
        hand_data['player_actions'] = 'PLAYER_BLACKJACK'
        hand_data['player_final_cards'] = '-'.join(player_cards)
        hand_data['dealer_final_cards'] = '-'.join(dealer_cards)
        hand_data['player_final_total'] = player_initial_total
        hand_data['dealer_final_total'] = dealer_initial_total
        hand_data['outcome'] = 'PLAYER_BLACKJACK'
        hand_data['profit'] = bet_amount * game.rules['blackjack_pays']
        logger.log_hand(hand_data)
        return bet_amount * game.rules['blackjack_pays'], bet_amount
    
    # Play player hand with basic strategy
    actions = []
    current_hand = player_cards.copy()
    total_wagered = bet_amount
    
    while game.hand_value(current_hand) < 21:
        can_double = len(current_hand) == 2
        can_split = len(current_hand) == 2 and current_hand[0] == current_hand[1]
        can_surrender = len(current_hand) == 2 and game.rules['surrender_allowed']
        
        decision = game.basic_strategy_decision(
            current_hand, dealer_up_card, can_double, can_split, can_surrender
        )
        
        actions.append(decision.upper())
        
        if decision == 'hit':
            if len(shoe) == 0:
                break
            new_card = shoe.pop()
            current_hand.append(new_card)
            counter.add_card(new_card)
            
        elif decision == 'double':
            if len(shoe) == 0:
                break
            new_card = shoe.pop()
            current_hand.append(new_card)
            counter.add_card(new_card)
            total_wagered = bet_amount * 2
            break
            
        elif decision == 'split':
            # For logging purposes, we'll note the split but play simplified
            actions.append('SPLIT_SIMPLIFIED')
            break
            
        elif decision == 'surrender':
            hand_data['player_actions'] = 'SURRENDER'
            hand_data['player_final_cards'] = '-'.join(current_hand)
            hand_data['dealer_final_cards'] = '-'.join(dealer_cards)
            hand_data['player_final_total'] = game.hand_value(current_hand)
            hand_data['dealer_final_total'] = dealer_initial_total
            hand_data['outcome'] = 'SURRENDER'
            hand_data['profit'] = -bet_amount * 0.5
            hand_data['total_wagered'] = total_wagered
            logger.log_hand(hand_data)
            return -bet_amount * 0.5, total_wagered
            
        elif decision == 'stand':
            break
    
    player_final_total = game.hand_value(current_hand)
    
    # Player busted
    if player_final_total > 21:
        hand_data['player_actions'] = '-'.join(actions)
        hand_data['player_final_cards'] = '-'.join(current_hand)
        hand_data['dealer_final_cards'] = '-'.join(dealer_cards)
        hand_data['player_final_total'] = player_final_total
        hand_data['dealer_final_total'] = dealer_initial_total
        hand_data['outcome'] = 'PLAYER_BUST'
        hand_data['profit'] = -total_wagered
        hand_data['total_wagered'] = total_wagered
        logger.log_hand(hand_data)
        return -total_wagered, total_wagered
    
    # Play dealer hand
    dealer_final_cards = dealer_cards.copy()
    game.play_dealer_hand(dealer_final_cards, shoe, counter)
    dealer_final_total = game.hand_value(dealer_final_cards)
    
    # Determine outcome
    if dealer_final_total > 21:
        outcome = 'DEALER_BUST'
        profit = total_wagered
    elif player_final_total > dealer_final_total:
        outcome = 'PLAYER_WIN'
        profit = total_wagered
    elif player_final_total < dealer_final_total:
        outcome = 'DEALER_WIN'
        profit = -total_wagered
    else:
        outcome = 'PUSH'
        profit = 0
    
    # Complete hand data
    hand_data['player_actions'] = '-'.join(actions)
    hand_data['player_final_cards'] = '-'.join(current_hand)
    hand_data['dealer_final_cards'] = '-'.join(dealer_final_cards)
    hand_data['player_final_total'] = player_final_total
    hand_data['dealer_final_total'] = dealer_final_total
    hand_data['outcome'] = outcome
    hand_data['profit'] = profit
    hand_data['total_wagered'] = total_wagered
    
    logger.log_hand(hand_data)
    return profit, total_wagered

def run_detailed_simulation():
    """Run exactly 100 hands with detailed logging"""
    
    print("🔍 RUNNING DETAILED SIMULATION WITH LOGGING")
    print("=" * 50)
    print("Configuration: Exactly 100 hands, 4 decks")
    print("Bet Spread: TC≤0=$0, TC+1=$5, TC+2=$10, TC+3=$15, TC+4=$25, TC+5+=$25")
    print()
    
    # Initialize components
    game = AdvancedBlackjackGame()
    logger = DetailedGameLogger()
    
    bet_spread = {
        'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
    }
    
    # Statistics tracking
    total_profit = 0
    total_wagered = 0
    hands_played = 0
    shoe_number = 1
    
    # Create initial shoe
    shoe = create_deck(4)  # 4 decks
    random.shuffle(shoe)
    counter = HighLowCounter()
    
    print("Starting 100-hand simulation...")
    print("Hand | TC   | RC | Bet | Player Cards | Dealer Up | Action | Outcome | Profit")
    print("-" * 80)
    
    # Play exactly 100 hands
    while hands_played < 100:
        # Check if we need a new shoe
        if len(shoe) < 10:
            shoe = create_deck(4)
            random.shuffle(shoe)
            counter.reset()
            shoe_number += 1
            print(f"[NEW SHOE #{shoe_number}]")
        
        remaining_cards = len(shoe)
        remaining_decks = calculate_remaining_decks(remaining_cards)
        running_count = counter.get_running_count()
        true_count = counter.get_true_count_precise(remaining_decks)
        
        # Play hand with detailed logging
        profit, wagered = play_logged_hand(
            game, shoe, true_count, running_count, remaining_decks, 
            counter, bet_spread, logger, shoe_number
        )
        
        hands_played += 1
        total_profit += profit
        total_wagered += wagered
        
        # Get the last logged hand for summary display
        if logger.log_data:
            last_hand = logger.log_data[-1]
            print(f"{hands_played:4d} | {last_hand['true_count']:4.1f} | {last_hand['running_count']:2d} | ${last_hand['bet_amount']:2d} | {last_hand['player_cards']:12s} | {last_hand['dealer_up_card']:9s} | {last_hand['player_actions']:6s} | {last_hand['outcome']:11s} | ${last_hand['profit']:6.2f}")
    
    # Calculate final statistics
    hands_with_bets = sum(1 for hand in logger.log_data if hand['bet_amount'] > 0)
    overall_edge = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
    
    print("\n" + "=" * 80)
    print("100-HAND SIMULATION COMPLETED!")
    print("=" * 80)
    print(f"Total hands played: {hands_played}")
    print(f"Hands with bets: {hands_with_bets}")
    print(f"Hands sitting out: {hands_played - hands_with_bets}")
    print(f"Total profit: ${total_profit:.2f}")
    print(f"Total wagered: ${total_wagered:.2f}")
    print(f"Overall edge: {overall_edge:.4f}%")
    print(f"Average bet size: ${total_wagered/hands_with_bets:.2f}" if hands_with_bets > 0 else "No bets placed")
    
    # Save detailed log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"detailed_100hands_log_{timestamp}.csv"
    logger.save_to_csv(filename)
    
    print(f"\n📊 Detailed log saved to: {filename}")
    print("\nThe CSV log includes complete details for all 100 hands:")
    print("- Every card dealt to player and dealer")
    print("- All player decisions (hit, stand, double, split, surrender)")
    print("- True count and running count for each hand")
    print("- Final outcomes and profit/loss")
    print("- Bet amounts and reasoning")
    
    return filename

if __name__ == "__main__":
    run_detailed_simulation()