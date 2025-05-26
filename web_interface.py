"""
Web interface for the blackjack simulation
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import threading
import time
from datetime import datetime
import csv
import zipfile
import io

from blackjack_simulator import BlackjackSimulator
from analysis import SimulationAnalyzer
from utils import validate_simulation_parameters, estimate_simulation_time

# Global variables for tracking simulation progress
simulation_status = {
    'running': False,
    'progress': 0,
    'current_config': '',
    'total_configs': 0,
    'completed_configs': 0,
    'start_time': None,
    'results': None,
    'error': None
}

def create_web_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/api/start_simulation', methods=['POST'])
    def start_simulation():
        """Start a new fast simulation with custom bet spread"""
        global simulation_status
        
        if simulation_status['running']:
            return jsonify({'error': 'Simulation already running'}), 400
        
        try:
            data = request.json
            bet_spread = data.get('bet_spread', {
                'tc_neg': 0, 'tc_1': 5, 'tc_2': 10, 
                'tc_3': 15, 'tc_4': 25, 'tc_5plus': 25
            })
            num_shoes = data.get('num_shoes', 100000)
            
            # Validate parameters
            errors, valid_combinations = validate_simulation_parameters(deck_counts, penetrations)
            if errors:
                return jsonify({'error': '; '.join(errors)}), 400
            
            # Reset status
            simulation_status = {
                'running': True,
                'progress': 0,
                'current_config': '',
                'total_configs': len(valid_combinations),
                'completed_configs': 0,
                'start_time': datetime.now(),
                'results': None,
                'error': None
            }
            
            # Start simulation in background thread
            thread = threading.Thread(
                target=run_simulation_background,
                args=(deck_counts, penetrations, hands_per_config, num_processes)
            )
            thread.daemon = True
            thread.start()
            
            estimated_time = estimate_simulation_time(len(valid_combinations), hands_per_config)
            
            return jsonify({
                'message': 'Simulation started',
                'total_configs': len(valid_combinations),
                'estimated_time': estimated_time
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/simulation_status')
    def get_simulation_status():
        """Get current simulation status"""
        global simulation_status
        
        status = simulation_status.copy()
        
        # Calculate elapsed time
        if status['start_time']:
            elapsed = datetime.now() - status['start_time']
            status['elapsed_time'] = str(elapsed).split('.')[0]  # Remove microseconds
        
        return jsonify(status)
    
    @app.route('/api/stop_simulation', methods=['POST'])
    def stop_simulation():
        """Stop current simulation"""
        global simulation_status
        
        simulation_status['running'] = False
        simulation_status['error'] = 'Simulation stopped by user'
        
        return jsonify({'message': 'Simulation stopped'})
    
    @app.route('/api/download_results')
    def download_results():
        """Download simulation results as ZIP file"""
        
        if not os.path.exists('simulation_results'):
            return jsonify({'error': 'No results available'}), 404
        
        # Create ZIP file in memory
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all CSV files from simulation_results
            for root, dirs, files in os.walk('simulation_results'):
                for file in files:
                    if file.endswith('.csv'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, 'simulation_results')
                        zf.write(file_path, arcname)
            
            # Add analysis results if available
            if os.path.exists('analysis_results'):
                for root, dirs, files in os.walk('analysis_results'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = f"analysis/{os.path.relpath(file_path, 'analysis_results')}"
                        zf.write(file_path, arcname)
        
        memory_file.seek(0)
        
        return send_file(
            io.BytesIO(memory_file.read()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'blackjack_simulation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
    
    @app.route('/api/results_summary')
    def get_results_summary():
        """Get summary of simulation results"""
        
        if not os.path.exists('simulation_results'):
            return jsonify({'error': 'No results available'}), 404
        
        try:
            # Count result files
            result_files = [f for f in os.listdir('simulation_results') if f.endswith('.csv')]
            
            # Read a sample result to get structure
            sample_data = []
            if result_files:
                sample_file = os.path.join('simulation_results', result_files[0])
                with open(sample_file, 'r') as f:
                    reader = csv.reader(f)
                    lines = list(reader)
                    
                    # Find data start (after metadata)
                    data_start = 0
                    for i, line in enumerate(lines):
                        if line and line[0] == 'True Count':
                            data_start = i + 1
                            break
                    
                    # Read sample data
                    for line in lines[data_start:data_start + 5]:  # First 5 data rows
                        if len(line) >= 2:
                            sample_data.append({
                                'true_count': line[0],
                                'percentage': line[1]
                            })
            
            return jsonify({
                'total_files': len(result_files),
                'sample_data': sample_data,
                'files': result_files[:10]  # First 10 filenames
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def run_simulation_background(deck_counts, penetrations, hands_per_config, num_processes):
    """Run simulation in background thread"""
    global simulation_status
    
    try:
        simulator = BlackjackSimulator(num_processes=num_processes)
        
        # Track progress
        total_configs = len(deck_counts) * len(penetrations)
        completed = 0
        
        results = {}
        
        for deck_count in deck_counts:
            for penetration in penetrations:
                if not simulation_status['running']:
                    return
                
                # Skip invalid combinations
                if penetration >= deck_count:
                    continue
                
                # Update status
                simulation_status['current_config'] = f"{deck_count} decks, {penetration} penetration"
                simulation_status['progress'] = (completed / total_configs) * 100
                
                # Run simulation for this configuration
                result = simulator._simulate_configuration(deck_count, penetration, hands_per_config)
                results[(deck_count, penetration)] = result
                
                # Save individual result
                simulator._save_configuration_results(deck_count, penetration, result)
                
                completed += 1
                simulation_status['completed_configs'] = completed
        
        # Generate analysis
        if results and simulation_status['running']:
            analyzer = SimulationAnalyzer(results)
            analyzer.generate_analysis_report()
        
        # Mark as complete
        simulation_status['running'] = False
        simulation_status['progress'] = 100
        simulation_status['results'] = results
        simulation_status['current_config'] = 'Completed'
        
    except Exception as e:
        simulation_status['running'] = False
        simulation_status['error'] = str(e)
        simulation_status['current_config'] = 'Error'
