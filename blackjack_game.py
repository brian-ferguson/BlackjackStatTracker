"""
Blackjack game logic for calculating player edges
"""

import random

class BlackjackGame:
    """Simple blackjack game engine for edge calculation"""
    
    def __init__(self):
        self.bet_amount = 10  # Fixed $10 bet
    
    def card_value(self, card):
        """Get numeric value of a card for blackjack"""
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 11  # Will handle soft aces in hand calculation
        else:
            return int(card)
    
    def hand_value(self, hand):
        """Calculate best hand value, handling aces"""
        total = 0
        aces = 0
        
        for card in hand:
            if card == 'A':
                aces += 1
                total += 11
            elif card in ['J', 'Q', 'K']:
                total += 10
            else:
                total += int(card)
        
        # Adjust for aces if over 21
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_blackjack(self, hand):
        """Check if hand is blackjack (21 with 2 cards)"""
        return len(hand) == 2 and self.hand_value(hand) == 21
    
    def basic_strategy_decision(self, player_hand, dealer_up_card, can_double=True, can_split=False):
        """Basic strategy decision (simplified)"""
        player_total = self.hand_value(player_hand)
        dealer_value = self.card_value(dealer_up_card)
        
        # Handle soft hands (with ace counted as 11)
        has_soft_ace = 'A' in player_hand and player_total <= 21
        
        if can_split and len(player_hand) == 2 and player_hand[0] == player_hand[1]:
            # Splitting logic (simplified)
            if player_hand[0] == 'A' or player_hand[0] == '8':
                return 'split'
            elif player_hand[0] in ['2', '3', '6', '7', '9'] and dealer_value <= 6:
                return 'split'
        
        if has_soft_ace and player_total >= 13 and player_total <= 18:
            # Soft hand strategy (simplified)
            if player_total <= 17 and dealer_value >= 7:
                return 'hit'
            elif player_total in [15, 16] and dealer_value in [4, 5, 6] and can_double:
                return 'double'
            elif player_total >= 18:
                return 'stand'
            else:
                return 'hit'
        
        # Hard hand strategy
        if player_total <= 8:
            return 'hit'
        elif player_total == 9:
            return 'double' if dealer_value in [3, 4, 5, 6] and can_double else 'hit'
        elif player_total == 10:
            return 'double' if dealer_value <= 9 and can_double else 'hit'
        elif player_total == 11:
            return 'double' if can_double else 'hit'
        elif player_total <= 16:
            return 'hit' if dealer_value >= 7 else 'stand'
        else:
            return 'stand'
    
    def play_hand(self, shoe, true_count, counter):
        """Play a single blackjack hand and return net result"""
        if len(shoe) < 10:  # Need enough cards for a hand
            return 0, 0  # No bet placed
        
        # Deal initial cards and update count
        player_hand = []
        dealer_hand = []
        
        # Deal player cards
        card1 = shoe.pop()
        player_hand.append(card1)
        counter.add_card(card1)
        
        card2 = shoe.pop()
        player_hand.append(card2)
        counter.add_card(card2)
        
        # Deal dealer cards
        dealer_card1 = shoe.pop()
        dealer_hand.append(dealer_card1)
        counter.add_card(dealer_card1)
        
        dealer_card2 = shoe.pop()
        dealer_hand.append(dealer_card2)
        counter.add_card(dealer_card2)
        
        dealer_up_card = dealer_hand[0]
        
        bet_amount = self.bet_amount
        total_bet = bet_amount
        
        # Check for blackjacks
        player_bj = self.is_blackjack(player_hand)
        dealer_bj = self.is_blackjack(dealer_hand)
        
        if player_bj and dealer_bj:
            return 0, total_bet  # Push
        elif player_bj:
            return bet_amount * 1.5, total_bet  # Blackjack pays 3:2
        elif dealer_bj:
            return -bet_amount, total_bet  # Lose to dealer blackjack
        
        # Play player hand using basic strategy
        player_total = self.hand_value(player_hand)
        
        while player_total < 21:
            decision = self.basic_strategy_decision(player_hand, dealer_up_card, 
                                                  can_double=len(player_hand)==2)
            
            if decision == 'hit':
                if len(shoe) == 0:
                    break
                new_card = shoe.pop()
                player_hand.append(new_card)
                counter.add_card(new_card)
                player_total = self.hand_value(player_hand)
            elif decision == 'double':
                if len(shoe) == 0:
                    break
                new_card = shoe.pop()
                player_hand.append(new_card)
                counter.add_card(new_card)
                player_total = self.hand_value(player_hand)
                total_bet *= 2  # Double the bet
                break
            elif decision == 'stand':
                break
            # Note: Splitting not implemented for simplicity
        
        # Player busted
        if player_total > 21:
            return -total_bet, total_bet
        
        # Play dealer hand
        dealer_total = self.hand_value(dealer_hand)
        while dealer_total < 17:
            if len(shoe) == 0:
                break
            new_card = shoe.pop()
            dealer_hand.append(new_card)
            counter.add_card(new_card)
            dealer_total = self.hand_value(dealer_hand)
        
        # Determine winner
        if dealer_total > 21:
            return total_bet, total_bet  # Dealer busts, player wins
        elif player_total > dealer_total:
            return total_bet, total_bet  # Player wins
        elif player_total < dealer_total:
            return -total_bet, total_bet  # Dealer wins
        else:
            return 0, total_bet  # Push