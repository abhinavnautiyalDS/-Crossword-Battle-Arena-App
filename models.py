from app import db
from datetime import datetime

class GameStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    player_score = db.Column(db.Integer, default=0)
    ai_score = db.Column(db.Integer, default=0)
    winner = db.Column(db.String(20))
    duration = db.Column(db.Integer)  # in seconds
    hints_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(32), nullable=False)  # session-based for now
    total_games = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
