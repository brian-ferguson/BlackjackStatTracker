// Blackjack Simulation Web Interface JavaScript

class SimulationController {
    constructor() {
        this.isRunning = false;
        this.statusUpdateInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Start simulation button
        document.getElementById('start-simulation').addEventListener('click', () => {
            this.startSimulation();
        });

        // Stop simulation button
        document.getElementById('stop-simulation').addEventListener('click', () => {
            this.stopSimulation();
        });

        // Download results button
        document.getElementById('download-results').addEventListener('click', () => {
            this.downloadResults();
        });

        // Deck count selection helpers
        this.addSelectionHelpers();
    }

    addSelectionHelpers() {
        // Add select all/none buttons for deck counts
        const deckSelection = document.querySelector('.deck-selection');
        if (deckSelection) {
            const helperDiv = document.createElement('div');
            helperDiv.className = 'mt-2';
            helperDiv.innerHTML = `
                <small>
                    <a href="#" id="select-all-decks" class="text-decoration-none me-2">Select All</a>
                    <a href="#" id="select-none-decks" class="text-decoration-none">Select None</a>
                </small>
            `;
            deckSelection.appendChild(helperDiv);

            document.getElementById('select-all-decks').addEventListener('click', (e) => {
                e.preventDefault();
                this.selectAllDecks(true);
            });

            document.getElementById('select-none-decks').addEventListener('click', (e) => {
                e.preventDefault();
                this.selectAllDecks(false);
            });
        }

        // Add select all/none buttons for penetrations
        const penSelection = document.querySelector('.penetration-selection');
        if (penSelection) {
            const helperDiv = document.createElement('div');
            helperDiv.className = 'mt-2';
            helperDiv.innerHTML = `
                <small>
                    <a href="#" id="select-all-pens" class="text-decoration-none me-2">Select All</a>
                    <a href="#" id="select-none-pens" class="text-decoration-none">Select None</a>
                </small>
            `;
            penSelection.appendChild(helperDiv);

            document.getElementById('select-all-pens').addEventListener('click', (e) => {
                e.preventDefault();
                this.selectAllPenetrations(true);
            });

            document.getElementById('select-none-pens').addEventListener('click', (e) => {
                e.preventDefault();
                this.selectAllPenetrations(false);
            });
        }
    }

