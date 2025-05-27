#!/usr/bin/env python3
"""
Fixed web interface for custom bet spread simulations and risk analysis
"""

from flask import Flask, render_template, request, jsonify
import threading
import time
import os
import csv
import math
from custom_simulation import run_custom_simulation
from risk_calculator import RiskOfRuinCalculator, format_ror_results

app = Flask(__name__)

# Global variables for simulation status
simulation_status = {
    'running': False,
    'progress': 0,
    'current_config': '',
    'total_configs': 0,
    'completed_configs': 0,
    'message': 'Ready to start simulation',
    'folder_name': '',
    'error': None
}

simulation_thread = None

@app.route('/')
def index():
    """Main page with working JavaScript"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom Blackjack Simulation</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            h2 { color: #444; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, button { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            input[type="number"] { width: 80px; }
            select { width: 150px; }
            button { background: #007bff; color: white; border: none; padding: 15px 30px; font-size: 16px; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .bet-spread { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 10px 0; }
            .status { margin: 20px 0; padding: 15px; border-radius: 5px; }
            .status.info { background: #d1ecf1; border: 1px solid #bee5eb; }
            .status.success { background: #d4edda; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; border: 1px solid #f5c6cb; }
            .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }
            .progress-bar { height: 100%; background: #28a745; transition: width 0.3s; }
            .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            .results-table th, .results-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .results-table th { background: #f8f9fa; }
            .metric-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
            .metric-box { padding: 20px; background: #f8f9fa; border-radius: 5px; text-align: center; }
            .metric-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
            .section { margin: 40px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🃏 Custom Blackjack Simulation & Risk Analysis</h1>
            
            <!-- Simulation Section -->
            <div class="section">
                <h2>🎯 Run New Simulation</h2>
                
                <div class="form-group">
                    <label>Number of Decks in Shoe:</label>
                    <select id="deck-count">
                        <option value="1">1 Deck</option>
                        <option value="2" selected>2 Decks</option>
                        <option value="3">3 Decks</option>
                        <option value="4">4 Decks</option>
                        <option value="6">6 Decks</option>
                        <option value="8">8 Decks</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Penetration (decks dealt before shuffle):</label>
                    <select id="penetration">
                        <option value="0" selected>No Penetration (all cards)</option>
                        <option value="0.25">0.25 decks</option>
                        <option value="0.5">0.5 decks</option>
                        <option value="0.75">0.75 decks</option>
                        <option value="1.0">1.0 deck</option>
                        <option value="1.25">1.25 decks</option>
                        <option value="1.5">1.5 decks</option>
                        <option value="1.75">1.75 decks</option>
                        <option value="2.0">2.0 decks</option>
                        <option value="2.25">2.25 decks</option>
                        <option value="2.5">2.5 decks</option>
                        <option value="2.75">2.75 decks</option>
                        <option value="3.0">3.0 decks</option>
                        <option value="3.25">3.25 decks</option>
                        <option value="3.5">3.5 decks</option>
                        <option value="3.75">3.75 decks</option>
                        <option value="4.0">4.0 decks</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Number of Shoes to Simulate:</label>
                    <select id="num-shoes">
                        <option value="1000">1,000 (Quick Test)</option>
                        <option value="10000">10,000 (Medium Test)</option>
                        <option value="100000" selected>100,000 (Default)</option>
                        <option value="1000000">1,000,000 (Full Study)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Custom Bet Spread (in dollars):</label>
                    <div class="bet-spread">
                        <div>
                            <label>TC ≤ 0:</label>
                            <input type="number" id="bet-tc-neg" value="0" min="0" step="5">
                        </div>
                        <div>
                            <label>TC +1:</label>
                            <input type="number" id="bet-tc-1" value="5" min="0" step="5">
                        </div>
                        <div>
                            <label>TC +2:</label>
                            <input type="number" id="bet-tc-2" value="10" min="0" step="5">
                        </div>
                        <div>
                            <label>TC +3:</label>
                            <input type="number" id="bet-tc-3" value="15" min="0" step="5">
                        </div>
                        <div>
                            <label>TC +4:</label>
                            <input type="number" id="bet-tc-4" value="25" min="0" step="5">
                        </div>
                        <div>
                            <label>TC +5+:</label>
                            <input type="number" id="bet-tc-5plus" value="25" min="0" step="5">
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Table Rules:</label>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 10px 0;">
                        <div>
                            <input type="checkbox" id="dealer-hits-soft17" checked>
                            <label for="dealer-hits-soft17">Dealer Hits Soft 17</label>
                        </div>
                        <div>
                            <input type="checkbox" id="double-after-split" checked>
                            <label for="double-after-split">Double After Split</label>
                        </div>
                        <div>
                            <input type="checkbox" id="split-aces" checked>
                            <label for="split-aces">Split Aces Allowed</label>
                        </div>
                        <div>
                            <input type="checkbox" id="resplit-aces">
                            <label for="resplit-aces">Re-split Aces</label>
                        </div>
                        <div>
                            <input type="checkbox" id="surrender-allowed">
                            <label for="surrender-allowed">Surrender Allowed</label>
                        </div>
                        <div>
                            <label for="max-splits">Max Splits:</label>
                            <select id="max-splits">
                                <option value="1">1 (2 hands)</option>
                                <option value="2">2 (3 hands)</option>
                                <option value="3" selected>3 (4 hands)</option>
                                <option value="4">4 (5 hands)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <button id="start-btn">🚀 Start Simulation</button>
                <button id="stop-btn" style="display:none;">⏹️ Stop Simulation</button>

                <div id="status" class="status info">
                    Ready to start simulation. Configure your bet spread and click Start!
                </div>

                <div id="progress-container" style="display:none;">
                    <div class="progress">
                        <div id="progress-bar" class="progress-bar" style="width: 0%"></div>
                    </div>
                    <p id="progress-text">0% complete</p>
                </div>

                <div id="results" style="display:none;">
                    <h3>📊 Results Ready!</h3>
                    <p>Your simulation results have been saved to folder: <strong id="folder-name"></strong></p>
                    <p>This folder contains the CSV file for your selected deck count and penetration configuration.</p>
                </div>
            </div>

            <!-- Risk Calculator Section -->
            <div class="section">
                <h2>📈 Risk of Ruin Calculator</h2>
                <p>Upload your simulation CSV file to calculate bankroll requirements:</p>

                <div class="form-group">
                    <label>Load Simulation Results:</label>
                    <input type="file" id="csv-file" accept=".csv">
                    <button onclick="loadFile()">📂 Load CSV File</button>
                </div>

                <div id="bankroll-calculator" style="display:none;">
                    <div class="form-group">
                        <label>Starting Bankroll ($):</label>
                        <input type="number" id="bankroll" value="10000" min="1000" step="1000">
                    </div>

                    <div class="form-group">
                        <label>Hands per Hour:</label>
                        <input type="number" id="hands-per-hour" value="100" min="50" max="200" step="10">
                        <small style="display: block; color: #666;">Typical range: 50-200 hands/hour</small>
                    </div>

                    <div class="form-group">
                        <label>Risk of Ruin Threshold (%):</label>
                        <input type="number" id="ror-threshold" value="5" min="1" max="50" step="1">
                        <small style="display: block; color: #666;">Percentage of bankroll loss that defines "ruin"</small>
                    </div>

                    <button id="calc-risk-btn">🧮 Calculate Risk Metrics</button>

                    <div id="risk-results" style="display:none;">
                        <h3>📊 Risk Analysis Results</h3>
                        <div class="metric-grid">
                            <div class="metric-box">
                                <div>Expected Hourly EV</div>
                                <div id="hourly-ev" class="metric-value" style="color: #28a745;">$0.00</div>
                            </div>
                            <div class="metric-box">
                                <div>Standard Deviation</div>
                                <div id="std-dev" class="metric-value" style="color: #007bff;">$0.00</div>
                            </div>
                            <div class="metric-box">
                                <div>N0 (Breakeven Hands)</div>
                                <div id="n0-hands" class="metric-value" style="color: #6f42c1;">0</div>
                            </div>
                            <div class="metric-box">
                                <div>Risk of Ruin</div>
                                <div id="risk-of-ruin" class="metric-value" style="color: #dc3545;">0.00%</div>
                            </div>
                        </div>
                        
                        <div>
                            <h4>📋 Detailed Breakdown</h4>
                            <table class="results-table" id="detailed-breakdown">
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let statusInterval;
            let simulationData = null;

            function getBetSpread() {
                return {
                    tc_neg: parseInt(document.getElementById('bet-tc-neg').value) || 0,
                    tc_1: parseInt(document.getElementById('bet-tc-1').value) || 0,
                    tc_2: parseInt(document.getElementById('bet-tc-2').value) || 0,
                    tc_3: parseInt(document.getElementById('bet-tc-3').value) || 0,
                    tc_4: parseInt(document.getElementById('bet-tc-4').value) || 0,
                    tc_5plus: parseInt(document.getElementById('bet-tc-5plus').value) || 0
                };
            }

            function getTableRules() {
                return {
                    dealer_hits_soft17: document.getElementById('dealer-hits-soft17').checked,
                    double_after_split: document.getElementById('double-after-split').checked,
                    split_aces: document.getElementById('split-aces').checked,
                    resplit_aces: document.getElementById('resplit-aces').checked,
                    surrender_allowed: document.getElementById('surrender-allowed').checked,
                    max_splits: parseInt(document.getElementById('max-splits').value)
                };
            }

            async function startSimulation() {
                const betSpread = getBetSpread();
                const tableRules = getTableRules();
                const numShoes = parseInt(document.getElementById('num-shoes').value);
                const deckCount = parseInt(document.getElementById('deck-count').value);
                const penetration = parseFloat(document.getElementById('penetration').value);

                const params = {
                    bet_spread: betSpread,
                    table_rules: tableRules,
                    num_shoes: numShoes,
                    deck_count: deckCount,
                    penetration: penetration
                };

                try {
                    const response = await fetch('/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(params)
                    });

                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('start-btn').style.display = 'none';
                        document.getElementById('stop-btn').style.display = 'inline-block';
                        document.getElementById('progress-container').style.display = 'block';
                        document.getElementById('results').style.display = 'none';
                        
                        statusInterval = setInterval(updateStatus, 2000);
                    } else {
                        updateStatusDiv(result.error, 'error');
                    }
                } catch (error) {
                    updateStatusDiv('Failed to start simulation: ' + error.message, 'error');
                }
            }

            async function stopSimulation() {
                try {
                    await fetch('/stop', { method: 'POST' });
                    clearInterval(statusInterval);
                    document.getElementById('start-btn').style.display = 'inline-block';
                    document.getElementById('stop-btn').style.display = 'none';
                    document.getElementById('progress-container').style.display = 'none';
                    updateStatusDiv('Simulation stopped', 'info');
                } catch (error) {
                    updateStatusDiv('Failed to stop simulation', 'error');
                }
            }

            async function updateStatus() {
                try {
                    const response = await fetch('/status');
                    const status = await response.json();
                    
                    if (status.running) {
                        const progress = (status.completed_configs / status.total_configs) * 100;
                        document.getElementById('progress-bar').style.width = progress + '%';
                        document.getElementById('progress-text').textContent = 
                            Math.round(progress) + '% complete - ' + status.current_config;
                        updateStatusDiv(status.message, 'info');
                    } else {
                        clearInterval(statusInterval);
                        document.getElementById('start-btn').style.display = 'inline-block';
                        document.getElementById('stop-btn').style.display = 'none';
                        document.getElementById('progress-container').style.display = 'none';
                        
                        if (status.error) {
                            updateStatusDiv('Error: ' + status.error, 'error');
                        } else if (status.folder_name) {
                            document.getElementById('results').style.display = 'block';
                            document.getElementById('folder-name').textContent = status.folder_name;
                            updateStatusDiv('Simulation completed successfully!', 'success');
                        }
                    }
                } catch (error) {
                    console.error('Status update failed:', error);
                }
            }

            function updateStatusDiv(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = 'status ' + type;
            }

            function loadFile() {
                const fileInput = document.getElementById('csv-file');
                const file = fileInput.files[0];
                
                if (!file) {
                    updateStatusDiv('Please select a CSV file first', 'error');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    const csvText = e.target.result;
                    simulationData = parseCSV(csvText);
                    
                    if (simulationData) {
                        document.getElementById('bankroll-calculator').style.display = 'block';
                        updateStatusDiv('CSV loaded successfully! Enter your parameters below.', 'success');
                    } else {
                        updateStatusDiv('Error parsing CSV file. Please check the format.', 'error');
                    }
                };
                reader.readAsText(file);
            }

            function parseCSV(csvText) {
                try {
                    const lines = csvText.split('\\n');
                    const data = {
                        deckCount: null,
                        penetration: null,
                        totalShoes: null,
                        totalHands: null,
                        betSpread: null,
                        trueCountData: []
                    };

                    // Parse header information
                    for (let line of lines) {
                        if (line.includes('Deck Count:')) {
                            data.deckCount = parseInt(line.split(':')[1].trim());
                        } else if (line.includes('Penetration:')) {
                            data.penetration = line.split(':')[1].trim();
                        } else if (line.includes('Total Shoes:')) {
                            data.totalShoes = parseInt(line.split(':')[1].replace(/[",]/g, '').trim());
                        } else if (line.includes('Total Hands:')) {
                            data.totalHands = parseInt(line.split(':')[1].replace(/[",]/g, '').trim());
                        } else if (line.includes('Bet Spread:')) {
                            data.betSpread = line.split(':')[1].trim();
                        }
                    }

                    // Parse true count data
                    let dataStarted = false;
                    for (let line of lines) {
                        if (line.startsWith('True Count,')) {
                            dataStarted = true;
                            continue;
                        }
                        
                        if (dataStarted && line.trim()) {
                            const parts = line.split(',');
                            if (parts.length >= 6) {
                                const tc = parseInt(parts[0]);
                                const frequency = parseInt(parts[1]);
                                const edge = parseFloat(parts[3]);
                                const profit = parseFloat(parts[4]);
                                const wagered = parseFloat(parts[5]);
                                
                                if (frequency > 0) {
                                    data.trueCountData.push({
                                        trueCount: tc,
                                        frequency: frequency,
                                        edge: edge,
                                        totalProfit: profit,
                                        totalWagered: wagered
                                    });
                                }
                            }
                        }
                    }

                    return data;
                } catch (error) {
                    console.error('Error parsing CSV:', error);
                    return null;
                }
            }

            function calculateRisk() {
                if (!simulationData) {
                    updateStatusDiv('Please load a CSV file first', 'error');
                    return;
                }

                const bankroll = parseFloat(document.getElementById('bankroll').value);
                const handsPerHour = parseInt(document.getElementById('hands-per-hour').value);
                const rorThreshold = parseFloat(document.getElementById('ror-threshold').value);

                // Calculate overall statistics
                let totalProfit = 0;
                let totalWagered = 0;
                let totalHands = 0;

                for (let tcData of simulationData.trueCountData) {
                    totalProfit += tcData.totalProfit;
                    totalWagered += tcData.totalWagered;
                    totalHands += tcData.frequency;
                }

                // Calculate key metrics
                const overallEdge = totalProfit / totalWagered;
                const avgBetPerHand = totalWagered / totalHands;
                const hourlyEV = overallEdge * avgBetPerHand * handsPerHour;
                
                // Simplified standard deviation calculation
                const avgProfit = totalProfit / totalHands;
                const stdDev = Math.sqrt(avgBetPerHand * avgBetPerHand * 1.1); // Approximate
                const hourlyStdDev = stdDev * Math.sqrt(handsPerHour);
                
                // N0 calculation
                const n0 = Math.pow(stdDev / (avgProfit), 2);
                
                // Use the actual Risk of Ruin from the server calculation
                const riskOfRuin = data.ror_percentage;

                // Display results
                document.getElementById('hourly-ev').textContent = '$' + hourlyEV.toFixed(2);
                document.getElementById('std-dev').textContent = '$' + hourlyStdDev.toFixed(2);
                document.getElementById('n0-hands').textContent = Math.round(n0).toLocaleString();
                document.getElementById('risk-of-ruin').textContent = riskOfRuin.toFixed(2) + '%';

                // Detailed breakdown
                const breakdown = document.getElementById('detailed-breakdown');
                breakdown.innerHTML = `
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Overall Edge</td><td>${(overallEdge * 100).toFixed(4)}%</td></tr>
                    <tr><td>Average Bet</td><td>$${avgBetPerHand.toFixed(2)}</td></tr>
                    <tr><td>Total Hands Simulated</td><td>${totalHands.toLocaleString()}</td></tr>
                    <tr><td>Deck Configuration</td><td>${simulationData.deckCount} decks, ${simulationData.penetration}</td></tr>
                    <tr><td>Betting Strategy</td><td>${simulationData.betSpread || 'N/A'}</td></tr>
                    <tr><td>Bankroll</td><td>$${bankroll.toLocaleString()}</td></tr>
                    <tr><td>Hands per Hour</td><td>${handsPerHour}</td></tr>
                `;
                
                document.getElementById('risk-results').style.display = 'block';
            }

            // Add event listeners when page loads
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('start-btn').addEventListener('click', startSimulation);
                document.getElementById('stop-btn').addEventListener('click', stopSimulation);
                document.getElementById('calc-risk-btn').addEventListener('click', calculateRisk);
                
                // Find and add event listener for load button
                const loadBtn = document.querySelector('button[onclick="loadFile()"]');
                if (loadBtn) {
                    loadBtn.removeAttribute('onclick');
                    loadBtn.addEventListener('click', loadFile);
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/start', methods=['POST'])
def start_simulation():
    """Start custom simulation"""
    global simulation_status, simulation_thread
    
    if simulation_status['running']:
        return jsonify({'error': 'Simulation already running'}), 400
    
    data = request.json
    bet_spread = data.get('bet_spread', {})
    table_rules = data.get('table_rules', {})
    num_shoes = data.get('num_shoes', 100000)
    deck_count = data.get('deck_count', 2)
    penetration = data.get('penetration', 0)
    
    # Reset status for single configuration
    simulation_status = {
        'running': True,
        'progress': 0,
        'current_config': f'{deck_count} decks, {penetration} penetration',
        'total_configs': 1,
        'completed_configs': 0,
        'message': f'Starting {deck_count}-deck simulation with {penetration} penetration...',
        'folder_name': '',
        'error': None
    }
    
    # Start simulation thread
    simulation_thread = threading.Thread(
        target=run_simulation_thread,
        args=(bet_spread, table_rules, num_shoes, deck_count, penetration)
    )
    simulation_thread.start()
    
    return jsonify({'message': 'Simulation started'})

@app.route('/stop', methods=['POST'])
def stop_simulation():
    """Stop simulation"""
    global simulation_status
    simulation_status['running'] = False
    return jsonify({'message': 'Stop signal sent'})

@app.route('/status')
def get_status():
    """Get simulation status"""
    return jsonify(simulation_status)

def run_simulation_thread(bet_spread, table_rules, num_shoes, deck_count, penetration):
    """Run simulation in background thread for single configuration"""
    global simulation_status
    
    try:
        # Import here to avoid circular imports
        from custom_simulation import simulate_configuration_custom, save_results_custom, create_bet_spread_folder
        
        def progress_callback(progress):
            simulation_status['message'] = f'Progress: {progress:.1f}%'
        
        # Create folder name for this specific configuration
        folder_name = create_bet_spread_folder(bet_spread, num_shoes)
        config_name = f'{deck_count}decks-{penetration}penetration'
        
        simulation_status['current_config'] = config_name
        simulation_status['message'] = f'Running {config_name}...'
        
        # Run single configuration simulation
        true_count_stats, total_hands = simulate_configuration_custom(
            deck_count, penetration, num_shoes, bet_spread, table_rules, progress_callback
        )
        
        # Save results
        save_results_custom(deck_count, penetration, num_shoes, true_count_stats, total_hands, folder_name, bet_spread)
        
        simulation_status['running'] = False
        simulation_status['completed_configs'] = 1
        simulation_status['folder_name'] = folder_name
        simulation_status['message'] = f'Single configuration simulation completed! Results saved to {folder_name}'
        
    except Exception as e:
        simulation_status['running'] = False
        simulation_status['error'] = str(e)
        simulation_status['message'] = f'Simulation failed: {str(e)}'

@app.route('/calculate_risk', methods=['POST'])
def calculate_risk():
    """Calculate Risk of Ruin using actual simulation data"""
    try:
        data = request.json
        csv_content = data.get('csv_content', '')
        bankroll = float(data.get('bankroll', 1000))
        bet_spread_input = data.get('bet_spread', {})
        
        # Parse bet spread from form data
        bet_spread = parse_bet_spread_from_string(bet_spread_input)
        
        # Parse CSV content and extract data
        tc_frequencies, tc_edges = parse_csv_content(csv_content)
        
        if not tc_frequencies or not tc_edges:
            return jsonify({'error': 'Could not parse simulation data from CSV content'})
        
        # Calculate Risk of Ruin
        calculator = RiskOfRuinCalculator()
        results = calculator.calculate_ror(
            tc_frequencies=tc_frequencies,
            tc_edges=tc_edges,
            tc_bet_sizes=bet_spread,
            bankroll=bankroll
        )
        
        # Format results for web display
        formatted_results = {
            'ror_percentage': results['risk_of_ruin_exponential'] * 100,
            'ror_normal_percentage': results['risk_of_ruin_normal_approx'] * 100,
            'expected_value_per_hand': results['expected_value_per_hand'],
            'expected_value_per_100_hands': results['expected_value_per_hand'] * 100,
            'standard_deviation': results['standard_deviation_per_hand'],
            'variance': results['variance_per_hand'],
            'kelly_fraction': results['kelly_fraction'],
            'average_bet_size': results['average_bet_size'],
            'is_positive_ev': results['is_positive_ev'],
            'bankroll': bankroll,
            'formatted_output': format_ror_results(results)
        }
        
        return jsonify({'success': True, 'results': formatted_results})
        
    except Exception as e:
        return jsonify({'error': f'Error calculating Risk of Ruin: {str(e)}'})

def parse_bet_spread_from_string(bet_spread_input):
    """Parse bet spread from the web form into dictionary"""
    bet_spread = {}
    
    # Get bet spread from form data
    tc0_bet = float(bet_spread_input.get('tc0', 0))
    tc1_bet = float(bet_spread_input.get('tc1', 5))
    tc2_bet = float(bet_spread_input.get('tc2', 10))
    tc3_bet = float(bet_spread_input.get('tc3', 15))
    tc4_bet = float(bet_spread_input.get('tc4', 25))
    tc5plus_bet = float(bet_spread_input.get('tc5plus', 25))
    
    # Map to true count values
    bet_spread = {
        -5: 0, -4: 0, -3: 0, -2: 0, -1: 0,  # Sit out negative counts
        0: tc0_bet,
        1: tc1_bet,
        2: tc2_bet,
        3: tc3_bet,
        4: tc4_bet
    }
    
    # Apply TC5+ bet to all counts 5 and above
    for tc in range(5, 11):
        bet_spread[tc] = tc5plus_bet
            
    return bet_spread

def parse_csv_content(csv_content):
    """Parse CSV content string and extract true count data"""
    tc_frequencies = {}
    tc_edges = {}
    
    try:
        lines = csv_content.strip().split('\n')
        if len(lines) < 2:
            return None, None
            
        # Parse header to find column indices
        header = lines[0].split(',')
        tc_index = next((i for i, col in enumerate(header) if 'True Count' in col), None)
        freq_index = next((i for i, col in enumerate(header) if 'Frequency' in col), None)
        edge_index = next((i for i, col in enumerate(header) if 'Edge' in col), None)
        
        if tc_index is None or freq_index is None or edge_index is None:
            return None, None
        
        total_frequency = 0
        
        # Parse data rows
        for line in lines[1:]:
            if line.strip():
                parts = line.split(',')
                if len(parts) > max(tc_index, freq_index, edge_index):
                    tc = int(float(parts[tc_index]))
                    frequency = float(parts[freq_index])
                    edge = float(parts[edge_index])
                    
                    tc_frequencies[tc] = frequency
                    tc_edges[tc] = edge
                    total_frequency += frequency
        
        # Normalize frequencies to sum to 1.0
        if total_frequency > 0:
            for tc in tc_frequencies:
                tc_frequencies[tc] /= total_frequency
                
        return tc_frequencies, tc_edges
        
    except Exception as e:
        print(f"Error parsing CSV content: {e}")
        return None, None

def read_csv_data(csv_file_path):
    """Read simulation data from CSV file"""
    tc_frequencies = {}
    tc_edges = {}
    
    try:
        if not os.path.exists(csv_file_path):
            return None, None
            
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            total_frequency = 0
            
            for row in reader:
                tc = int(float(row['True Count']))
                frequency = float(row['Frequency'])
                edge = float(row['Edge'])
                
                tc_frequencies[tc] = frequency
                tc_edges[tc] = edge
                total_frequency += frequency
        
        # Normalize frequencies to sum to 1.0
        if total_frequency > 0:
            for tc in tc_frequencies:
                tc_frequencies[tc] /= total_frequency
                
        return tc_frequencies, tc_edges
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None, None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)