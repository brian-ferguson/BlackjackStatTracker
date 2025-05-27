"""
Test Risk of Ruin with actual CSV data to fix the parsing issue
"""

from risk_calculator import RiskOfRuinCalculator

def test_with_real_csv():
    # Read actual CSV file
    with open('attached_assets/2decks-nopenetration.csv', 'r') as f:
        csv_content = f.read()
    
    print("Testing with real CSV data...")
    
    # Parse manually to understand the format
    tc_frequencies = {}
    tc_edges = {}
    
    lines = csv_content.strip().split('\n')
    header_found = False
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('True Count,'):
            header_found = True
            continue
            
        if header_found:
            # Remove quotes and split
            line = line.replace('"', '').replace(',', '', 2)  # Remove first 2 commas from numbers
            parts = line.split(',')
            
            if len(parts) >= 6:
                try:
                    tc = int(parts[0])
                    frequency = int(parts[1])
                    percentage = float(parts[2])
                    edge = float(parts[3])
                    
                    if frequency > 0:
                        tc_frequencies[tc] = percentage / 100.0
                        tc_edges[tc] = edge
                except:
                    continue
    
    print(f"Parsed {len(tc_frequencies)} true count entries")
    
    # Test bet spread
    bet_spread = {
        -10: 0, -9: 0, -8: 0, -7: 0, -6: 0, -5: 0, -4: 0, -3: 0, -2: 0, -1: 0, 0: 0,
        1: 5, 2: 10, 3: 15, 4: 25, 5: 25, 6: 25, 7: 25, 8: 25, 9: 25, 10: 25
    }
    
    # Test different bankrolls
    calculator = RiskOfRuinCalculator()
    bankrolls = [1000, 2000, 5000, 10000]
    
    for bankroll in bankrolls:
        results = calculator.calculate_ror(
            tc_frequencies=tc_frequencies,
            tc_edges=tc_edges,
            tc_bet_sizes=bet_spread,
            bankroll=bankroll
        )
        
        print(f"Bankroll ${bankroll}: RoR = {results['risk_of_ruin_exponential']*100:.4f}%")

if __name__ == "__main__":
    test_with_real_csv()