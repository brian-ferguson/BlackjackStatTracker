#!/usr/bin/env python3
"""
Simple web interface for custom bet spread simulations
"""

from flask import Flask, render_template, request, jsonify
import threading
import time
import os
from custom_simulation import run_custom_simulation

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
    """Simple main page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom Blackjack Simulation</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, button { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            input[type="number"] { width: 80px; }
            select { width: 150px; }
            button { background: #007bff; color: white; border: none; padding: 15px 30px; font-size: 16px; cursor: pointer; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .bet-spread { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 10px 0; }
            .status { margin: 20px 0; padding: 15px; border-radius: 5px; }
            .status.info { background: #d1ecf1; border: 1px solid #bee5eb; }
            .status.success { background: #d4edda; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; border: 1px solid #f5c6cb; }
            .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }
            .progress-bar { height: 100%; background: #28a745; transition: width 0.3s; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🃏 Custom Blackjack Simulation</h1>
            
            <div class="form-group">
                <label>Number of Shoes per Configuration:</label>
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

            <button id="start-btn" onclick="startSimulation()">🚀 Start Simulation</button>
            <button id="stop-btn" onclick="stopSimulation()" style="display:none;">⏹️ Stop Simulation</button>

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
                <p>This folder contains all 54 CSV files with your custom bet spread analysis.</p>
            </div>
        </div>

        <script>
            let statusInterval;

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

            async function startSimulation() {
                const betSpread = getBetSpread();
                const numShoes = parseInt(document.getElementById('num-shoes').value);

                const params = {
                    bet_spread: betSpread,
                    num_shoes: numShoes
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
                        
                        // Start status updates
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
    num_shoes = data.get('num_shoes', 100000)
    
    # Reset status
    simulation_status = {
        'running': True,
        'progress': 0,
        'current_config': 'Starting...',
        'total_configs': 54,
        'completed_configs': 0,
        'message': 'Initializing simulation...',
        'folder_name': '',
        'error': None
    }
    
    # Start simulation thread
    simulation_thread = threading.Thread(
        target=run_simulation_thread,
        args=(bet_spread, num_shoes)
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

def run_simulation_thread(bet_spread, num_shoes):
    """Run simulation in background thread"""
    global simulation_status
    
    try:
        def progress_callback(completed, total, config_name):
            simulation_status['completed_configs'] = completed
            simulation_status['total_configs'] = total
            simulation_status['current_config'] = config_name
            simulation_status['message'] = f'Processing configuration {completed}/{total}: {config_name}'
        
        folder_name = run_custom_simulation(bet_spread, num_shoes, progress_callback)
        
        simulation_status['running'] = False
        simulation_status['folder_name'] = folder_name
        simulation_status['message'] = 'Simulation completed successfully!'
        
    except Exception as e:
        simulation_status['running'] = False
        simulation_status['error'] = str(e)
        simulation_status['message'] = f'Simulation failed: {str(e)}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)