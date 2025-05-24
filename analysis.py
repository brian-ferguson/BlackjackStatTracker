"""
Analysis module for simulation results
"""

import os
import csv
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

class SimulationAnalyzer:
    """Analyzes simulation results and generates reports"""
    
    def __init__(self, simulation_results):
        self.results = simulation_results
        
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        
        print("\nGenerating Analysis Report...")
        
        # Create analysis directory
        os.makedirs('analysis_results', exist_ok=True)
        
        # Perform various analyses
        self._analyze_deck_count_impact()
        self._analyze_penetration_impact()
        self._generate_summary_statistics()
        self._create_comparison_matrix()
        
        print("Analysis report generated in 'analysis_results' directory")
    
    def _analyze_deck_count_impact(self):
        """Analyze how deck count affects true count distribution"""
        
        print("Analyzing deck count impact...")
        
        # Group results by deck count
        deck_groups = defaultdict(list)
        for (deck_count, penetration), result in self.results.items():
            deck_groups[deck_count].append(result)
        
        # Calculate average distributions for each deck count
        deck_averages = {}
        for deck_count, results in deck_groups.items():
            avg_distribution = {}
            for tc in range(-10, 11):
                values = [r['distribution'][tc] for r in results]
                avg_distribution[tc] = np.mean(values)
            deck_averages[deck_count] = avg_distribution
        
        # Save to CSV
        with open('analysis_results/deck_count_impact.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = ['True Count'] + [f'{deck} Decks' for deck in sorted(deck_averages.keys())]
            writer.writerow(header)
            
            # Data
            for tc in range(-10, 11):
                row = [tc]
                for deck_count in sorted(deck_averages.keys()):
                    row.append(f"{deck_averages[deck_count][tc]:.6f}")
                writer.writerow(row)
        
        # Calculate variance across deck counts
        variances = {}
        for tc in range(-10, 11):
            values = [deck_averages[deck][tc] for deck in deck_averages.keys()]
            variances[tc] = np.var(values)
        
        # Find true counts most affected by deck count
        high_variance_tcs = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:5]
        
        with open('analysis_results/deck_count_analysis.txt', 'w') as f:
            f.write("DECK COUNT IMPACT ANALYSIS\n")
            f.write("=" * 40 + "\n\n")
            f.write("True counts most affected by deck count (highest variance):\n")
            for tc, variance in high_variance_tcs:
                f.write(f"TC {tc:+2d}: variance = {variance:.8f}\n")
            f.write(f"\nOverall variance across all true counts: {np.mean(list(variances.values())):.8f}\n")
    
    def _analyze_penetration_impact(self):
        """Analyze how penetration affects true count distribution"""
        
        print("Analyzing penetration impact...")
        
        # Group results by penetration
        pen_groups = defaultdict(list)
        for (deck_count, penetration), result in self.results.items():
            pen_groups[penetration].append(result)
        
        # Calculate average distributions for each penetration
        pen_averages = {}
        for penetration, results in pen_groups.items():
            avg_distribution = {}
            for tc in range(-10, 11):
                values = [r['distribution'][tc] for r in results]
                avg_distribution[tc] = np.mean(values)
            pen_averages[penetration] = avg_distribution
        
        # Save to CSV
        with open('analysis_results/penetration_impact.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = ['True Count'] + [f'{pen} Pen' for pen in sorted(pen_averages.keys(), reverse=True)]
            writer.writerow(header)
            
            # Data
            for tc in range(-10, 11):
                row = [tc]
                for penetration in sorted(pen_averages.keys(), reverse=True):
                    row.append(f"{pen_averages[penetration][tc]:.6f}")
                writer.writerow(row)
        
        # Calculate variance across penetrations
        variances = {}
        for tc in range(-10, 11):
            values = [pen_averages[pen][tc] for pen in pen_averages.keys()]
            variances[tc] = np.var(values)
        
        # Find true counts most affected by penetration
        high_variance_tcs = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:5]
        
        with open('analysis_results/penetration_analysis.txt', 'w') as f:
            f.write("PENETRATION IMPACT ANALYSIS\n")
            f.write("=" * 40 + "\n\n")
            f.write("True counts most affected by penetration (highest variance):\n")
            for tc, variance in high_variance_tcs:
                f.write(f"TC {tc:+2d}: variance = {variance:.8f}\n")
            f.write(f"\nOverall variance across all true counts: {np.mean(list(variances.values())):.8f}\n")
    
    def _generate_summary_statistics(self):
        """Generate overall summary statistics"""
        
        print("Generating summary statistics...")
        
        all_distributions = []
        for result in self.results.values():
            all_distributions.append(result['distribution'])
        
        # Calculate global averages
        global_avg = {}
        for tc in range(-10, 11):
            values = [dist[tc] for dist in all_distributions]
            global_avg[tc] = np.mean(values)
        
        # Calculate statistics
        stats = {}
        for tc in range(-10, 11):
            values = [dist[tc] for dist in all_distributions]
            stats[tc] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'range': np.max(values) - np.min(values)
            }
        
        # Save summary statistics
        with open('analysis_results/summary_statistics.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['True Count', 'Mean %', 'Std Dev', 'Min %', 'Max %', 'Range %'])
            
            for tc in range(-10, 11):
                s = stats[tc]
                writer.writerow([
                    tc,
                    f"{s['mean']:.6f}",
                    f"{s['std']:.6f}",
                    f"{s['min']:.6f}",
                    f"{s['max']:.6f}",
                    f"{s['range']:.6f}"
                ])
        
        # Generate summary report
        with open('analysis_results/summary_report.txt', 'w') as f:
            f.write("BLACKJACK HIGH-LOW SIMULATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total configurations simulated: {len(self.results)}\n")
            total_hands = sum(r['total_hands'] for r in self.results.values())
            f.write(f"Total hands simulated: {total_hands:,}\n\n")
            
            # Most common true counts
            f.write("Most frequently observed true counts (global average):\n")
            sorted_tcs = sorted(global_avg.items(), key=lambda x: x[1], reverse=True)[:5]
            for tc, pct in sorted_tcs:
                f.write(f"TC {tc:+2d}: {pct:.4f}%\n")
            
            f.write("\nLeast frequently observed true counts:\n")
            least_common = sorted(global_avg.items(), key=lambda x: x[1])[:5]
            for tc, pct in least_common:
                f.write(f"TC {tc:+2d}: {pct:.4f}%\n")
            
            # Highest variance true counts
            f.write("\nTrue counts with highest variance across configurations:\n")
            variances = [(tc, stats[tc]['std']) for tc in range(-10, 11)]
            high_var = sorted(variances, key=lambda x: x[1], reverse=True)[:5]
            for tc, var in high_var:
                f.write(f"TC {tc:+2d}: std dev = {var:.6f}\n")
    
    def _create_comparison_matrix(self):
        """Create a matrix comparing all configurations"""
        
        print("Creating comparison matrix...")
        
        # Create DataFrame for easier manipulation
        data = []
        for (deck_count, penetration), result in self.results.items():
            row = {
                'Deck_Count': deck_count,
                'Penetration': penetration,
                'Total_Hands': result['total_hands']
            }
            
            # Add true count percentages
            for tc in range(-10, 11):
                row[f'TC_{tc:+03d}'] = result['distribution'][tc]
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df = df.sort_values(['Deck_Count', 'Penetration'])
        
        # Save full comparison matrix
        df.to_csv('analysis_results/full_comparison_matrix.csv', index=False)
        
        # Create summary matrix with key statistics
        summary_data = []
        for (deck_count, penetration), result in self.results.items():
            dist = result['distribution']
            
            summary_row = {
                'Deck_Count': deck_count,
                'Penetration': penetration,
                'TC_Negative_Sum': sum(dist[tc] for tc in range(-10, 0)),
                'TC_Zero': dist[0],
                'TC_Positive_Sum': sum(dist[tc] for tc in range(1, 11)),
                'TC_Extreme_Sum': sum(dist[tc] for tc in [-10, -9, -8, 8, 9, 10]),
                'TC_Moderate_Sum': sum(dist[tc] for tc in range(-7, 8))
            }
            summary_data.append(summary_row)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values(['Deck_Count', 'Penetration'])
        summary_df.to_csv('analysis_results/summary_comparison_matrix.csv', index=False)
