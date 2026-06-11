"""
Game Registry for VibeTerminal
Manages game registration and loading
"""

import os
import importlib.util
from pathlib import Path


class GameRegistry:
    """Registry for all available games"""

    print("GameRegistry")
    
    def __init__(self):
        self.games = {}
        # self.game_dir = "Games"
        self.game_dir = "games"
        self._load_games()
    
    def _load_games(self):
        """Dynamically load all games from the Games directory"""
        games_path = Path(self.game_dir)
        
        print("inside this _load_games()")
        if not games_path.exists():
            print("inside this game path not()")
            return
        
        # Look for game files matching the pattern *_game.py
        for game_file in games_path.glob("*_game.py"):
            if game_file.name.startswith("_"):
                continue
            
            try:
                self._load_game_from_file(game_file)
            except Exception as e:
                print(f"Error loading game from {game_file}: {str(e)}")
    
    def _load_game_from_file(self, file_path):
        """Load a single game from a file"""
        spec = importlib.util.spec_from_file_location(
            file_path.stem,
            file_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for a 'create_game' function or 'Game' class
        if hasattr(module, 'create_game'):
            game = module.create_game()
            self.register_game(game.name, game)
        elif hasattr(module, 'Game'):
            game = module.Game()
            self.register_game(game.name, game)
    
    def register_game(self, name, game_instance):
        """
        Register a game
        
        Args:
            name: Game name (identifier)
            game_instance: Instance of BaseGame subclass
        """
        self.games[name.lower()] = game_instance
    
    def get_game(self, name):
        """
        Get a game by name
        
        Args:
            name: Game name
        
        Returns:
            Game instance or None
        """
        return self.games.get(name.lower())
    
    def get_game_list(self):
        """Get list of all game names"""
        return sorted(self.games.keys())
    
    def get_all_games(self):
        """Get all registered games"""
        return self.games
    
    def unregister_game(self, name):
        """Unregister a game"""
        if name.lower() in self.games:
            del self.games[name.lower()]
    
    def reload_games(self):
        """Reload all games"""
        self.games = {}
        self._load_games()