    selectAllDecks(select) {
        const checkboxes = document.querySelectorAll('.deck-selection input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = select);
    }

    selectAllPenetrations(select) {
        const checkboxes = document.querySelectorAll('.penetration-selection input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = select);
    }

    getSelectedDeckCounts() {
        const checkboxes = document.querySelectorAll('.deck-selection input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => parseInt(cb.value));
    }

    getSelectedPenetrations() {
        const checkboxes = document.querySelectorAll('.penetration-selection input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => parseFloat(cb.value));
    }

    validateConfiguration() {
        const deckCounts = this.getSelectedDeckCounts();
        const penetrations = this.getSelectedPenetrations();

        if (deckCounts.length === 0) {
            return { valid: false, message: 'Please select at least one deck count.' };
        }

        if (penetrations.length === 0) {
            return { valid: false, message: 'Please select at least one penetration level.' };
        }

        // Check for valid combinations
        let validCombinations = 0;
        for (const deck of deckCounts) {
            for (const pen of penetrations) {
                if (pen < deck) {
                    validCombinations++;
                }
            }
        }

        if (validCombinations === 0) {
            return { 
                valid: false, 
                message: 'No valid combinations found. Penetration must be less than deck count.' 
            };
        }

        return { valid: true, combinations: validCombinations };
    }

    async startSimulation() {
        // Validate configuration
        const validation = this.validateConfiguration();
        if (!validation.valid) {
            alert(validation.message);
            return;
        }

        // Prepare simulation parameters
        const deckCounts = this.getSelectedDeckCounts();
        const penetrations = this.getSelectedPenetrations();
        const handsPerConfig = parseInt(document.getElementById('hands-per-config').value);
        const numProcesses = document.getElementById('num-processes').value || null;

        const params = {
            deck_counts: deckCounts,
            penetrations: penetrations,
            hands_per_config: handsPerConfig,
            num_processes: numProcesses ? parseInt(numProcesses) : null
        };

        try {
            const response = await fetch('/api/start_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            const result = await response.json();

            if (response.ok) {
                this.isRunning = true;
                this.updateUIForRunningState();
                this.startStatusUpdates();
                this.showEstimation(validation.combinations, handsPerConfig, result.estimated_time);
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            alert(`Error starting simulation: ${error.message}`);
        }
    }

    async stopSimulation() {
        try {
            const response = await fetch('/api/stop_simulation', {
                method: 'POST'
            });

            if (response.ok) {
                this.isRunning = false;
                this.updateUIForStoppedState();
                this.stopStatusUpdates();
            }
        } catch (error) {
            alert(`Error stopping simulation: ${error.message}`);
        }
    }

    updateUIForRunningState() {
        document.getElementById('start-simulation').style.display = 'none';
        document.getElementById('stop-simulation').style.display = 'block';
        
        // Disable configuration inputs
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => input.disabled = true);
    }

    updateUIForStoppedState() {
        document.getElementById('start-simulation').style.display = 'block';
        document.getElementById('stop-simulation').style.display = 'none';
        
        // Enable configuration inputs
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => input.disabled = false);
    }

    showEstimation(combinations, handsPerConfig, estimatedTime) {
        const totalHands = combinations * handsPerConfig;
        const statusContent = document.getElementById('status-content');
        
        statusContent.innerHTML = `
            <div class="estimation-info">
                <h6><i class="fas fa-calculator me-2"></i>Simulation Estimation</h6>
                <div class="row">
                    <div class="col-md-6">
                        <div class="status-item">
                            <span class="status-label">Configurations:</span>
                            <span class="status-value">${combinations.toLocaleString()}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Hands per Config:</span>
                            <span class="status-value">${handsPerConfig.toLocaleString()}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="status-item">
                            <span class="status-label">Total Hands:</span>
                            <span class="status-value">${totalHands.toLocaleString()}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Estimated Time:</span>
                            <span class="status-value">${estimatedTime}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    startStatusUpdates() {
        this.statusUpdateInterval = setInterval(() => {
            this.updateStatus();
        }, 2000); // Update every 2 seconds
    }

    stopStatusUpdates() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
            this.statusUpdateInterval = null;
        }
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/simulation_status');
            const status = await response.json();

            this.displayStatus(status);

            // Check if simulation is complete
            if (!status.running && this.isRunning) {
                this.isRunning = false;
                this.updateUIForStoppedState();
                this.stopStatusUpdates();
                
                if (status.error) {
                    this.showError(status.error);
                } else {
                    this.showCompletion();
                    this.loadResultsSummary();
                }
            }
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    displayStatus(status) {
        const statusContent = document.getElementById('status-content');

        if (status.running) {
            statusContent.innerHTML = `
                <div class="alert alert-info">
                    <div class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm me-3" role="status"></div>
                        <div class="flex-grow-1">
                            <strong>Simulation Running</strong><br>
                            <small>${status.current_config}</small>
                        </div>
                    </div>
                </div>
                <div class="progress mb-3">
                    <div class="progress-bar" role="progressbar" 
                         style="width: ${status.progress}%" 
                         aria-valuenow="${status.progress}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${status.progress.toFixed(1)}%
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="status-item">
                            <span class="status-label">Progress:</span>
                            <span class="status-value">${status.completed_configs}/${status.total_configs}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Elapsed Time:</span>
                            <span class="status-value">${status.elapsed_time || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="status-item">
                            <span class="status-label">Current Config:</span>
                            <span class="status-value">${status.current_config || 'Starting...'}</span>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    showError(error) {
        const statusContent = document.getElementById('status-content');
        statusContent.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Simulation Error:</strong> ${error}
            </div>
        `;
    }

    showCompletion() {
        const statusContent = document.getElementById('status-content');
        statusContent.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Simulation Completed Successfully!</strong><br>
                <small>Results are ready for download.</small>
            </div>
        `;
        
        // Show results card
        document.getElementById('results-card').style.display = 'block';
    }

    async loadResultsSummary() {
        try {
            const response = await fetch('/api/results_summary');
            
            if (response.ok) {
                const summary = await response.json();
                this.displayResultsSummary(summary);
            } else {
                console.error('Failed to load results summary');
            }
        } catch (error) {
            console.error('Error loading results summary:', error);
        }
    }

    displayResultsSummary(summary) {
        const summaryDiv = document.getElementById('results-summary');
        
        let sampleTable = '';
        if (summary.sample_data && summary.sample_data.length > 0) {
            sampleTable = `
                <h6>Sample Results Preview:</h6>
                <div class="table-responsive">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>True Count</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${summary.sample_data.map(row => `
                                <tr>
                                    <td>${row.true_count}</td>
                                    <td>${row.percentage}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        summaryDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Results Summary:</h6>
                    <ul class="list-unstyled">
                        <li><strong>Total Files Generated:</strong> ${summary.total_files}</li>
                        <li><strong>Individual Configuration Files:</strong> CSV format</li>
                        <li><strong>Analysis Reports:</strong> Included</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    ${sampleTable}
                </div>
            </div>
        `;
    }

    async downloadResults() {
        try {
            // Show loading state
            const button = document.getElementById('download-results');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Preparing Download...';
            button.disabled = true;

            const response = await fetch('/api/download_results');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'simulation_results.zip';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                const error = await response.json();
                alert(`Error downloading results: ${error.error}`);
            }

            // Restore button state
            button.innerHTML = originalText;
            button.disabled = false;

        } catch (error) {
            alert(`Error downloading results: ${error.message}`);
            
            // Restore button state
            const button = document.getElementById('download-results');
            button.innerHTML = '<i class="fas fa-download me-2"></i>Download All Results';
            button.disabled = false;
        }
    }
}

// Initialize the simulation controller when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SimulationController();
});
