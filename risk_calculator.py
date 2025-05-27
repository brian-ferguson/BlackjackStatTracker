"""
Advanced Risk of Ruin Calculator for Blackjack Card Counting
Uses actual simulation data with proper variance and Kelly Criterion formulas
"""

import math
import numpy as np
from typing import Dict, Tuple


class RiskOfRuinCalculator:
    """
    Calculate Risk of Ruin using actual simulation data and proper mathematical models
    """
    
    def __init__(self, base_sd_per_unit: float = 1.15):
        """
        Initialize the RoR calculator
        
        Args:
            base_sd_per_unit: Standard deviation per unit bet (typically 1.15 for blackjack)
        """
        self.base_sd_per_unit = base_sd_per_unit
    
    def calculate_ror(self, 
                     tc_frequencies: Dict[int, float],
                     tc_edges: Dict[int, float], 
                     tc_bet_sizes: Dict[int, float],
                     bankroll: float) -> Dict[str, float]:
        """
        Calculate Risk of Ruin using weighted variance and expected value
        
        Args:
            tc_frequencies: Dictionary of {true_count: frequency}
            tc_edges: Dictionary of {true_count: edge_per_hand}
            tc_bet_sizes: Dictionary of {true_count: bet_size_in_units}
            bankroll: Bankroll in betting units
            
        Returns:
            Dictionary with RoR results and supporting calculations
        """
        
        # Validate inputs
        self._validate_inputs(tc_frequencies, tc_edges, tc_bet_sizes, bankroll)
        
        # Calculate weighted expected value per hand
        ev_per_hand = self._calculate_weighted_ev(tc_frequencies, tc_edges, tc_bet_sizes)
        
        # Calculate weighted variance per hand
        variance_per_hand = self._calculate_weighted_variance(tc_frequencies, tc_edges, tc_bet_sizes)
        
        # Calculate standard deviation
        sd_per_hand = math.sqrt(variance_per_hand)
        
        # Calculate Risk of Ruin using the exponential formula
        if variance_per_hand > 0 and ev_per_hand != 0:
            # RoR = exp(-2 * bankroll * EV / variance)
            ror_exponential = math.exp(-2 * bankroll * ev_per_hand / variance_per_hand)
        else:
            ror_exponential = 1.0 if ev_per_hand <= 0 else 0.0
        
        # Calculate alternative RoR using normal approximation for comparison
        if sd_per_hand > 0 and ev_per_hand > 0:
            # Z-score for ruin: (0 - bankroll) / (sd * sqrt(hands))
            # For long-term play, approximate hands needed for ruin
            hands_to_ruin_estimate = (bankroll / abs(ev_per_hand)) if ev_per_hand != 0 else float('inf')
            if hands_to_ruin_estimate != float('inf'):
                z_score = -bankroll / (sd_per_hand * math.sqrt(hands_to_ruin_estimate))
                # Convert to probability using normal CDF approximation
                ror_normal = 0.5 * math.erfc(-z_score / math.sqrt(2))
            else:
                ror_normal = 0.0
        else:
            ror_normal = 1.0 if ev_per_hand <= 0 else 0.0
        
        # Calculate Kelly fraction for reference
        kelly_fraction = ev_per_hand / variance_per_hand if variance_per_hand > 0 else 0
        
        # Calculate average bet size
        avg_bet_size = sum(freq * tc_bet_sizes.get(tc, 0) for tc, freq in tc_frequencies.items())
        
        return {
            'risk_of_ruin_exponential': ror_exponential,
            'risk_of_ruin_normal_approx': ror_normal,
            'expected_value_per_hand': ev_per_hand,
            'variance_per_hand': variance_per_hand,
            'standard_deviation_per_hand': sd_per_hand,
            'kelly_fraction': kelly_fraction,
            'average_bet_size': avg_bet_size,
            'bankroll_in_units': bankroll,
            'is_positive_ev': ev_per_hand > 0
        }
    
    def _calculate_weighted_ev(self, tc_frequencies: Dict[int, float], 
                              tc_edges: Dict[int, float], 
                              tc_bet_sizes: Dict[int, float]) -> float:
        """Calculate weighted expected value per hand"""
        ev = 0.0
        for tc, frequency in tc_frequencies.items():
            edge = tc_edges.get(tc, 0.0)
            bet_size = tc_bet_sizes.get(tc, 0.0)
            # EV contribution = frequency × edge × bet_size
            ev += frequency * edge * bet_size
        return ev
    
    def _calculate_weighted_variance(self, tc_frequencies: Dict[int, float],
                                   tc_edges: Dict[int, float],
                                   tc_bet_sizes: Dict[int, float]) -> float:
        """Calculate weighted variance per hand"""
        variance = 0.0
        
        for tc, frequency in tc_frequencies.items():
            bet_size = tc_bet_sizes.get(tc, 0.0)
            edge = tc_edges.get(tc, 0.0)
            
            # Variance for this true count = (bet_size * base_sd)²
            # The standard deviation scales with bet size
            tc_variance = (bet_size * self.base_sd_per_unit) ** 2
            
            # Weight by frequency
            variance += frequency * tc_variance
        
        return variance
    
    def _validate_inputs(self, tc_frequencies: Dict[int, float],
                        tc_edges: Dict[int, float],
                        tc_bet_sizes: Dict[int, float],
                        bankroll: float) -> None:
        """Validate input parameters"""
        if bankroll <= 0:
            raise ValueError("Bankroll must be positive")
        
        if not tc_frequencies:
            raise ValueError("True count frequencies cannot be empty")
        
        # Normalize frequencies to sum to 1.0
        freq_sum = sum(tc_frequencies.values())
        if freq_sum > 0:
            # Normalize all frequencies so they sum to 1.0
            for tc in tc_frequencies:
                tc_frequencies[tc] = tc_frequencies[tc] / freq_sum
        
        # Ensure all required true counts have corresponding data
        for tc in tc_frequencies:
            if tc not in tc_edges:
                raise ValueError(f"Missing edge data for true count {tc}")
            if tc not in tc_bet_sizes:
                raise ValueError(f"Missing bet size data for true count {tc}")


