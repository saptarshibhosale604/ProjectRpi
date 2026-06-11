"""
Riddle Game for VibeTerminal
Solve riddles for points! Uses LLM to generate riddles with test data fallback.
"""

import random
from games.base_game import BaseGame
from logger import Logger

class Game(BaseGame):
    """
    Riddle Game
    
    The player must solve riddles. Can use LLM to generate unique riddles
    or use predefined test data when LLM is unavailable.
    """
    
    def __init__(self):
        super().__init__(
            name="riddle",
            description="Solve riddles! Test your problem-solving skills.",
            use_llm=True
        )

        self.logger = Logger()
        
        # Predefined riddles for test/fallback mode
        self.test_riddles = [
            {
                "question": "I have keys but no locks. What am I?",
                "answer": "keyboard",
                "hints": ["It's electronic", "Musicians use it"]
            },
            {
                "question": "The more you take, the more you leave behind. What am I?",
                "answer": "footsteps",
                "hints": ["You make them when you walk", "They can be in sand or snow"]
            },
            {
                "question": "I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?",
                "answer": "echo",
                "hints": ["Sound-related", "Mountains have them"]
            },
            {
                "question": "The more it dries, the wetter it gets. What is it?",
                "answer": "towel",
                "hints": ["You use it in the bathroom", "It absorbs water"]
            },
            {
                "question": "What has hands but cannot clap?",
                "answer": "clock",
                "hints": ["Tells time", "Hangs on walls"]
            },
        ]
        
        self.current_riddle = None
        self.attempts = 0
        self.max_attempts = 3
        self.score = 0
    
    def play(self):
        """Main game loop"""
        self.logger.info("Riddle game started New one")
        self.display_instructions()
        
        num_riddles = 3
        self.score = 0
        
        for riddle_num in range(num_riddles):
            self.ui.assistant(f"\nRiddle {riddle_num + 1}/{num_riddles}")
            self.ui.separator()
            
            if not self._solve_riddle():
                self.ui.info("Game over! You couldn't solve the riddle.")
                break
        
        self.end_game(f"Game complete! Total score: {self.score} points")
        return self.score
    
    def _solve_riddle(self):
        """
        Get and process a single riddle
        Returns True if solved, False if gave up or failed
        """
        # Get riddle (LLM or test data)
        riddle = self._get_riddle()
        
        if not riddle:
            self.ui.error("Could not generate riddle.")
            return False
        
        self.current_riddle = riddle
        self.attempts = 0
        
        self.ui.assistant(riddle["question"])
        
        while self.attempts < self.max_attempts:
            self.ui.bubble("You")
            answer = input().strip().lower()
            
            if answer == "quit":
                return False
            
            if answer == "hint":
                self._give_hint()
                continue
            
            self.attempts += 1
            
            if self._check_answer(answer, riddle["answer"]):
                points = self._calculate_points()
                self.score += points
                self.ui.success(
                    f"Correct! You solved it in {self.attempts} attempts.\n"
                    f"+{points} points! (Total: {self.score})"
                )
                return True
            else:
                remaining = self.max_attempts - self.attempts
                if remaining > 0:
                    self.ui.error(f"Not quite. Try again. ({remaining} attempts left)")
                else:
                    self.ui.error(f"Out of attempts! The answer was: {riddle['answer']}")
                    return False
        
        return False
    
    def _get_riddle(self):
        """Get a riddle from LLM or test data"""
        if self.use_llm and self.llm:
            return self._get_llm_riddle()
        else:
            return self._get_test_riddle()
    
    def _get_llm_riddle(self):
        """Generate riddle using LLM"""
        prompt = (
            "Generate a clever riddle with the following format:\n"
            "RIDDLE: [The riddle question]\n"
            "ANSWER: [The one-word answer]\n"
            "HINT1: [Hint 1]\n"
            "HINT2: [Hint 2]\n\n"
            "Make it moderately difficult but solvable."
        )
        
        response = ""

        for chunk in self.llm.get_stream_response(
            prompt=prompt,
            system_prompt="You are a riddle master. Create clever, appropriate riddles."
        ):
            response += chunk

        if response:
            return self._parse_riddle_response(response)
        # response = self.llm.get_response(
        # # response = self.llm.get_stream_response(
        #     prompt=prompt,
        #     system_prompt="You are a riddle master. Create clever, appropriate riddles."
        # )
        
        if response:
            return self._parse_riddle_response(response)
        
        # Fallback to test data
        return self._get_test_riddle()
    
    def _parse_riddle_response(self, response):
        """Parse LLM response into riddle format"""
        lines = response.strip().split('\n')
        riddle = {"question": "", "answer": "", "hints": []}
        
        for line in lines:
            if line.startswith("RIDDLE:"):
                riddle["question"] = line.replace("RIDDLE:", "").strip()
            elif line.startswith("ANSWER:"):
                riddle["answer"] = line.replace("ANSWER:", "").strip().lower()
            elif line.startswith("HINT"):
                hint = line.split(":", 1)[1].strip() if ":" in line else ""
                if hint:
                    riddle["hints"].append(hint)
        
        # Validate parsed riddle
        if riddle["question"] and riddle["answer"]:
            return riddle
        
        return None
    
    def _get_test_riddle(self):
        """Get a riddle from predefined test data"""
        return random.choice(self.test_riddles)
    
    def _check_answer(self, user_answer, correct_answer):
        """Check if answer is correct (with partial matching)"""
        user_words = set(user_answer.lower().split())
        correct_words = set(correct_answer.lower().split())
        
        # Exact match or contains the answer word
        return (user_answer.lower() == correct_answer.lower() or
                correct_answer.lower() in user_answer.lower())
    
    def _give_hint(self):
        """Display a hint"""
        if not self.current_riddle or "hints" not in self.current_riddle:
            self.ui.info("No hints available.")
            return
        
        hints = self.current_riddle["hints"]
        hint_index = min(self.attempts - 1, len(hints) - 1)
        
        if hint_index >= 0 and hint_index < len(hints):
            self.ui.info(f"Hint: {hints[hint_index]}")
        else:
            self.ui.info("No more hints available.")
    
    def _calculate_points(self):
        """Calculate points based on attempts"""
        # First attempt: 50 points
        # Second attempt: 30 points
        # Third attempt: 10 points
        points_per_attempt = [50, 30, 10]
        
        if self.attempts <= len(points_per_attempt):
            return points_per_attempt[self.attempts - 1]
        return 0
    
    def display_instructions(self):
        """Display game instructions"""
        self.ui.assistant(
            "Welcome to the Riddle Game!\n\n"
            # "You'll be given riddles to solve.\n"
            # "You have 3 attempts per riddle.\n"
            # "Type 'hint' to get a hint (counts as an attempt).\n"
            # "Type 'quit' to give up.\n\n"
            # "Scoring:\n"
            # "• Solved on 1st attempt: 50 points\n"
            # "• Solved on 2nd attempt: 30 points\n"
            # "• Solved on 3rd attempt: 10 points"
        )
    
    def get_test_response(self):
        """Test response (for compatibility)"""
        return random.choice(self.test_riddles)["question"]


def create_game():
    """Factory function for game registry"""
    return Game()
