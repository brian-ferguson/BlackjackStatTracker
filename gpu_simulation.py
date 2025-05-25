#!/usr/bin/env python3
"""
GPU-accelerated blackjack simulation using CUDA
"""

import numpy as np
import csv
import os
from datetime import datetime

try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("GPU acceleration available with CuPy")
except ImportError:
    import numpy as cp
    GPU_AVAILABLE = False
    print("CuPy not available, falling back to CPU NumPy")

class GPUBlackjackSimulator:
    """GPU-accelerated blackjack simulation"""
    
    def __init__(self):
        self.use_gpu = GPU_AVAILABLE
        
    def create_gpu_deck(self, num_decks, batch_size):
        """Create multiple shuffled decks on GPU"""
        # Card values: A=1, 2-9=face, 10/J/Q/K=10
        single_deck = cp.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4)
        full_deck = cp.tile(single_deck, num_decks)
        
        # Create batch of shuffled decks
        decks = cp.tile(full_deck, (batch_size, 1))
        
        # Shuffle each deck
        for i in range(batch_size):
            cp.random.shuffle(decks[i])
            
        return decks
    
    def calculate_hand_values_gpu(self, hands):
        """Calculate hand values on GPU handling aces"""
        # hands: (batch_size, max_cards_per_hand)
        # Returns best hand values
        
        values = cp.sum(hands, axis=1)  # Sum all cards
        aces = cp.sum(hands == 1, axis=1)  # Count aces
        
        # Handle soft aces (count as 11 instead of 1)
        # Add 10 for each ace we can count as 11 without busting
        can_use_soft_ace = (values + 10 <= 21) & (aces > 0)
        values = cp.where(can_use_soft_ace, values + 10, values)
        
        return values
    
    def basic_strategy_gpu(self, player_hands, dealer_up_cards):
        """Vectorized basic strategy decisions on GPU"""
        batch_size = player_hands.shape[0]
        
        # Calculate hand values
        player_values = self.calculate_hand_values_gpu(player_hands)
        dealer_values = dealer_up_cards
        
        # Initialize decisions (0=hit, 1=stand, 2=double)
        decisions = cp.zeros(batch_size, dtype=cp.int32)
        
        # Basic strategy rules (simplified but accurate)
        # Hard totals
        decisions = cp.where((player_values <= 8), 0, decisions)  # Hit
        decisions = cp.where((player_values == 9) & (dealer_values >= 3) & (dealer_values <= 6), 2, decisions)  # Double
        decisions = cp.where((player_values == 9) & ((dealer_values < 3) | (dealer_values > 6)), 0, decisions)  # Hit
        decisions = cp.where((player_values == 10) & (dealer_values <= 9), 2, decisions)  # Double
        decisions = cp.where((player_values == 10) & (dealer_values > 9), 0, decisions)  # Hit
        decisions = cp.where((player_values == 11), 2, decisions)  # Double
        decisions = cp.where((player_values == 12) & (dealer_values >= 4) & (dealer_values <= 6), 1, decisions)  # Stand
        decisions = cp.where((player_values == 12) & ((dealer_values < 4) | (dealer_values > 6)), 0, decisions)  # Hit
        decisions = cp.where((player_values >= 13) & (player_values <= 16) & (dealer_values <= 6), 1, decisions)  # Stand
        decisions = cp.where((player_values >= 13) & (player_values <= 16) & (dealer_values > 6), 0, decisions)  # Hit
        decisions = cp.where((player_values >= 17), 1, decisions)  # Stand
        
        return decisions
    
    def simulate_hands_gpu(self, deck_count, penetration, num_shoes, batch_size=10000):
        """Simulate many hands on GPU in batches"""
        
        total_cards = deck_count * 52
        if penetration == 0:
            cards_to_play = total_cards
        else:
            cards_to_play = int(penetration * 52)
        
        # Track results
        true_count_stats = {}
        
        hands_per_shoe = cards_to_play // 5  # Approximate hands per shoe
        total_batches = (num_shoes * hands_per_shoe) // batch_size + 1
        
        print(f"  Processing {total_batches} GPU batches of {batch_size} hands each...")
        
        for batch_num in range(total_batches):
            if total_batches > 10 and batch_num % (total_batches // 10) == 0 and batch_num > 0:
                progress = (batch_num / total_batches) * 100
                print(f"    GPU Progress: {progress:.0f}%")
            
            # Create batch of decks
            decks = self.create_gpu_deck(deck_count, batch_size)
            
            # Simulate card counting and hand outcomes
            running_counts = cp.zeros(batch_size, dtype=cp.int32)
            
            # Deal initial cards (simplified - 4 cards per hand)
            player_hands = decks[:, :2]  # First 2 cards
            dealer_hands = decks[:, 2:4]  # Next 2 cards
            
            # Update running count (High-Low: +1 for 2-6, -1 for 10-A)
            all_dealt_cards = decks[:, :4].flatten()
            low_cards = cp.sum((all_dealt_cards >= 2) & (all_dealt_cards <= 6))
            high_cards = cp.sum((all_dealt_cards >= 10) | (all_dealt_cards == 1))
            running_count = low_cards - high_cards
            
            # Calculate true count (simplified)
            remaining_decks = (total_cards - 4) / 52
            true_count = int(running_count / remaining_decks) if remaining_decks > 0 else 0
            true_count = max(-10, min(10, true_count))  # Clamp to range
            
            # Basic strategy decisions
            dealer_up_cards = dealer_hands[:, 0]
            decisions = self.basic_strategy_gpu(player_hands, dealer_up_cards)
            
            # Simplified outcome calculation
            player_values = self.calculate_hand_values_gpu(player_hands)
            dealer_values = self.calculate_hand_values_gpu(dealer_hands)
            
            # Determine winners (simplified)
            player_wins = (player_values <= 21) & ((dealer_values > 21) | (player_values > dealer_values))
            pushes = (player_values <= 21) & (dealer_values <= 21) & (player_values == dealer_values)
            
            # Calculate profits (+10 win, -10 loss, 0 push)
            profits = cp.where(player_wins, 10, cp.where(pushes, 0, -10))
            
            # Handle doubling
            doubled = (decisions == 2)
            profits = cp.where(doubled, profits * 2, profits)
            bet_amounts = cp.where(doubled, 20, 10)
            
            # Track results for this true count
            if true_count not in true_count_stats:
                true_count_stats[true_count] = {
                    'frequency': 0,
                    'total_profit': 0.0,
                    'total_wagered': 0.0
                }
            
            # Convert GPU results to CPU for accumulation
            total_profit = float(cp.sum(profits))
            total_wagered = float(cp.sum(bet_amounts))
            
            true_count_stats[true_count]['frequency'] += batch_size
            true_count_stats[true_count]['total_profit'] += total_profit
            true_count_stats[true_count]['total_wagered'] += total_wagered
        
        return true_count_stats
    
    def save_results(self, deck_count, penetration, num_shoes, true_count_stats):
        """Save GPU simulation results to CSV"""
        
        # Calculate totals
        total_hands = sum(stats['frequency'] for stats in true_count_stats.values())
        
        os.makedirs('simulation_results', exist_ok=True)
        
        if penetration == 0:
            filename = f"simulation_results/{deck_count}decks-nopenetration-gpu.csv"
            penetration_desc = "No penetration (all cards played)"
        else:
            filename = f"simulation_results/{deck_count}decks-{penetration}penetration-gpu.csv"
            penetration_desc = f"{penetration} deck penetration"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['# GPU-Accelerated Blackjack High-Low Simulation Results'])
            writer.writerow([f'# Deck Count: {deck_count}'])
            writer.writerow([f'# Penetration: {penetration_desc}'])
            writer.writerow([f'# Total Shoes: {num_shoes:,}'])
            writer.writerow([f'# Total Hands: {total_hands:,}'])
            writer.writerow(['# Fixed Bet Amount: $10 per hand'])
            writer.writerow([f'# GPU Accelerated: {self.use_gpu}'])
            writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Column headers
            writer.writerow(['True Count', 'Frequency', 'Percentage', 'Player Edge', 'Total Profit', 'Total Wagered'])
            
            # Data
            for true_count in range(-10, 11):
                if true_count in true_count_stats:
                    stats = true_count_stats[true_count]
                    frequency = stats['frequency']
                    percentage = (frequency / total_hands) * 100 if total_hands > 0 else 0
                    edge = (stats['total_profit'] / stats['total_wagered']) if stats['total_wagered'] > 0 else 0.0
                    
                    writer.writerow([
                        true_count,
                        frequency,
                        f"{percentage:.6f}",
                        f"{edge:.6f}",
                        f"{stats['total_profit']:.2f}",
                        f"{stats['total_wagered']:.2f}"
                    ])
                else:
                    writer.writerow([
                        true_count,
                        0,
                        "0.000000",
                        "0.000000",
                        "0.00",
                        "0.00"
                    ])
        
        print(f"  GPU results saved to {filename}")
        return filename

