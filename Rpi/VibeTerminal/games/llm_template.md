# VibeTerminal Game Creation Template

This guide shows you how to create new games for VibeTerminal using LLM assistance, with fallback to manual test data.

## Quick Start

1. **Describe your game** in plain English
2. **Use the template below** with LLM to generate the game code
3. **Place the generated file** in the Games directory as `{game_name}_game.py`
4. **Play it** with `play {game_name}`

---

## Prompting Template for LLM

Use this template when asking LLM to create a new game:

```
Create a VibeTerminal game called "{GAME_NAME}" with the following description:

Game Description:
{YOUR_GAME_DESCRIPTION}

Requirements:
- Inherit from BaseGame (imported from games.base_game)
- Implement the play() method that returns a score (int)
- Use self.ui for user interface (UIManager methods: assistant, bubble, stream, success, error, info)
- Use self.ask_llm_with_fallback() for LLM-powered interactions
- Override get_test_response() to provide hardcoded test data when LLM is unavailable
- Name the game class 'Game' and create a 'create_game()' function

Game Logic:
{YOUR_GAME_LOGIC}

Test Data:
{EXAMPLE_TEST_RESPONSES}
```

---

## Example Game Template (Copy & Modify)

Here's a complete working example you can adapt:

```python
"""
{GAME_NAME} for VibeTerminal
{GAME_DESCRIPTION}
"""

from games.base_game import BaseGame
from config import CONFIG


class Game(BaseGame):
    """
    {GAME_NAME}
    
    Game mechanics: {BRIEF_MECHANICS}
    """
    
    def __init__(self):
        super().__init__(
            name="{game_name}",
            description="{Game description}",
            use_llm=True  # Set to False to disable LLM for this game
        )
        # Add game-specific initialization here
        self.test_data = {
            "questions": [
                {"q": "Question 1?", "a": "answer1"},
                {"q": "Question 2?", "a": "answer2"},
            ]
        }
    
    def play(self):
        """Main game loop"""
        self.display_instructions()
        
        self.ui.assistant("Game starting...")
        
        # Game loop example:
        score = 0
        while True:
            self.ui.bubble("You")
            user_input = input().strip()
            
            if user_input.lower() == "quit":
                break
            
            # Use LLM with fallback:
            response = self.ask_llm_with_fallback(
                prompt=f"User input: {user_input}",
                system_prompt="You are a helpful game assistant."
            )
            
            self.ui.assistant(response)
            score += 1  # Award points as game progresses
        
        self.end_game(f"Game complete! Score: {score}")
        return score
    
    def get_test_response(self):
        """
        Fallback test data when LLM is unavailable
        This ensures the game works without API access
        """
        import random
        question = random.choice(self.test_data["questions"])
        return f"Test mode - {question['q']}"


def create_game():
    """Factory function for game registry"""
    return Game()
```

---

## Advanced: LLM-Powered Game Example

Here's a more sophisticated example with dynamic LLM interaction:

```python
"""
{GAME_NAME} for VibeTerminal
{GAME_DESCRIPTION}
"""

from games.base_game import BaseGame
import random


class Game(BaseGame):
    """
    {GAME_NAME}
    """
    
    def __init__(self):
        super().__init__(
            name="{game_name}",
            description="{Description}",
            use_llm=True
        )
        self.difficulty = "medium"
        self.max_turns = 5
        self.current_turn = 0
        
        # Test data for fallback mode
        self.test_scenarios = [
            {
                "context": "You are in a dark forest",
                "choices": ["Go left", "Go right", "Stay put"],
                "outcomes": ["You find a cave", "You see light", "A wolf appears"]
            },
            {
                "context": "You are at a crossroads",
                "choices": ["North", "South", "East", "West"],
                "outcomes": ["Mountains", "River", "Village", "Desert"]
            }
        ]
    
    def play(self):
        """Main game loop with LLM"""
        self.ui.assistant(
            f"Welcome to {self.name}! "
            f"You have {self.max_turns} turns to complete your quest."
        )
        
        score = 0
        
        for turn in range(self.max_turns):
            self.current_turn = turn + 1
            
            # Get scenario (LLM or test data)
            scenario = self._get_scenario(self.current_turn)
            self.ui.assistant(f"[Turn {self.current_turn}/{self.max_turns}] {scenario}")
            
            # Get user choice
            self.ui.bubble("You")
            choice = input("Enter your choice: ").strip()
            
            # Get outcome
            outcome = self._get_outcome(choice, self.current_turn)
            self.ui.assistant(outcome)
            
            score += 10  # Points per turn
        
        self.end_game(f"Quest complete! Final score: {score}")
        return score
    
    def _get_scenario(self, turn):
        """Get game scenario - LLM or test data"""
        prompt = f"Generate a short game scenario for turn {turn} in an adventure game. Keep it to 1-2 sentences."
        
        return self.ask_llm_with_fallback(
            prompt=prompt,
            system_prompt="You are a creative game master."
        )
    
    def _get_outcome(self, choice, turn):
        """Get outcome for player choice"""
        prompt = f"The player chose: '{choice}' on turn {turn}. Generate a short outcome (1-2 sentences)."
        
        return self.ask_llm_with_fallback(
            prompt=prompt,
            system_prompt="You are a game master describing outcomes."
        )
    
    def get_test_response(self):
        """Test data fallback"""
        scenario = random.choice(self.test_scenarios)
        return f"{scenario['context']} - Choose: {', '.join(scenario['choices'])}"


def create_game():
    """Factory function"""
    return Game()
```

