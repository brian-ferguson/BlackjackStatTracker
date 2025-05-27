"""
Simple fix for Risk of Ruin calculation using your actual CSV data
"""

from flask import Flask, request, jsonify
from risk_calculator import RiskOfRuinCalculator
import csv
import io

def read_csv_data(csv_file_path):
    """Read simulation data from CSV file"""
    tc_frequencies = {}
    tc_edges = {}
    
    with open(csv_file_path, 'r') as file:
        content = file.read()
        
    lines = content.strip().split('\n')
    header_found = False
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if 'True Count,Frequency,Percentage,Player Edge' in line:
            header_found = True
            continue
            
        if header_found:
            line = line.replace('"', '')
            parts = line.split(',')
            
            if len(parts) >= 4:
                try:
                    tc = int(parts[0])
                    frequency = int(parts[1].replace(',', ''))
                    percentage = float(parts[2])
                    edge = float(parts[3])
                    
                    if frequency > 0:
                        tc_frequencies[tc] = percentage / 100.0
                        tc_edges[tc] = edge
                except:
                    continue
    
    return tc_frequencies, tc_edges

def test_ror_calculation():
    """Test Risk of Ruin with your actual data"""
    
    # Use your 2-deck no penetration data
    tc_frequencies, tc_edges = read_csv_data('attached_assets/2decks-nopenetration.csv')
    
    print(f"Loaded {len(tc_frequencies)} true count entries")
    
    # Your bet spread: TC<=0=$0, TC1=$5, TC2=$10, TC3=$15, TC4=$25, TC5+=$25
    bet_spread = {}
    for tc in range(-15, 16):
        if tc <= 0:
            bet_spread[tc] = 0  # Sit out
        elif tc == 1:
            bet_spread[tc] = 5
        elif tc == 2:
            bet_spread[tc] = 10
        elif tc == 3:
            bet_spread[tc] = 15
        elif tc == 4:
            bet_spread[tc] = 25
        else:  # tc >= 5
            bet_spread[tc] = 25
    
    calculator = RiskOfRuinCalculator()
    
    # Test different bankrolls
    bankrolls = [500, 1000, 2000, 5000, 10000]
    
    print("\nRisk of Ruin Results:")
    print("=" * 40)
    
    for bankroll in bankrolls:
        try:
            results = calculator.calculate_ror(
                tc_frequencies=tc_frequencies,
                tc_edges=tc_edges,
                tc_bet_sizes=bet_spread,
                bankroll=bankroll
            )
            
            ror_percent = results['risk_of_ruin_exponential'] * 100
            ev_per_hand = results['expected_value_per_hand']
            
            print(f"Bankroll: ${bankroll:,} → RoR: {ror_percent:.2f}% (EV: ${ev_per_hand:.4f}/hand)")
            
        except Exception as e:
            print(f"Error with ${bankroll}: {e}")

if __name__ == "__main__":
    test_ror_calculation()