def run_gpu_simulation(num_shoes):
    """Run GPU-accelerated simulation"""
    
    simulator = GPUBlackjackSimulator()
    
    # Generate configurations
    deck_counts = [1, 2, 3, 4, 6, 8]
    configurations = []
    
    for deck_count in deck_counts:
        configurations.append((deck_count, 0))  # No penetration
        current_penetration = deck_count - 0.25
        while current_penetration >= deck_count / 2:
            configurations.append((deck_count, current_penetration))
            current_penetration -= 0.25
    
    print(f"GPU Simulation: {num_shoes:,} shoes per configuration")
    print(f"Total configurations: {len(configurations)}")
    print(f"GPU Available: {GPU_AVAILABLE}")
    print("=" * 60)
    
    for i, (deck_count, penetration) in enumerate(configurations, 1):
        print(f"\nGPU Configuration {i}/{len(configurations)}:")
        print(f"Running {deck_count} deck(s), penetration {penetration}, {num_shoes:,} shoes...")
        
        stats = simulator.simulate_hands_gpu(deck_count, penetration, num_shoes)
        simulator.save_results(deck_count, penetration, num_shoes, stats)
    
    print(f"\n{'='*60}")
    print("GPU simulation completed!")
    print("Results saved with '-gpu' suffix")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        num_shoes = int(sys.argv[1])
    else:
        num_shoes = 10000
    
    run_gpu_simulation(num_shoes)