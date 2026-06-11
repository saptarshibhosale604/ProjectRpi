"""
Score Manager for VibeTerminal
Handles score tracking and persistence
"""

import json
import os
from datetime import datetime


class ScoreManager:
    """Manages game scores and statistics"""
    
    def __init__(self, scores_file="scores.json"):
        self.scores_file = scores_file
        self.scores = self._load_scores()
    
    def _load_scores(self):
        """Load scores from file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_scores(self):
        """Save scores to file"""
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def add_score(self, game_name, points):
        """Add score for a game"""
        if game_name not in self.scores:
            self.scores[game_name] = {
                "total": 0,
                "wins": 0,
                "last_played": None,
                "history": []
            }
        
        self.scores[game_name]["total"] += points
        self.scores[game_name]["wins"] += 1
        self.scores[game_name]["last_played"] = datetime.now().isoformat()
        self.scores[game_name]["history"].append({
            "points": points,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_scores()
    
    def get_score(self, game_name):
        """Get total score for a game"""
        if game_name in self.scores:
            return self.scores[game_name]["total"]
        return 0
    
    def get_all_scores(self):
        """Get all scores"""
        result = {}
        for game_name, data in self.scores.items():
            result[game_name] = data["total"]
        return result
    
    def get_stats(self, game_name):
        """Get detailed stats for a game"""
        if game_name in self.scores:
            return self.scores[game_name]
        return None
    
    def reset_scores(self):
        """Reset all scores"""
        self.scores = {}
        self._save_scores()
    
    def reset_game_score(self, game_name):
        """Reset score for a specific game"""
        if game_name in self.scores:
            del self.scores[game_name]
            self._save_scores()
