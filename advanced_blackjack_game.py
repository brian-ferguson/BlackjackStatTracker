#!/usr/bin/env python3
"""
Advanced Blackjack game engine with complete basic strategy implementation
Including splitting, doubling, surrender, and configurable table rules
"""

import random
from copy import deepcopy

class AdvancedBlackjackGame:
    """Complete blackjack game engine with all basic strategy options"""
    
    def __init__(self, table_rules=None):
        """Initialize with configurable table rules"""
        self.base_bet = 5
        
        # Default table rules (favorable to player)
        self.rules = {
            'dealer_hits_soft17': False,  # Dealer stands on soft 17 (player favorable)
            'double_after_split': True,
            'split_aces': True,
            'resplit_aces': False,
            'surrender_allowed': True,   # Allow surrender (player favorable)
            'max_splits': 3,
            'blackjack_pays': 1.5  # 3:2 payout
        }
        
        # Update with custom rules if provided
        if table_rules:
            self.rules.update(table_rules)
    
    def card_value(self, card):
        """Get numeric value of a card for blackjack"""
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 11  # Will be adjusted in hand_value if needed
        else:
            return int(card)
    
    def hand_value(self, hand):
        """Calculate best hand value, handling aces optimally"""
        if not hand:
            return 0
        
        total = 0
        aces = 0
        
        for card in hand:
            if card == 'A':
                aces += 1
                total += 11
            else:
                total += self.card_value(card)
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10  # Convert ace from 11 to 1
            aces -= 1
        
        return total
    
    def is_soft_hand(self, hand):
        """Check if hand is soft (contains ace counted as 11)"""
        if 'A' not in hand:
            return False
        
        # Check if we can count an ace as 11 without busting
        total_hard = sum(self.card_value(card) if card != 'A' else 1 for card in hand)
        return total_hard + 11 <= 21
    
    def is_blackjack(self, hand):
        """Check if hand is blackjack (21 with 2 cards)"""
        return len(hand) == 2 and self.hand_value(hand) == 21
    
    def can_split(self, hand):
        """Check if hand can be split"""
        if len(hand) != 2:
            return False
        
        # Check if both cards have same value
        card1, card2 = hand[0], hand[1]
        value1 = 10 if card1 in ['10', 'J', 'Q', 'K'] else self.card_value(card1)
        value2 = 10 if card2 in ['10', 'J', 'Q', 'K'] else self.card_value(card2)
        
        if value1 != value2:
            return False
        
        # Check ace splitting rules
        if card1 == 'A' and card2 == 'A':
            return self.rules['split_aces']
        
        return True
    
    def basic_strategy_decision(self, player_hand, dealer_up_card, can_double=True, can_split=False, can_surrender=False):
        """Complete basic strategy decision including surrender"""
        player_total = self.hand_value(player_hand)
        dealer_value = self.card_value(dealer_up_card)
        
        # Surrender decision (early surrender)
        if can_surrender and self.rules['surrender_allowed'] and len(player_hand) == 2:
            if player_total == 16 and dealer_value in [9, 10, 11]:
                return 'surrender'
            elif player_total == 15 and dealer_value == 10:
                return 'surrender'
        
        # Handle pairs first
        if can_split and self.can_split(player_hand):
            pair_card = player_hand[0]
            
            if pair_card == 'A':
                return 'split'  # Always split aces if allowed
            elif pair_card == '8':
                return 'split'  # Always split 8s
            elif pair_card in ['2', '3']:
                return 'split' if dealer_value in [2, 3, 4, 5, 6, 7] else 'hit'
            elif pair_card == '4':
                return 'hit'  # Never split 4s
            elif pair_card == '5':
                # Treat as hard 10
                if can_double and dealer_value <= 9:
                    return 'double'
                else:
                    return 'hit'
            elif pair_card == '6':
                return 'split' if dealer_value in [2, 3, 4, 5, 6] else 'hit'
            elif pair_card == '7':
                return 'split' if dealer_value in [2, 3, 4, 5, 6, 7] else 'hit'
            elif pair_card == '9':
                if dealer_value in [7, 10, 11]:
                    return 'stand'
                else:
                    return 'split'
            elif pair_card in ['10', 'J', 'Q', 'K']:
                return 'stand'  # Never split 10s
        
        # Handle soft hands (with ace counted as 11)
        if self.is_soft_hand(player_hand):
            soft_value = player_total - 11  # The non-ace part
            
            if soft_value <= 2:  # A,A or A,2 (soft 13)
                if dealer_value in [5, 6] and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif soft_value == 3:  # A,3 (soft 14)
                if dealer_value in [5, 6] and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif soft_value == 4:  # A,4 (soft 15)
                if dealer_value in [4, 5, 6] and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif soft_value == 5:  # A,5 (soft 16)
                if dealer_value in [4, 5, 6] and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif soft_value == 6:  # A,6 (soft 17)
                if dealer_value in [3, 4, 5, 6] and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif soft_value == 7:  # A,7 (soft 18)
                if dealer_value in [3, 4, 5, 6] and can_double:
                    return 'double'
                elif dealer_value in [2, 7, 8]:
                    return 'stand'
                else:  # 9, 10, A
                    return 'hit'
            elif soft_value >= 8:  # A,8+ (soft 19+)
                return 'stand'
        
        # Handle hard hands
        else:
            if player_total <= 8:
                return 'hit'
            elif player_total == 9:
                if dealer_value in [3, 4, 5, 6] and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif player_total == 10:
                if dealer_value <= 9 and can_double:
                    return 'double'
                else:
                    return 'hit'
            elif player_total == 11:
                if can_double:
                    return 'double'
                else:
                    return 'hit'
            elif player_total == 12:
                if dealer_value in [4, 5, 6]:
                    return 'stand'
                else:
                    return 'hit'
            elif player_total in [13, 14, 15, 16]:
                if dealer_value <= 6:
                    return 'stand'
                else:
                    return 'hit'
            else:  # 17+
                return 'stand'
        
        return 'stand'  # Default
    
    def get_bet_amount(self, true_count, bet_spread):
        """Calculate bet amount based on true count and bet spread"""
        tc = round(true_count)
        if tc <= 0:
            return bet_spread.get('tc_neg', 0)
        elif tc == 1:
            return bet_spread.get('tc_1', 5)
        elif tc == 2:
            return bet_spread.get('tc_2', 10)
        elif tc == 3:
            return bet_spread.get('tc_3', 15)
        elif tc == 4:
            return bet_spread.get('tc_4', 25)
        else:  # tc >= 5
            return bet_spread.get('tc_5plus', 25)
    
    def play_dealer_hand(self, dealer_hand, shoe, counter):
        """Play dealer hand according to rules"""
        while True:
            dealer_total = self.hand_value(dealer_hand)
            
            # Dealer stands on hard 17 or higher
            if dealer_total >= 17:
                # Check soft 17 rule
                if dealer_total == 17 and self.is_soft_hand(dealer_hand) and self.rules['dealer_hits_soft17']:
                    pass  # Continue to hit
                else:
                    break
            
            # Dealer hits
            if len(shoe) == 0:
                break
            new_card = shoe.pop()
            dealer_hand.append(new_card)
            counter.add_card(new_card)
    
    def play_hand_recursive(self, player_hand, dealer_up_card, shoe, counter, bet_amount, split_depth=0):
        """
        Recursively play a hand with full basic strategy including splits
        Returns: (net_result, total_wagered)
        """
        total_wagered = bet_amount
        
        # Check for blackjack (only on initial 2-card hands, not after splits)
        if len(player_hand) == 2 and split_depth == 0 and self.is_blackjack(player_hand):
            return bet_amount * self.rules['blackjack_pays'], total_wagered
        
        # Play the hand
        while True:
            player_total = self.hand_value(player_hand)
            
            if player_total > 21:
                return -bet_amount, total_wagered  # Bust
            
            if player_total == 21:
                break  # Stand on 21
            
            # Determine available actions
            can_double = len(player_hand) == 2 and len(shoe) > 0
            can_split = (self.can_split(player_hand) and 
                        split_depth < self.rules['max_splits'] and 
                        len(shoe) > 1)
            
            # Special case: after splitting aces, usually only one card allowed
            if split_depth > 0 and len(player_hand) >= 2 and player_hand[0] == 'A':
                if not self.rules['resplit_aces']:
                    break  # Stand after receiving one card to split ace
            
            can_surrender = (len(player_hand) == 2 and 
                           split_depth == 0 and 
                           self.rules['surrender_allowed'])
            
            # Check doubling after split rules
            if split_depth > 0 and not self.rules['double_after_split']:
                can_double = False
            
            # Get basic strategy decision
            decision = self.basic_strategy_decision(
                player_hand, dealer_up_card, can_double, can_split, can_surrender
            )
            
            if decision == 'hit':
                if len(shoe) == 0:
                    break
                new_card = shoe.pop()
                player_hand.append(new_card)
                counter.add_card(new_card)
                
            elif decision == 'double':
                if len(shoe) == 0:
                    break
                new_card = shoe.pop()
                player_hand.append(new_card)
                counter.add_card(new_card)
                total_wagered = bet_amount * 2
                break  # Stand after doubling
                
            elif decision == 'split':
                # Split the hand
                card1, card2 = player_hand[0], player_hand[1]
                
                # Create two new hands
                hand1 = [card1]
                hand2 = [card2]
                
                # Deal one card to each hand
                if len(shoe) >= 2:
                    new_card1 = shoe.pop()
                    hand1.append(new_card1)
                    counter.add_card(new_card1)
                    
                    new_card2 = shoe.pop()
                    hand2.append(new_card2)
                    counter.add_card(new_card2)
                    
                    # Play each hand recursively
                    result1, wagered1 = self.play_hand_recursive(
                        hand1, dealer_up_card, shoe, counter, bet_amount, split_depth + 1
                    )
                    result2, wagered2 = self.play_hand_recursive(
                        hand2, dealer_up_card, shoe, counter, bet_amount, split_depth + 1
                    )
                    
                    return result1 + result2, wagered1 + wagered2
                else:
                    break  # Not enough cards to split
                    
            elif decision == 'surrender':
                return -bet_amount * 0.5, total_wagered  # Lose half bet
                
            elif decision == 'stand':
                break
        
        # Hand is complete, return for comparison with dealer
        return 0, total_wagered  # Will be resolved against dealer hand
    
    def play_hand(self, shoe, true_count, counter, bet_spread):
        """Play a complete blackjack hand with proper rules"""
        if len(shoe) < 10:
            return 0, 0
        
        # Check bet amount
        bet_amount = self.get_bet_amount(true_count, bet_spread)
        if bet_amount == 0:
            # Sit out but burn cards
            cards_to_burn = min(4, len(shoe))
            for _ in range(cards_to_burn):
                if shoe:
                    card = shoe.pop()
                    counter.add_card(card)
            return 0, 0
        
        # Deal initial cards
        player_hand = []
        dealer_hand = []
        
        # Deal player cards
        player_hand.append(shoe.pop())
        counter.add_card(player_hand[-1])
        player_hand.append(shoe.pop())
        counter.add_card(player_hand[-1])
        
        # Deal dealer cards  
        dealer_hand.append(shoe.pop())
        counter.add_card(dealer_hand[-1])
        dealer_hand.append(shoe.pop())
        counter.add_card(dealer_hand[-1])
        
        dealer_up_card = dealer_hand[0]
        
        # Check for dealer blackjack
        dealer_bj = self.is_blackjack(dealer_hand)
        player_bj = self.is_blackjack(player_hand)
        
        if dealer_bj and player_bj:
            return 0, bet_amount  # Push
        elif dealer_bj:
            return -bet_amount, bet_amount  # Dealer blackjack wins
        elif player_bj:
            return bet_amount * self.rules['blackjack_pays'], bet_amount  # Player blackjack
        
        # Play player hand
        player_result, total_wagered = self.play_hand_recursive(
            player_hand, dealer_up_card, shoe, counter, bet_amount
        )
        
        # If player surrendered or busted, return result
        if player_result != 0 or self.hand_value(player_hand) > 21:
            return player_result, total_wagered
        
        # Play dealer hand
        self.play_dealer_hand(dealer_hand, shoe, counter)
        
        # Compare hands
        player_total = self.hand_value(player_hand)
        dealer_total = self.hand_value(dealer_hand)
        
        if dealer_total > 21:
            return total_wagered, total_wagered  # Dealer busts
        elif player_total > dealer_total:
            return total_wagered, total_wagered  # Player wins
        elif player_total < dealer_total:
            return -total_wagered, total_wagered  # Dealer wins
        else:
            return 0, total_wagered  # Push