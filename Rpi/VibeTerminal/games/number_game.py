"""
Number Guessing Game for VibeTerminal
Guess a number between 1-100 in the fewest attempts possible.
"""

import random
from games.base_game import BaseGame


class Game(BaseGame):
    """
    Number Guessing Game
    
    The player must guess a random number between 1-100.
    Score is based on the number of attempts (lower is better).
    """
    
    def __init__(self):
        super().__init__(
            name="number",
            description="Guess a number between 1-100. Lower attempts = higher score!",
            use_llm=False  # This game doesn't need LLM
        )
        self.secret = 0
        self.attempts = 0
        self.max_score = 100
    
    def play(self):
        """Main game loop"""
        self.display_instructions()
        
        self.secret = random.randint(1, 100)
        self.attempts = 0
        
        self.ui.assistant("I'm thinking of a number between 1 and 100.")
        self.ui.assistant("Try to guess it! Type 'quit' to give up.")
        
        while True:
            self.ui.bubble("You")
            guess_input = input().strip()
            
            if guess_input.lower() == "quit":
                self.ui.assistant("Game abandoned.")
                return 0
            
            try:
                guess = int(guess_input)
            except ValueError:
                self.ui.error("Please enter a valid number.")
                continue
            
            if guess < 1 or guess > 100:
                self.ui.error("Number must be between 1 and 100.")
                continue
            
            self.attempts += 1
            
            if guess == self.secret:
                score = self._calculate_score()
                self.end_game(
                    f"🎉 Correct! You guessed it in {self.attempts} attempts.\n"
                    f"Score: {score} points!"
                )
                return score
            elif guess < self.secret:
                self.ui.info("Too low. Try a higher number.")
            else:
                self.ui.info("Too high. Try a lower number.")
    
    def _calculate_score(self):
        """Calculate score based on attempts"""
        # Perfect score: 1-5 attempts = 100 points
        # Good score: 6-10 attempts = 70 points
        # Average score: 11-20 attempts = 40 points
        # Poor score: 21+ attempts = 10 points
        
        if self.attempts <= 5:
            return 100
        elif self.attempts <= 10:
            return 70
        elif self.attempts <= 20:
            return 40
        else:
            return 10
    
    def display_instructions(self):
        """Display game instructions"""
        self.ui.assistant(
            "Welcome to the Number Guessing Game!\n\n"
            "I will think of a random number between 1 and 100.\n"
            "You need to guess what it is.\n"
            "After each guess, I'll tell you if the number is higher or lower.\n\n"
            "Scoring: Guess in fewer attempts for more points!\n"
            "• 1-5 attempts: 100 points\n"
            "• 6-10 attempts: 70 points\n"
            "• 11-20 attempts: 40 points\n"
            "• 21+ attempts: 10 points"
        )


def create_game():
    """Factory function for game registry"""
    return Game()
