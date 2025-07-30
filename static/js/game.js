// Crossword Battle Arena - Game Logic

class CrosswordGame {
    constructor() {
        this.gameState = {
            isActive: false,
            difficulty: 'medium',
            mode: 'quick_play',
            currentClue: null,
            puzzle: null,
            scores: { player: 0, ai: 0 },
            turn: 'player',
            streak: 0,
            hintsRemaining: 3
        };
        
        this.updateInterval = null;
        this.soundEnabled = true;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Answer input enter key
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && document.getElementById('answerModal').classList.contains('show')) {
                this.submitAnswer();
            }
        });
        
        // Real-time answer input formatting
        const answerInput = document.getElementById('answer-input');
        if (answerInput) {
            answerInput.addEventListener('input', (e) => {
                e.target.value = e.target.value.toUpperCase();
            });
        }
    }
    
    selectDifficulty(difficulty) {
        this.gameState.difficulty = difficulty;
        
        // Update button states
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-difficulty="${difficulty}"]`).classList.add('active');
        
        this.playSound('select');
    }
    
    selectMode(mode) {
        this.gameState.mode = mode;
        
        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        this.playSound('select');
    }
    
    async startGame() {
        try {
            this.showLoading('Starting game...');
            
            const response = await fetch('/start_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    difficulty: this.gameState.difficulty,
                    mode: this.gameState.mode
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.gameState.isActive = true;
                this.gameState.puzzle = data.puzzle;
                this.gameState.scores = { player: 0, ai: 0 };
                this.gameState.turn = 'player';
                this.gameState.streak = 0;
                this.gameState.hintsRemaining = 3;
                
                this.showGameBoard();
                this.renderPuzzle();
                this.startGameStateUpdates();
                
                this.playSound('start');
            } else {
                throw new Error(data.error || 'Failed to start game');
            }
        } catch (error) {
            console.error('Error starting game:', error);
            this.showError('Failed to start game. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    showGameBoard() {
        document.getElementById('game-setup').classList.add('d-none');
        document.getElementById('game-board').classList.remove('d-none');
    }
    
    renderPuzzle() {
        const puzzle = this.gameState.puzzle;
        
        // Set puzzle title
        document.getElementById('puzzle-title').textContent = puzzle.title;
        
        // Render crossword grid
        this.renderGrid(puzzle.size);
        
        // Render clues
        this.renderClues(puzzle.clues);
        
        // Update hints counter
        document.getElementById('hints-remaining').textContent = this.gameState.hintsRemaining;
    }
    
    renderGrid(size) {
        const gridContainer = document.getElementById('crossword-grid');
        gridContainer.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
        gridContainer.innerHTML = '';
        
        for (let i = 0; i < size; i++) {
            for (let j = 0; j < size; j++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell empty';
                cell.dataset.row = i;
                cell.dataset.col = j;
                cell.id = `cell-${i}-${j}`;
                gridContainer.appendChild(cell);
            }
        }
    }
    
    renderClues(clues) {
        const cluesContainer = document.getElementById('clues-container');
        cluesContainer.innerHTML = '';
        
        clues.forEach(clue => {
            const clueElement = document.createElement('div');
            clueElement.className = 'clue-item d-flex align-items-center';
            clueElement.dataset.clueId = clue.id;
            clueElement.onclick = () => this.showAnswerModal(clue);
            
            clueElement.innerHTML = `
                <span class="clue-number">${clue.id}.</span>
                <span class="clue-text">${clue.clue}</span>
                <span class="clue-length">${clue.length} letters</span>
                <span class="clue-points ms-2">${clue.points}pts</span>
            `;
            
            cluesContainer.appendChild(clueElement);
        });
    }
    
    showAnswerModal(clue) {
        if (this.gameState.turn !== 'player' || !this.gameState.isActive) {
            this.showError('It\'s not your turn!');
            return;
        }
        
        this.gameState.currentClue = clue;
        
        document.getElementById('modal-clue-text').textContent = clue.clue;
        document.getElementById('answer-length').textContent = clue.length;
        document.getElementById('answer-input').value = '';
        document.getElementById('hint-display').classList.add('d-none');
        
        const modal = new bootstrap.Modal(document.getElementById('answerModal'));
        modal.show();
        
        // Focus on input after modal is shown
        setTimeout(() => {
            document.getElementById('answer-input').focus();
        }, 300);
    }
    
    async submitAnswer() {
        const answer = document.getElementById('answer-input').value.trim();
        if (!answer) {
            this.showError('Please enter an answer');
            return;
        }
        
        try {
            this.showLoading('Checking answer...');
            
            const response = await fetch('/submit_answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    clue_id: this.gameState.currentClue.id,
                    answer: answer
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('answerModal')).hide();
            
            if (result.correct) {
                this.handleCorrectAnswer(result);
            } else {
                this.handleIncorrectAnswer(result);
            }
            
            if (result.game_ended && result.winner) {
                setTimeout(() => this.showGameOver(result.winner), 1000);
            }
            
        } catch (error) {
            console.error('Error submitting answer:', error);
            this.showError(error.message || 'Failed to submit answer');
        } finally {
            this.hideLoading();
        }
    }
    
    handleCorrectAnswer(result) {
        this.playSound('correct');
        
        // Mark clue as answered
        const clueElement = document.querySelector(`[data-clue-id="${this.gameState.currentClue.id}"]`);
        if (clueElement) {
            clueElement.classList.add('answered');
            clueElement.onclick = null;
            clueElement.style.cursor = 'not-allowed';
        }
        
        // Update streak
        this.gameState.streak = result.streak || 0;
        
        // Show success feedback
        this.showFeedback('Correct! Great job!', 'success');
        
        // Update turn indicator for AI turn
        this.updateTurnDisplay('ai');
    }
    
    handleIncorrectAnswer(result) {
        this.playSound('incorrect');
        this.gameState.streak = 0;
        
        // Show error feedback
        this.showFeedback('Incorrect answer. Try again!', 'error');
        
        // Shake the clue item
        const clueElement = document.querySelector(`[data-clue-id="${this.gameState.currentClue.id}"]`);
        if (clueElement) {
            clueElement.classList.add('incorrect-feedback');
            setTimeout(() => {
                clueElement.classList.remove('incorrect-feedback');
            }, 500);
        }
    }
    
    async getHint() {
        if (this.gameState.hintsRemaining <= 0) {
            this.showError('No hints remaining!');
            return;
        }
        
        try {
            const response = await fetch('/get_hint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    clue_id: this.gameState.currentClue.id
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            // Show hint
            document.getElementById('hint-text').textContent = result.hint;
            document.getElementById('hint-display').classList.remove('d-none');
            
            // Update hints remaining
            this.gameState.hintsRemaining = result.hints_remaining;
            document.getElementById('hints-remaining').textContent = this.gameState.hintsRemaining;
            
            this.playSound('hint');
            
        } catch (error) {
            console.error('Error getting hint:', error);
            this.showError(error.message || 'Failed to get hint');
        }
    }
    
    startGameStateUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateGameState();
        }, 1000);
    }
    
    async updateGameState() {
        if (!this.gameState.isActive) return;
        
        try {
            const response = await fetch('/get_state');
            const state = await response.json();
            
            if (state.error) {
                console.error('Game state error:', state.error);
                // If session is lost, stop polling and show setup screen
                if (state.error.includes('No active game session')) {
                    this.gameState.isActive = false;
                    clearInterval(this.updateInterval);
                    this.showError('Game session lost. Please start a new game.');
                    setTimeout(() => {
                        this.newGame();
                    }, 2000);
                }
                return;
            }
            
            // Update scores with animation
            this.updateScore('player', state.player_score);
            this.updateScore('ai', state.ai_score);
            
            // Update turn
            if (state.turn !== this.gameState.turn) {
                this.gameState.turn = state.turn;
                this.updateTurnDisplay(state.turn);
            }
            
            // Update grid
            if (state.grid_state) {
                this.updateGrid(state.grid_state);
            }
            
            // Update streak
            this.gameState.streak = state.streak || 0;
            document.getElementById('player-streak').textContent = this.gameState.streak;
            
            // Check for game end
            if (state.game_ended && state.winner) {
                this.showGameOver(state.winner);
            }
            
        } catch (error) {
            console.error('Error updating game state:', error);
        }
    }
    
    updateScore(player, newScore) {
        const scoreElement = document.getElementById(`${player}-score`);
        const currentScore = parseInt(scoreElement.textContent);
        
        if (newScore > currentScore) {
            scoreElement.textContent = newScore;
            scoreElement.classList.add('score-increase');
            setTimeout(() => {
                scoreElement.classList.remove('score-increase');
            }, 600);
        }
        
        this.gameState.scores[player] = newScore;
    }
    
    updateTurnDisplay(turn) {
        const turnDisplay = document.getElementById('turn-display');
        const turnText = document.getElementById('turn-text');
        const aiStatus = document.getElementById('ai-status');
        
        turnDisplay.className = `turn-indicator ${turn}-turn`;
        
        if (turn === 'player') {
            turnText.innerHTML = '<i class="fas fa-user me-2"></i>Your Turn';
            aiStatus.textContent = 'Waiting';
            aiStatus.classList.remove('ai-thinking');
        } else {
            turnText.innerHTML = '<i class="fas fa-robot me-2"></i>AI Turn';
            aiStatus.textContent = 'Thinking...';
            aiStatus.classList.add('ai-thinking');
        }
    }
    
    updateGrid(gridState) {
        Object.entries(gridState).forEach(([position, letter]) => {
            const cell = document.getElementById(`cell-${position}`);
            if (cell && letter) {
                cell.textContent = letter;
                cell.classList.remove('empty');
                cell.classList.add('filled');
            }
        });
    }
    
    showGameOver(winner) {
        this.gameState.isActive = false;
        clearInterval(this.updateInterval);
        
        const modal = document.getElementById('gameOverModal');
        const winnerDisplay = document.getElementById('winner-display');
        const finalScores = document.getElementById('final-scores');
        
        let winnerContent = '';
        let celebrationClass = '';
        
        switch (winner) {
            case 'player':
                winnerContent = '<i class="fas fa-trophy text-warning me-2"></i>Congratulations! You Won!';
                celebrationClass = 'winner-player';
                this.playSound('win');
                break;
            case 'ai':
                winnerContent = '<i class="fas fa-robot text-danger me-2"></i>AI Wins! Better luck next time!';
                celebrationClass = 'winner-ai';
                this.playSound('lose');
                break;
            case 'tie':
                winnerContent = '<i class="fas fa-handshake text-warning me-2"></i>It\'s a Tie! Great game!';
                celebrationClass = 'winner-tie';
                this.playSound('tie');
                break;
        }
        
        winnerDisplay.innerHTML = `<div class="winner-celebration ${celebrationClass}">${winnerContent}</div>`;
        finalScores.innerHTML = `
            <div class="row">
                <div class="col-6">
                    <strong>Your Score:</strong><br>
                    <span class="text-info">${this.gameState.scores.player}</span>
                </div>
                <div class="col-6">
                    <strong>AI Score:</strong><br>
                    <span class="text-danger">${this.gameState.scores.ai}</span>
                </div>
            </div>
        `;
        
        new bootstrap.Modal(modal).show();
    }
    
    newGame() {
        bootstrap.Modal.getInstance(document.getElementById('gameOverModal')).hide();
        document.getElementById('game-setup').classList.remove('d-none');
        document.getElementById('game-board').classList.add('d-none');
        this.resetGame();
    }
    
    async resetGame() {
        try {
            await fetch('/reset_game', { method: 'POST' });
            
            this.gameState.isActive = false;
            clearInterval(this.updateInterval);
            
            // Reset UI
            document.getElementById('game-setup').classList.remove('d-none');
            document.getElementById('game-board').classList.add('d-none');
            
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    }
    
    pauseGame() {
        // Toggle game state updates
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            this.showFeedback('Game Paused', 'info');
        } else {
            this.startGameStateUpdates();
            this.showFeedback('Game Resumed', 'info');
        }
    }
    
    async showStats() {
        try {
            this.showLoading('Loading statistics...');
            
            const response = await fetch('/get_stats');
            const stats = await response.json();
            
            if (stats.error) {
                throw new Error(stats.error);
            }
            
            // Update main stats
            document.getElementById('total-games').textContent = stats.total_games;
            document.getElementById('player-wins').textContent = stats.player_wins;
            document.getElementById('ai-wins').textContent = stats.ai_wins;
            document.getElementById('win-rate').textContent = `${stats.win_rate}%`;
            document.getElementById('avg-player-score').textContent = stats.avg_player_score;
            document.getElementById('avg-ai-score').textContent = stats.avg_ai_score;
            
            // Update difficulty breakdown
            const difficultyContainer = document.getElementById('difficulty-breakdown');
            difficultyContainer.innerHTML = '';
            
            Object.entries(stats.difficulty_stats).forEach(([difficulty, count]) => {
                const badgeClass = `badge-${difficulty}`;
                difficultyContainer.innerHTML += `
                    <div class="difficulty-stat">
                        <span>
                            <span class="badge ${badgeClass}">${difficulty}</span>
                        </span>
                        <strong>${count}</strong>
                    </div>
                `;
            });
            
            // Update recent games table
            const tableBody = document.getElementById('recent-games-table');
            tableBody.innerHTML = '';
            
            if (stats.recent_games && stats.recent_games.length > 0) {
                stats.recent_games.forEach(game => {
                    const resultClass = game.winner === 'player' ? 'result-win' : 
                                       game.winner === 'ai' ? 'result-loss' : 'result-tie';
                    const resultText = game.winner === 'player' ? 'WIN' : 
                                      game.winner === 'ai' ? 'LOSS' : 'TIE';
                    
                    const duration = game.duration ? `${Math.floor(game.duration / 60)}:${String(game.duration % 60).padStart(2, '0')}` : 'N/A';
                    
                    tableBody.innerHTML += `
                        <tr>
                            <td>${game.created_at}</td>
                            <td><span class="badge badge-${game.difficulty}">${game.difficulty}</span></td>
                            <td>${game.mode}</td>
                            <td>${game.player_score}</td>
                            <td>${game.ai_score}</td>
                            <td><span class="${resultClass}">${resultText}</span></td>
                            <td>${duration}</td>
                        </tr>
                    `;
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No games played yet</td></tr>';
            }
            
            // Show the modal
            new bootstrap.Modal(document.getElementById('statsModal')).show();
            
        } catch (error) {
            console.error('Error loading statistics:', error);
            this.showError('Failed to load statistics');
        } finally {
            this.hideLoading();
        }
    }
    
    showLoading(message = 'Loading...') {
        // Show loading indicator (implement as needed)
        console.log('Loading:', message);
    }
    
    hideLoading() {
        // Hide loading indicator
        console.log('Loading complete');
    }
    
    showError(message) {
        this.showFeedback(message, 'error');
    }
    
    showFeedback(message, type = 'info') {
        // Create toast notification
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = 9999;
        
        const toastClass = {
            'success': 'text-bg-success',
            'error': 'text-bg-danger',
            'warning': 'text-bg-warning',
            'info': 'text-bg-info'
        }[type] || 'text-bg-info';
        
        toastContainer.innerHTML = `
            <div class="toast ${toastClass}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        document.body.appendChild(toastContainer);
        
        const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
        toast.show();
        
        // Remove toast container after it's hidden
        setTimeout(() => {
            document.body.removeChild(toastContainer);
        }, 5000);
    }
    
    playSound(type) {
        if (!this.soundEnabled) return;
        
        // Simple audio feedback using Web Audio API
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        const frequencies = {
            'correct': 800,
            'incorrect': 300,
            'select': 600,
            'start': 1000,
            'win': 1200,
            'lose': 200,
            'tie': 700,
            'hint': 900
        };
        
        oscillator.frequency.value = frequencies[type] || 600;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }
}

// Global game instance
const game = new CrosswordGame();

// Global functions for HTML onclick handlers
function selectDifficulty(difficulty) {
    game.selectDifficulty(difficulty);
}

function selectMode(mode) {
    game.selectMode(mode);
}

function startGame() {
    game.startGame();
}

function submitAnswer() {
    game.submitAnswer();
}

function getHint() {
    game.getHint();
}

function resetGame() {
    game.resetGame();
}

function pauseGame() {
    game.pauseGame();
}

function newGame() {
    game.newGame();
}

function showStats() {
    game.showStats();
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Crossword Battle Arena loaded successfully!');
});
