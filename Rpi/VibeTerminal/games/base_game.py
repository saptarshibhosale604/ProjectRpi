"""
Base Game Class for VibeTerminal
All games should inherit from this class
"""

from abc import ABC, abstractmethod
from llm_handler import LLMHandler
from logger import Logger
from ui_manager import UIManager


class BaseGame(ABC):
    """Abstract base class for all VibeTerminal games"""
    
    def __init__(self, name, description="A VibeTerminal game", use_llm=True):
        """
        Initialize a game
        
        Args:
            name: Game name
            description: Game description
            use_llm: Whether to use LLM for this game
        """
        self.name = name
        self.description = description
        self.use_llm = use_llm
        self.ui = UIManager()
        # self.llm = LLMHandler() if use_llm else None
        self.logger = Logger()
        self.llm = LLMHandler(self.logger) if use_llm else None
        self.score = 0
    
    @abstractmethod
    def play(self):
        """
        Main game loop - must be implemented by subclass
        Should return the score earned
        
        Returns:
            int: Score earned in this game session
        """
        pass
    
    def get_llm_response(self, prompt, system_prompt=None, use_test=False):
        """
        Get response from LLM
        
        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            use_test: Force test data mode
        
        Returns:
            str: LLM response or test data
        """
        if not self.llm:
            return None
        return self.llm.get_response(prompt, system_prompt, use_test=use_test)
    
    def get_test_response(self):
        """
        Get test data response when LLM is unavailable
        Override this method in subclass to provide game-specific test data
        
        Returns:
            str: Test response
        """
        return "Using test data mode"
    
    def ask_llm_with_fallback(self, prompt, system_prompt=None):
        """
        Ask LLM with automatic fallback to test data
        
        Args:
            prompt: The prompt
            system_prompt: Optional system prompt
        
        Returns:
            str: Response from LLM or test data
        """
        if self.use_llm and self.llm:
            response = self.llm.get_response(prompt, system_prompt)
            if response:
                return response
        
        return self.get_test_response()
    
    def display_instructions(self):
        """Display game instructions (optional)"""
        self.ui.assistant(f"Starting {self.name}...")
    
    def end_game(self, message):
        """Display end game message"""
        self.ui.assistant(message)
    
    @property
    def game_info(self):
        """Return game information"""
        return {
            "name": self.name,
            "description": self.description,
            "uses_llm": self.use_llm
        }
