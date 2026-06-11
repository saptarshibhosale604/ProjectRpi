"""
UI Manager for VibeTerminal
Handles all terminal output, formatting, and visual effects
"""

import time
from config import CONFIG


class UIManager:
    """Manages terminal UI elements and output formatting"""
    
    def __init__(self):
        self.typing_delay = CONFIG["typing_delay"]
        self.use_typing_effect = CONFIG["use_typing_effect"]
    
    def bubble(self, title):
        """Display a labeled bubble/header"""
        print()
        print("╭──────────────╮")
        print(f"│ {title:<12} │")
        print("╰──────────────╯")
        print()
    
    def stream(self, text):
        """Stream text with typing effect"""
        if not self.use_typing_effect:
            print(text)
            return
        
        for ch in text:
            print(ch, end="", flush=True)
            time.sleep(self.typing_delay)
        print()
    
    def assistant(self, msg):
        """Display assistant message with bubble"""
        self.bubble("Assistant")
        self.stream(msg)
    
    def success(self, msg):
        """Display success message"""
        print("✓ " + msg)
    
    def error(self, msg):
        """Display error message"""
        print("✗ " + msg)
    
    def info(self, msg):
        """Display info message"""
        print("ℹ " + msg)
    
    def separator(self):
        """Display a visual separator"""
        print("-" * 50)
    
    def clear(self):
        """Clear terminal screen (cross-platform)"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
