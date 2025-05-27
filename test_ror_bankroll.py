"""
Test Risk of Ruin calculation with different bankrolls to verify it changes properly
"""

from risk_calculator import RiskOfRuinCalculator

# Sample data that mimics what we'd get from simulation
tc_frequencies = {
    -5: 0.02, -4: 0.03, -3: 0.05, -2: 0.08, -1: 0.12, 0: 0.15,
    1: 0.25, 2: 0.15, 3: 0.08, 4: 0.04, 5: 0.02, 6: 0.01
}

tc_edges = {
    -5: -0.02, -4: -0.015, -3: -0.01, -2: -0.008, -1: -0.005, 0: -0.002,
    1: 0.005, 2: 0.012, 3: 0.018, 4: 0.025, 5: 0.032, 6: 0.040
}

# Your bet spread: TC<=0=$0, TC1=$5, TC2=$10, TC3=$15, TC4=$25, TC5+=$25
tc_bet_sizes = {
    -5: 0, -4: 0, -3: 0, -2: 0, -1: 0, 0: 0,
    1: 5, 2: 10, 3: 15, 4: 25, 5: 25, 6: 25
}

def test_different_bankrolls():
    """Test RoR with different bankroll amounts"""
    calculator = RiskOfRuinCalculator()
    
    bankrolls = [500, 1000, 1500, 2000, 3000, 5000]
    
    print("Testing Risk of Ruin with different bankrolls:")
    print("=" * 60)
    
    for bankroll in bankrolls:
        results = calculator.calculate_ror(
            tc_frequencies=tc_frequencies,
            tc_edges=tc_edges,
            tc_bet_sizes=tc_bet_sizes,
            bankroll=bankroll
        )
        
        ror_percent = results['risk_of_ruin_exponential'] * 100
        ev_per_hand = results['expected_value_per_hand']
        variance = results['variance_per_hand']
        
        print(f"Bankroll: ${bankroll:,}")
        print(f"  Risk of Ruin: {ror_percent:.4f}%")
        print(f"  EV per hand: ${ev_per_hand:.4f}")
        print(f"  Variance: {variance:.2f}")
        print(f"  Formula check: exp(-2 * {bankroll} * {ev_per_hand:.4f} / {variance:.2f}) = {results['risk_of_ruin_exponential']:.6f}")
        print()

if __name__ == "__main__":
    test_different_bankrolls()