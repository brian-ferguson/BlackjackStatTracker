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
from blackjack_game import BlackjackGame

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
        worker_results = []
        
        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            future_to_task = {
                executor.submit(_simulate_hands_worker, task): task 
                for task in tasks
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    worker_results.append(result)
                except Exception as e:
                    print(f"Process {task[3]} failed: {e}")
                    raise
        
        # Combine results from all processes
        combined_stats = defaultdict(lambda: {
            'frequency': 0,
            'total_profit': 0.0,
            'total_wagered': 0.0
        })
        
        total_hands_simulated = 0
        
        for worker_result in worker_results:
            for true_count, stats in worker_result.items():
                combined_stats[true_count]['frequency'] += stats['frequency']
                combined_stats[true_count]['total_profit'] += stats['total_profit']
                combined_stats[true_count]['total_wagered'] += stats['total_wagered']
                total_hands_simulated += stats['frequency']
        
        # Calculate edges and create distribution for backward compatibility
        percentage_distribution = {}
        edge_data = {}
        
        for true_count in range(-10, 11):
            stats = combined_stats.get(true_count, {'frequency': 0, 'total_profit': 0.0, 'total_wagered': 0.0})
            
            # Calculate frequency percentage
            frequency = stats['frequency']
            percentage = (frequency / total_hands_simulated) * 100 if total_hands_simulated > 0 else 0
            percentage_distribution[true_count] = percentage
            
            # Calculate edge
            total_wagered = stats['total_wagered']
            total_profit = stats['total_profit']
            edge = (total_profit / total_wagered) if total_wagered > 0 else 0.0
            
            edge_data[true_count] = {
                'frequency': frequency,
                'edge': edge,
                'total_profit': total_profit,
                'total_wagered': total_wagered
            }
        
        return {
            'distribution': percentage_distribution,
            'edge_data': edge_data,
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
            writer.writerow(['# Blackjack High-Low Simulation Results with Player Edge Analysis'])
            writer.writerow([f'# Deck Count: {deck_count}'])
            writer.writerow([f'# Penetration: {penetration_desc}'])
            writer.writerow([f'# Total Shoes: {result["total_shoes"]:,}'])
            writer.writerow([f'# Total Hands: {result["total_hands"]:,}'])
            writer.writerow([f'# Fixed Bet Amount: $10 per hand'])
            writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Write column headers
            writer.writerow(['True Count', 'Frequency', 'Percentage', 'Player Edge', 'Total Profit', 'Total Wagered'])
            
            # Write data
            for true_count in range(-10, 11):
                percentage = result['distribution'][true_count]
                edge_info = result.get('edge_data', {}).get(true_count, {
                    'frequency': 0,
                    'edge': 0.0,
                    'total_profit': 0.0,
                    'total_wagered': 0.0
                })
                
                writer.writerow([
                    true_count,
                    edge_info['frequency'],
                    f"{percentage:.6f}",
                    f"{edge_info['edge']:.6f}",
                    f"{edge_info['total_profit']:.2f}",
                    f"{edge_info['total_wagered']:.2f}"
                ])
        
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
    """Worker function for parallel simulation with edge calculation"""
    deck_count, penetration, num_shoes, process_id = args
    
    # Initialize for this process
    random.seed()  # Each process gets different random seed
    counter = HighLowCounter()
    game = BlackjackGame()
    
    # Track frequency and financial results for each true count
    true_count_stats = defaultdict(lambda: {
        'frequency': 0,
        'total_profit': 0.0,
        'total_wagered': 0.0
    })
    
    # Calculate how many cards to play before reshuffle
    total_cards = deck_count * 52
    if penetration == 0:  # No penetration = play all cards
        cards_to_play = total_cards
    else:  # Penetration = how many decks worth of cards to play
        cards_to_play = int(penetration * 52)
    
    total_hands_played = 0
    
    for shoe_num in range(num_shoes):
        # Create and shuffle new shoe
        shoe = create_deck(deck_count)
        random.shuffle(shoe)
        cards_dealt = 0
        counter.reset()
        
        # Deal through the shoe until penetration reached
        while cards_dealt < cards_to_play and len(shoe) >= 10:  # Need enough cards for blackjack
            # Calculate true count before playing hand
            remaining_cards_in_shoe = len(shoe)
            remaining_decks = calculate_remaining_decks(remaining_cards_in_shoe)
            true_count_precise = counter.get_true_count_precise(remaining_decks)
            true_count_rounded = round(true_count_precise)
            
            # Only track and play hands for true counts in range [-10, +10]
            if -10 <= true_count_rounded <= 10:
                # Play a blackjack hand at this true count
                profit, bet_amount = game.play_hand(shoe, true_count_rounded, counter)
                
                if bet_amount > 0:  # Hand was actually played
                    true_count_stats[true_count_rounded]['frequency'] += 1
                    true_count_stats[true_count_rounded]['total_profit'] += profit
                    true_count_stats[true_count_rounded]['total_wagered'] += bet_amount
                    total_hands_played += 1
            
            # Update cards dealt counter
            cards_dealt = total_cards - len(shoe)
    
    return true_count_stats
