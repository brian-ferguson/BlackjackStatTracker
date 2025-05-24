"""
Blackjack simulation engine with High-Low card counting
"""

import random
import numpy as np
from collections import deque, Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import csv
import os
from datetime import datetime
import time

from card_counting import HighLowCounter
from utils import create_deck, calculate_remaining_decks

class BlackjackSimulator:
    """Main simulation engine for blackjack with card counting"""
    
    def __init__(self, num_processes=None):
        self.num_processes = num_processes or multiprocessing.cpu_count()
        
    def run_penetration_simulation(self, configurations, shoes_per_config):
        """Run simulation for specified deck/penetration configurations"""
        
        # Create output directory
        os.makedirs('simulation_results', exist_ok=True)
        
        total_configs = len(configurations)
        current_config = 0
        
        all_results = {}
        
        print(f"Running {total_configs} configurations with {self.num_processes} processes")
        
        for deck_count, penetration in configurations:
            current_config += 1
            
            if penetration == 0:
                config_name = f"{deck_count}decks-nopenetration"
            else:
                config_name = f"{deck_count}decks-{penetration}penetration"
            
            print(f"\nConfig {current_config}/{total_configs}: {config_name}")
            start_time = time.time()
            
            # Run simulation for this configuration
            result = self._simulate_configuration(deck_count, penetration, shoes_per_config)
            
            # Store results
            config_key = (deck_count, penetration)
            all_results[config_key] = result
            
            # Save individual result to CSV with new naming convention
            self._save_penetration_results(deck_count, penetration, result)
            
            elapsed = time.time() - start_time
            print(f"Completed in {elapsed:.2f} seconds")
        
        return all_results

    def run_full_simulation(self, deck_counts, penetrations, hands_per_config):
        """Run simulation for all combinations of deck counts and penetrations (legacy method)"""
        
        # Create output directory
        os.makedirs('simulation_results', exist_ok=True)
        
        total_configs = len(deck_counts) * len(penetrations)
        current_config = 0
        
        all_results = {}
        
        print(f"Running {total_configs} configurations with {self.num_processes} processes")
        
        for deck_count in deck_counts:
            for penetration in penetrations:
                current_config += 1
                
                # Skip invalid combinations (penetration can't exceed deck count)
                if penetration >= deck_count:
                    print(f"Skipping invalid config: {deck_count} decks, {penetration} penetration")
                    continue
                
                print(f"\nConfig {current_config}/{total_configs}: {deck_count} decks, {penetration} penetration")
                start_time = time.time()
                
                # Run simulation for this configuration
                result = self._simulate_configuration(deck_count, penetration, hands_per_config)
                
                # Store results
                config_key = (deck_count, penetration)
                all_results[config_key] = result
                
                # Save individual result to CSV
                self._save_configuration_results(deck_count, penetration, result)
                
                elapsed = time.time() - start_time
                print(f"Completed in {elapsed:.2f} seconds")
        
        return all_results
    
    def _simulate_configuration(self, deck_count, penetration, num_shoes):
        """Simulate a specific configuration using parallel processing"""
        
        # Split work across processes (now dividing shoes, not hands)
        shoes_per_process = num_shoes // self.num_processes
        remaining_shoes = num_shoes % self.num_processes
        
        tasks = []
        for i in range(self.num_processes):
            process_shoes = shoes_per_process
            if i < remaining_shoes:
                process_shoes += 1
            
            tasks.append((deck_count, penetration, process_shoes, i))
        
        # Run simulations in parallel
        true_count_distributions = []
        
        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            future_to_task = {
                executor.submit(_simulate_hands_worker, task): task 
                for task in tasks
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    true_count_distributions.append(result)
                except Exception as e:
                    print(f"Process {task[3]} failed: {e}")
                    raise
        
        # Combine results from all processes
        combined_distribution = Counter()
        total_hands_simulated = 0
        
        for distribution in true_count_distributions:
            for true_count, count in distribution.items():
                combined_distribution[true_count] += count
                total_hands_simulated += count
        
        # Convert to percentages
        percentage_distribution = {}
        for true_count in range(-10, 11):
            count = combined_distribution.get(true_count, 0)
            percentage = (count / total_hands_simulated) * 100 if total_hands_simulated > 0 else 0
            percentage_distribution[true_count] = percentage
        
        return {
            'distribution': percentage_distribution,
            'total_hands': total_hands_simulated,
            'total_shoes': num_shoes,
            'deck_count': deck_count,
            'penetration': penetration
        }
    
    def _save_penetration_results(self, deck_count, penetration, result):
        """Save results for a single configuration to CSV with new naming convention"""
        
        if penetration == 0:
            filename = f"simulation_results/{deck_count}decks-nopenetration.csv"
            penetration_desc = "No penetration (all cards played)"
        else:
            filename = f"simulation_results/{deck_count}decks-{penetration}penetration.csv"
            penetration_desc = f"{penetration} deck penetration"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with metadata
            writer.writerow(['# Blackjack High-Low Simulation Results'])
            writer.writerow([f'# Deck Count: {deck_count}'])
            writer.writerow([f'# Penetration: {penetration_desc}'])
            writer.writerow([f'# Total Shoes: {result["total_shoes"]:,}'])
            writer.writerow([f'# Total Hands: {result["total_hands"]:,}'])
            writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Write column headers
            writer.writerow(['True Count', 'Percentage'])
            
            # Write data
            for true_count in range(-10, 11):
                percentage = result['distribution'][true_count]
                writer.writerow([true_count, f"{percentage:.6f}"])
        
        print(f"Saved results to {filename}")

    def _save_configuration_results(self, deck_count, penetration, result):
        """Save results for a single configuration to CSV (legacy method)"""
        
        filename = f"simulation_results/{deck_count}deck_{penetration}pen.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with metadata
            writer.writerow(['# Blackjack High-Low Simulation Results'])
            writer.writerow([f'# Deck Count: {deck_count}'])
            writer.writerow([f'# Penetration: {penetration}'])
            writer.writerow([f'# Total Hands: {result["total_hands"]:,}'])
            writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Write column headers
            writer.writerow(['True Count', 'Percentage'])
            
            # Write data
            for true_count in range(-10, 11):
                percentage = result['distribution'][true_count]
                writer.writerow([true_count, f"{percentage:.6f}"])
        
        print(f"Saved results to {filename}")

def _simulate_hands_worker(args):
    """Worker function for parallel simulation"""
    deck_count, penetration, num_shoes, process_id = args
    
    # Initialize for this process
    random.seed()  # Each process gets different random seed
    counter = HighLowCounter()
    true_count_distribution = Counter()
    
    # Calculate how many cards to play before reshuffle
    total_cards = deck_count * 52
    if penetration == 0:  # No penetration = play all cards
        cards_to_play = total_cards
    else:  # Penetration = how many decks worth of cards to play
        cards_to_play = int(penetration * 52)
    
    total_hands_counted = 0
    
    for shoe_num in range(num_shoes):
        # Create and shuffle new shoe
        shoe = create_deck(deck_count)
        random.shuffle(shoe)
        cards_dealt = 0
        counter.reset()
        
        # Deal through the shoe until penetration reached
        while cards_dealt < cards_to_play:
            # Deal 2-7 cards per hand (typical range for blackjack hands)
            cards_this_hand = random.randint(2, 7)
            
            # Make sure we don't exceed the penetration limit
            if cards_dealt + cards_this_hand > cards_to_play:
                break
            
            if len(shoe) < cards_this_hand:
                # Should not happen with proper penetration calculation
                break
            
            # Deal the cards and update count
            for _ in range(cards_this_hand):
                if shoe and cards_dealt < cards_to_play:
                    card = shoe.pop()
                    counter.add_card(card)
                    cards_dealt += 1
            
            # Calculate true count (only count cards that will actually be dealt)
            remaining_cards_in_play = cards_to_play - cards_dealt
            remaining_decks = calculate_remaining_decks(remaining_cards_in_play)
            true_count = counter.get_true_count(remaining_decks)
            
            # Clamp true count to range [-10, +10] for analysis
            clamped_true_count = max(-10, min(10, true_count))
            true_count_distribution[clamped_true_count] += 1
            total_hands_counted += 1
    
    return true_count_distribution
