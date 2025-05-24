"""
Utility functions for blackjack simulation
"""

import random
from collections import deque

def create_deck(num_decks=1):
    """Create a shuffled deck with specified number of standard 52-card decks"""
    
    # Standard deck ranks
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    
    deck = []
    for _ in range(num_decks):
        for rank in ranks:
            for suit in suits:
                deck.append(rank)  # For counting, we only need the rank
    
    return deck

def calculate_remaining_decks(remaining_cards):
    """Calculate remaining decks from remaining cards"""
    return max(0.5, remaining_cards / 52.0)  # Minimum 0.5 to avoid division by zero

def format_percentage(value, decimal_places=6):
    """Format percentage with specified decimal places"""
    return f"{value:.{decimal_places}f}%"

def create_progress_bar(current, total, bar_length=50):
    """Create a simple progress bar string"""
    progress = current / total
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    return f'[{bar}] {progress:.1%} ({current}/{total})'

def validate_simulation_parameters(deck_counts, penetrations):
    """Validate simulation parameters"""
    errors = []
    
    # Check deck counts
    if not all(isinstance(d, int) and d > 0 for d in deck_counts):
        errors.append("Deck counts must be positive integers")
    
    # Check penetrations
    if not all(isinstance(p, (int, float)) and p > 0 for p in penetrations):
        errors.append("Penetrations must be positive numbers")
    
    # Check for valid combinations
    valid_combinations = []
    for deck_count in deck_counts:
        for penetration in penetrations:
            if penetration < deck_count:
                valid_combinations.append((deck_count, penetration))
    
    if not valid_combinations:
        errors.append("No valid combinations found (penetration must be less than deck count)")
    
    return errors, valid_combinations

def estimate_simulation_time(num_configurations, hands_per_config, hands_per_second=50000):
    """Estimate total simulation time"""
    total_hands = num_configurations * hands_per_config
    estimated_seconds = total_hands / hands_per_second
    
    hours = int(estimated_seconds // 3600)
    minutes = int((estimated_seconds % 3600) // 60)
    seconds = int(estimated_seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    return numerator / denominator
