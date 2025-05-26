#!/usr/bin/env python3
"""
Debug why edges are too low compared to standard Hi-Lo tables
"""

from custom_simulation import simulate_configuration_custom
import time

def test_different_penetrations():
    """Test how penetration affects edge calculations"""
    
    bet_spread = {
        'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
    }
    
    print("🔍 TESTING PENETRATION EFFECTS ON EDGE:")
    print("=" * 60)
    
    # Test different penetration levels
    penetrations = [0, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    
    for pen in penetrations:
        print(f"\n📊 Testing 6-deck, {pen} deck penetration (5,000 shoes)...")
        
        start_time = time.time()
        true_count_stats, total_hands = simulate_configuration_custom(
            deck_count=6, 
            penetration=pen, 
            num_shoes=5000, 
            bet_spread=bet_spread
        )
        elapsed_time = time.time() - start_time
        
        print(f"Completed in {elapsed_time:.1f}s, {total_hands:,} hands")
        
        # Show edges for key true counts
        for tc in [1, 2, 3, 4, 5, 6]:
            if tc in true_count_stats and true_count_stats[tc]['frequency'] > 0:
                stats = true_count_stats[tc]
                edge = (stats['total_profit'] / stats['total_wagered']) * 100 if stats['total_wagered'] > 0 else 0
                frequency = stats['frequency']
                print(f"  TC +{tc}: {edge:6.2f}% edge ({frequency:,} hands)")
        
        # Calculate overall edge for played hands
        total_profit = sum(stats['total_profit'] for tc, stats in true_count_stats.items() if tc > 0)
        total_wagered = sum(stats['total_wagered'] for tc, stats in true_count_stats.items() if tc > 0)
        overall_edge = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0
        print(f"  Overall Edge: {overall_edge:.3f}%")

def test_single_deck_deep_penetration():
    """Test single deck with very deep penetration for maximum edge"""
    
    bet_spread = {
        'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
    }
    
    print("\n" + "=" * 60)
    print("🔍 TESTING SINGLE DECK WITH DEEP PENETRATION:")
    print("=" * 60)
    
    # Single deck with 0.75 deck penetration (39 cards dealt)
    print("📊 Testing 1-deck, 0.75 deck penetration (10,000 shoes)...")
    
    start_time = time.time()
    true_count_stats, total_hands = simulate_configuration_custom(
        deck_count=1, 
        penetration=0.75, 
        num_shoes=10000, 
        bet_spread=bet_spread
    )
    elapsed_time = time.time() - start_time
    
    print(f"Completed in {elapsed_time:.1f}s, {total_hands:,} hands")
    print("\nEdge by True Count:")
    print("TC | Edge %  | Hands  | Expected")
    print("-" * 35)
    
    expected_edges = {1: 0.0, 2: 0.5, 3: 1.0, 4: 1.5, 5: 2.0, 6: 2.5}
    
    for tc in range(1, 7):
        if tc in true_count_stats and true_count_stats[tc]['frequency'] > 0:
            stats = true_count_stats[tc]
            edge = (stats['total_profit'] / stats['total_wagered']) * 100 if stats['total_wagered'] > 0 else 0
            frequency = stats['frequency']
            expected = expected_edges.get(tc, 0)
            status = "✓" if abs(edge - expected) < 1.0 else "✗"
            print(f"{tc:2d} | {edge:6.2f} | {frequency:6,} | {expected:6.1f} {status}")
        else:
            print(f"{tc:2d} | No data | No data | {expected_edges.get(tc, 0):6.1f}")

if __name__ == "__main__":
    test_different_penetrations()
    test_single_deck_deep_penetration()