---

## File Naming Convention

Save your game as: `{game_name}_game.py`

Examples:
- `number_game.py`
- `riddle_game.py`
- `adventure_game.py`
- `quiz_game.py`

The registry will automatically load it.

---

## Available UIManager Methods

```python
self.ui.bubble(title)              # Display labeled header
self.ui.stream(text)               # Typewriter effect
self.ui.assistant(msg)             # Assistant bubble + stream
self.ui.success(msg)               # ✓ message
self.ui.error(msg)                 # ✗ message
self.ui.info(msg)                  # ℹ message
self.ui.separator()                # Visual separator
self.ui.clear()                    # Clear screen
```

---

## LLM Methods

```python
# Get response with automatic fallback
response = self.ask_llm_with_fallback(
    prompt="Your question here",
    system_prompt="Optional system instructions"
)

# Force test data mode
response = self.get_llm_response(
    prompt="Your question",
    use_test=True
)

# Stream response (not fully tested in all games)
for chunk in self.llm.stream_response(prompt):
    print(chunk, end="", flush=True)
```

---

## Best Practices

### 1. Always Implement Test Data
```python
def get_test_response(self):
    """Fallback when LLM unavailable"""
    return "This is test data"
```

### 2. Keep Prompts Clear
```python
# Good
response = self.ask_llm_with_fallback(
    prompt=f"Generate one riddle about animals."
)

# Bad
response = self.ask_llm_with_fallback(
    prompt=f"do something"
)
```

### 3. Always Return Score
```python
def play(self):
    # ... game logic ...
    return score  # Must return int
```

### 4. Use Scoring System
- Award points for correct answers
- Award points for progress
- Award bonuses for speed/difficulty
- Examples: 10 points per turn, 50 points for completion

---

## Testing Your Game

### Test without LLM (test data mode)
```python
game = Game()
game.use_llm = False
score = game.play()
```

### Test with LLM
```python
game = Game()
game.use_llm = True
score = game.play()
```

### From main.py
```bash
python main.py
# Then type: play {game_name}
```

---

## Example: Creating a Quiz Game

Use this prompt with LLM:

```
Create a VibeTerminal game called "Quiz" with the following:

Game Description:
A trivia quiz game that asks the player 5 questions and scores based on correct answers.

Game Logic:
1. Display instructions
2. For each of 5 rounds:
   - Ask a trivia question (use LLM to generate)
   - Get player answer
   - Check if correct (use LLM to validate)
   - Award 10 points if correct
3. Display final score

Test Data:
When LLM unavailable, show these pre-made questions:
- "What is the capital of France?" → "Paris"
- "What is 2+2?" → "4"
- "What is the largest planet?" → "Jupiter"
- "What year did Python release?" → "1991"
- "What does API stand for?" → "Application Programming Interface"

Include a scoring system where correct answers = 10 points each.
```

Then save the generated code as `quiz_game.py` in the Games directory.

---

## Troubleshooting

**Game not loading?**
- Check filename matches `*_game.py` pattern
- Check class is named `Game`
- Check `create_game()` function exists
- Check imports are correct

**LLM not working?**
- Check `ANTHROPIC_API_KEY` is set
- Check `CONFIG["llm_enabled"]` is True
- Game will fall back to test data automatically

**Can't find game?**
- Type `games` in main menu to list loaded games
- Check file is in Games directory
- Try `python main.py` then reload or restart

---

## Contributing New Games

1. Create your game using this template
2. Test it thoroughly with both LLM and test data modes
3. Include clear instructions in the game
4. Add comprehensive test data for fallback
5. Submit with documentation

Happy game creating! 🎮
