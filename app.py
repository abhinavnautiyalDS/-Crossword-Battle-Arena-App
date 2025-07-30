import os
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import threading
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///crossword_battle.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import modules after app creation
from crossword_data import CrosswordPuzzleManager
from ai_player import AIPlayer

# Global game managers
puzzle_manager = CrosswordPuzzleManager()
ai_player = AIPlayer()

# Game state storage (in production, use Redis or database)
game_sessions = {}

class GameSession:
    def __init__(self, session_id, difficulty="medium", mode="quick_play"):
        self.session_id = session_id
        self.difficulty = difficulty
        self.mode = mode
        self.player_score = 0
        self.ai_score = 0
        self.turn = "player"
        self.current_puzzle = None
        self.answered_clues = []
        self.game_started = False
        self.game_ended = False
        self.winner = None
        self.start_time = None
        self.grid_state = {}
        self.hints_used = 0
        self.streak = 0
        
    def start_game(self):
        self.current_puzzle = puzzle_manager.get_puzzle(self.difficulty)
        self.game_started = True
        self.start_time = datetime.now()
        self.grid_state = {f"{i}-{j}": "" for i in range(self.current_puzzle["size"]) for j in range(self.current_puzzle["size"])}
        
    def submit_answer(self, clue_id, answer):
        if self.turn != "player" or self.game_ended:
            return {"error": "Not your turn or game ended"}
            
        if not self.current_puzzle or "clues" not in self.current_puzzle:
            return {"error": "No active puzzle"}
            
        clue = next((c for c in self.current_puzzle["clues"] if c["id"] == clue_id), None)
        if not clue or clue_id in self.answered_clues:
            return {"error": "Invalid clue or already answered"}
            
        if clue["answer"].upper() == answer.upper():
            self.player_score += clue.get("points", 10)
            self.answered_clues.append(clue_id)
            self.streak += 1
            self._update_grid(clue, answer.upper())
            self.turn = "ai"
            
            # Check win condition
            if self._check_win():
                self._save_game_stats()
                return {"correct": True, "winner": self.winner, "game_ended": True}
                
            # Start AI turn
            threading.Thread(target=self._ai_turn).start()
            return {"correct": True, "streak": self.streak}
        else:
            self.streak = 0
            return {"correct": False, "streak": self.streak}
    
    def _update_grid(self, clue, answer):
        """Update the crossword grid with the answered word"""
        if "position" in clue and "direction" in clue:
            start_row, start_col = clue["position"]
            direction = clue["direction"]
            
            for i, letter in enumerate(answer):
                if direction == "across":
                    self.grid_state[f"{start_row}-{start_col + i}"] = letter
                else:  # down
                    self.grid_state[f"{start_row + i}-{start_col}"] = letter
    
    def _ai_turn(self):
        """AI makes its move"""
        if self.turn != "ai" or self.game_ended:
            return
            
        if not self.current_puzzle or "clues" not in self.current_puzzle:
            return
            
        # AI thinking time based on difficulty
        thinking_time = {"easy": 3, "medium": 2, "hard": 1}.get(self.difficulty, 2)
        time.sleep(thinking_time)
        
        available_clues = [c for c in self.current_puzzle["clues"] if c["id"] not in self.answered_clues]
        if available_clues:
            selected_clue = ai_player.select_clue(available_clues, self.difficulty)
            self.ai_score += selected_clue.get("points", 10)
            self.answered_clues.append(selected_clue["id"])
            self._update_grid(selected_clue, selected_clue["answer"])
        
        self.turn = "player"
        self._check_win()
    
    def _check_win(self):
        """Check if game is won"""
        if not self.current_puzzle or "clues" not in self.current_puzzle:
            return False
            
        total_clues = len(self.current_puzzle["clues"])
        answered = len(self.answered_clues)
        
        if answered >= total_clues:
            if self.player_score > self.ai_score:
                self.winner = "player"
            elif self.ai_score > self.player_score:
                self.winner = "ai"
            else:
                self.winner = "tie"
            self.game_ended = True
            return True
        
        # Score-based win (optional)
        if self.mode == "quick_play" and (self.player_score >= 100 or self.ai_score >= 100):
            self.winner = "player" if self.player_score > self.ai_score else "ai"
            self.game_ended = True
            return True
            
        return False
    
    def get_hint(self, clue_id):
        """Get a hint for a specific clue"""
        if self.hints_used >= 3:  # Limit hints
            return {"error": "No more hints available"}
            
        if not self.current_puzzle or "clues" not in self.current_puzzle:
            return {"error": "No active puzzle"}
            
        clue = next((c for c in self.current_puzzle["clues"] if c["id"] == clue_id), None)
        if clue and clue_id not in self.answered_clues:
            self.hints_used += 1
            hint = clue["answer"][:2] + "..." if len(clue["answer"]) > 2 else clue["answer"][0] + "..."
            return {"hint": hint, "hints_remaining": 3 - self.hints_used}
        return {"error": "Cannot provide hint for this clue"}
    
    def _save_game_stats(self):
        """Save game statistics to database"""
        from models import GameStats, PlayerStats
        from datetime import datetime
        
        try:
            # Calculate game duration
            duration = int((datetime.now() - self.start_time).total_seconds()) if self.start_time else 0
            
            # Save game stats
            game_stat = GameStats(
                session_id=self.session_id,
                difficulty=self.difficulty,
                mode=self.mode,
                player_score=self.player_score,
                ai_score=self.ai_score,
                winner=self.winner,
                duration=duration,
                hints_used=self.hints_used
            )
            db.session.add(game_stat)
            
            # Update or create player stats
            player_stats = PlayerStats.query.filter_by(player_id=self.session_id[:8]).first()
            if not player_stats:
                player_stats = PlayerStats(player_id=self.session_id[:8])
                db.session.add(player_stats)
            
            player_stats.total_games += 1
            player_stats.total_score += self.player_score
            
            if self.winner == "player":
                player_stats.wins += 1
            elif self.winner == "ai":
                player_stats.losses += 1
            else:
                player_stats.ties += 1
            
            if self.streak > player_stats.best_streak:
                player_stats.best_streak = self.streak
                
            player_stats.updated_at = datetime.utcnow()
            
            db.session.commit()
            app.logger.info(f"Saved game stats for session {self.session_id}")
            
        except Exception as e:
            app.logger.error(f"Error saving game stats: {e}")
            db.session.rollback()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    difficulty = data.get('difficulty', 'medium')
    mode = data.get('mode', 'quick_play')
    
    # Generate a new session ID for each game
    session_id = os.urandom(16).hex()
    session['session_id'] = session_id
    
    # Clear any existing session for this browser
    existing_session_id = session.get('session_id')
    if existing_session_id and existing_session_id in game_sessions:
        del game_sessions[existing_session_id]
    
    game_session = GameSession(session_id, difficulty, mode)
    game_session.start_game()
    game_sessions[session_id] = game_session
    
    if not game_session.current_puzzle:
        return jsonify({"error": "Failed to initialize puzzle"})
        
    return jsonify({
        "status": "success",
        "session_id": session_id,
        "difficulty": difficulty,
        "mode": mode,
        "puzzle": {
            "size": game_session.current_puzzle["size"],
            "title": game_session.current_puzzle["title"],
            "clues": game_session.current_puzzle["clues"]
        }
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    session_id = session.get('session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({"error": "No active game session"})
    
    game_session = game_sessions[session_id]
    data = request.get_json()
    clue_id = data.get('clue_id')
    answer = data.get('answer', '').strip()
    
    result = game_session.submit_answer(clue_id, answer)
    return jsonify(result)

@app.route('/get_state')
def get_state():
    session_id = session.get('session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({"error": "No active game session"})
    
    game_session = game_sessions[session_id]
    return jsonify({
        "player_score": game_session.player_score,
        "ai_score": game_session.ai_score,
        "turn": game_session.turn,
        "game_ended": game_session.game_ended,
        "winner": game_session.winner,
        "answered_clues": game_session.answered_clues,
        "grid_state": game_session.grid_state,
        "hints_used": game_session.hints_used,
        "streak": game_session.streak
    })

@app.route('/get_hint', methods=['POST'])
def get_hint():
    session_id = session.get('session_id')
    if not session_id or session_id not in game_sessions:
        return jsonify({"error": "No active game session"})
    
    game_session = game_sessions[session_id]
    data = request.get_json()
    clue_id = data.get('clue_id')
    
    result = game_session.get_hint(clue_id)
    return jsonify(result)

@app.route('/reset_game', methods=['POST'])
def reset_game():
    session_id = session.get('session_id')
    if session_id and session_id in game_sessions:
        del game_sessions[session_id]
    return jsonify({"status": "reset"})

@app.route('/get_stats')
def get_stats():
    """Get player statistics"""
    from models import GameStats, PlayerStats
    
    try:
        # Get recent games
        recent_games = GameStats.query.order_by(GameStats.created_at.desc()).limit(10).all()
        
        # Get global player stats (aggregated)
        total_games = GameStats.query.count()
        player_wins = GameStats.query.filter_by(winner='player').count()
        ai_wins = GameStats.query.filter_by(winner='ai').count()
        ties = GameStats.query.filter_by(winner='tie').count()
        
        # Get average scores
        avg_player_score = db.session.query(db.func.avg(GameStats.player_score)).scalar() or 0
        avg_ai_score = db.session.query(db.func.avg(GameStats.ai_score)).scalar() or 0
        
        # Get difficulty distribution
        difficulty_stats = db.session.query(
            GameStats.difficulty, 
            db.func.count(GameStats.id)
        ).group_by(GameStats.difficulty).all()
        
        stats = {
            "total_games": total_games,
            "player_wins": player_wins,
            "ai_wins": ai_wins,
            "ties": ties,
            "win_rate": round((player_wins / total_games * 100), 1) if total_games > 0 else 0,
            "avg_player_score": round(avg_player_score, 1),
            "avg_ai_score": round(avg_ai_score, 1),
            "difficulty_stats": {diff: count for diff, count in difficulty_stats},
            "recent_games": [
                {
                    "id": game.id,
                    "difficulty": game.difficulty,
                    "mode": game.mode,
                    "player_score": game.player_score,
                    "ai_score": game.ai_score,
                    "winner": game.winner,
                    "duration": game.duration,
                    "created_at": game.created_at.strftime("%Y-%m-%d %H:%M")
                } for game in recent_games
            ]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        app.logger.error(f"Error getting stats: {e}")
        return jsonify({"error": "Failed to retrieve statistics"})

with app.app_context():
    # Import models after app context is available
    import models
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
