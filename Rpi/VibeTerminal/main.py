#!/usr/bin/env python3
"""
VibeTerminal - Main Entry Point
Orchestrates the chat UI experience with modular game system
"""

from config import CONFIG
from logger import Logger
from ui_manager import UIManager
from score_manager import ScoreManager
# from Games.game_registry import GameRegistry
from games.game_registry import GameRegistry

logger = Logger()
ui_manager = UIManager()
score_manager = ScoreManager()
game_registry = GameRegistry()

# games         - List all available games
# play <game>   - Play a specific game
# score         - Show current scores
# quit          - Exit VibeTerminal

def help_menu():
    """Display available commands and games"""
    help_text = """Commands

help          - Show this menu

Available Games:
"""
    # Add registered games
    for game_name in game_registry.get_game_list():
        help_text += f"  • {game_name}\n"
    
    help_text += "\nOr ask about:\n"
    help_text += "  • python\n  • tcp\n  • linux"
    
    ui_manager.assistant(help_text)


def play_game(game_name):
    """Play a game from the registry"""
    game = game_registry.get_game(game_name)
    if game is None:
        ui_manager.assistant(f"Game '{game_name}' not found. Type 'games' to see available games.")
        return
    
    try:
        result = game.play()
        if result:
            score_manager.add_score(game_name, result)
            logger.log(f"Game completed: {game_name}, Score: {result}")
    except Exception as e:
        logger.log(f"Error playing game {game_name}: {str(e)}")
        ui_manager.assistant(f"An error occurred: {str(e)}")


def show_games():
    """Display all available games with descriptions"""
    games = game_registry.get_all_games()
    ui_manager.bubble("Available Games")
    
    if not games:
        print("No games available yet.")
        return
    
    for game_name, game in games.items():
        print(f"• {game_name}: {game.description}")


def show_score():
    """Display current scores"""
    scores = score_manager.get_all_scores()
    ui_manager.bubble("Your Scores")
    
    if not scores:
        print("No scores yet. Play some games!")
        return
    
    total = 0
    for game_name, score in scores.items():
        print(f"  {game_name}: {score}")
        total += score
    print(f"\n  Total: {total}")


def handle_knowledge_query(text):
    """Handle general knowledge queries"""
    knowledge_base = {
        "python": "Python is a high-level programming language known for readability and versatility.",
        "tcp": "TCP (Transmission Control Protocol) provides reliable, ordered, and error-checked delivery using a three-way handshake: SYN, SYN-ACK, ACK.",
        "linux": "Linux is an open-source operating system kernel used in servers, desktops, and Raspberry Pi devices.",
        "hello": "Hello! I'm VibeTerminal. Type 'help' to see available commands.",
    }
    
    text_lower = text.lower()
    for key, response in knowledge_base.items():
        if key in text_lower:
            ui_manager.assistant(response)
            return True
    
    return False


def main():
    """Main application loop"""
    print("=" * 50)
    print(f"{CONFIG['app_name']} - {CONFIG['version']}")
    print("=" * 50)
    ui_manager.assistant("Welcome! Type 'help' to begin.")
    
    while True:
        ui_manager.bubble("You")
        user_input = input().strip()
        
        if not user_input:
            continue
        
        logger.log(user_input)
        command = user_input.lower()
        
        # Command routing
        if command == "quit":
            ui_manager.assistant("Goodbye!")
            break
        elif command == "help":
            help_menu()
        elif command == "games":
            show_games()
        elif command == "score":
            show_score()
        elif command.startswith("play "):
            game_name = command[5:].strip()
            play_game(game_name)
        else:
            # Try knowledge query
            if not handle_knowledge_query(user_input):
                ui_manager.assistant(
                    "I'm a demo Chat UI terminal. Try: help, games, play <game>, "
                    "score, or ask about python, tcp, or linux."
                )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        logger.log(f"Fatal error: {str(e)}")
        print(f"Fatal error: {str(e)}")