def format_ror_results(results: Dict[str, float]) -> str:
    """
    Format RoR calculation results for easy reading
    
    Args:
        results: Dictionary from calculate_ror()
        
    Returns:
        Formatted string with results
    """
    
    ror_pct = results['risk_of_ruin_exponential'] * 100
    ror_normal_pct = results['risk_of_ruin_normal_approx'] * 100
    ev_per_100_hands = results['expected_value_per_hand'] * 100
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    RISK OF RUIN ANALYSIS                    ║
╠══════════════════════════════════════════════════════════════╣
║ Primary Risk of Ruin (Exponential):  {ror_pct:8.4f}%          ║
║ Alternative RoR (Normal Approx):     {ror_normal_pct:8.4f}%          ║
║                                                              ║
║ Expected Value per Hand:             {results['expected_value_per_hand']:8.6f} units ║
║ Expected Value per 100 Hands:       {ev_per_100_hands:8.4f} units ║
║ Standard Deviation per Hand:         {results['standard_deviation_per_hand']:8.4f} units ║
║ Variance per Hand:                   {results['variance_per_hand']:8.4f} units² ║
║                                                              ║
║ Average Bet Size:                    {results['average_bet_size']:8.2f} units ║
║ Bankroll:                            {results['bankroll_in_units']:8.0f} units ║
║ Kelly Fraction:                      {results['kelly_fraction']:8.6f}        ║
║                                                              ║
║ Positive Expected Value:             {'Yes' if results['is_positive_ev'] else 'No':>8}        ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    if results['is_positive_ev']:
        output += "\n✅ This betting strategy has positive expected value!"
    else:
        output += "\n❌ Warning: This betting strategy has negative expected value."
        
    if ror_pct < 1:
        output += f"\n✅ Very low risk of ruin ({ror_pct:.4f}%)"
    elif ror_pct < 5:
        output += f"\n⚠️  Low risk of ruin ({ror_pct:.4f}%)"
    elif ror_pct < 13.5:  # Kelly criterion typically suggests < 13.5% RoR
        output += f"\n⚠️  Moderate risk of ruin ({ror_pct:.4f}%)"
    else:
        output += f"\n🚨 High risk of ruin ({ror_pct:.4f}%) - Consider larger bankroll"
    
    return output


# Example usage and testing
if __name__ == "__main__":
    # Example data - replace with actual simulation results
    example_tc_frequencies = {
        -2: 0.05, -1: 0.15, 0: 0.30, 1: 0.25, 2: 0.15, 3: 0.07, 4: 0.03
    }
    
    example_tc_edges = {
        -2: -0.015, -1: -0.008, 0: -0.002, 1: 0.005, 2: 0.012, 3: 0.020, 4: 0.028
    }
    
    example_tc_bet_sizes = {
        -2: 0, -1: 0, 0: 0, 1: 1, 2: 2, 3: 4, 4: 8  # Sit out negative counts
    }
    
    calculator = RiskOfRuinCalculator()
    results = calculator.calculate_ror(
        tc_frequencies=example_tc_frequencies,
        tc_edges=example_tc_edges,
        tc_bet_sizes=example_tc_bet_sizes,
        bankroll=500
    )
    
    print(format_ror_results(results))