"""
High-Low card counting system implementation
"""

class HighLowCounter:
    """Implements the High-Low card counting system"""
    
    # High-Low card values
    CARD_VALUES = {
        'A': -1, 'K': -1, 'Q': -1, 'J': -1, '10': -1,
        '9': 0, '8': 0, '7': 0,
        '6': 1, '5': 1, '4': 1, '3': 1, '2': 1
    }
    
    def __init__(self):
        self.running_count = 0
    
    def reset(self):
        """Reset the running count (used when shoe is shuffled)"""
        self.running_count = 0
    
    def add_card(self, card):
        """Add a card to the count"""
        card_value = self.CARD_VALUES.get(card, 0)
        self.running_count += card_value
    
    def get_running_count(self):
        """Get the current running count"""
        return self.running_count
    
    def get_true_count(self, remaining_decks):
        """Calculate true count by dividing running count by remaining decks"""
        if remaining_decks <= 0:
            return 0
        return round(self.running_count / remaining_decks)
    
    def get_true_count_precise(self, remaining_decks):
        """Get precise true count without rounding"""
        if remaining_decks <= 0:
            return 0.0
        return self.running_count / remaining_decks
