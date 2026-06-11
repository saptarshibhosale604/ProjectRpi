# VibeTerminal - Modular Chat UI Edition

A modular, extensible terminal-based chat interface with a game system powered by Claude AI, featuring LLM integration with graceful fallback to test data.

## 🚀 Quick Start

### Prerequisites
```bash
python3.8+
pip install anthropic  # Optional, for LLM features
```

### Setup
```bash
# Set your API key (optional, only for LLM features)
export ANTHROPIC_API_KEY="your-key-here"

# Run the application
python main.py
```

### Play a Game
```
> play number      # Number guessing game
> play riddle      # Riddle solving game
> games            # List all games
> score            # View your scores
```

---

## 📁 Project Structure

```
VibeTerminal/
│
├── main.py                      # Application entry point
├── config.py                    # Configuration settings
├── ui_manager.py                # Terminal UI handling
├── logger.py                    # Logging functionality
├── score_manager.py             # Score tracking & persistence
├── llm_handler.py               # LLM integration (Claude API)
├── test_games.py                # Automated testing suite
│
├── Games/                       # Game modules directory
│   ├── __init__.py
│   ├── base_game.py             # Abstract base class for all games
│   ├── game_registry.py         # Game management & loading
│   ├── llmTemplate.md           # 📋 Template for creating new games
│   ├── number_game.py           # Number guessing game
│   └── riddle_game.py           # Riddle solving game (with LLM support)
│
├── Logs/                        # Generated log files
└── scores.json                  # Game scores storage

```

---

## 🔧 Core Components

### 1. **main.py** - Application Orchestrator
- Main event loop
- Command routing (help, play, games, score, quit)
- Game lifecycle management
- Knowledge base queries

**Key Commands:**
```python
help              # Show help menu
games             # List available games
play <game>       # Play a specific game
score             # Show scores
quit              # Exit app
```

### 2. **config.py** - Centralized Configuration
Settings for:
- Application metadata
- UI behavior (typing speed)
- Logging
- LLM settings
- Game directory
- API keys (from environment)

**Usage:**
```python
from config import CONFIG
print(CONFIG["app_name"])
print(CONFIG["llm_enabled"])
```

### 3. **ui_manager.py** - Terminal UI
Handles all terminal output and visual effects.

**Methods:**
```python
ui = UIManager()
ui.bubble("Title")              # Display header
ui.stream("Text")               # Typewriter effect
ui.assistant("Message")         # Assistant bubble
ui.success("Message")           # ✓ Success message
ui.error("Message")             # ✗ Error message
ui.info("Message")              # ℹ Info message
ui.separator()                  # Visual divider
ui.clear()                      # Clear screen
```

### 4. **llm_handler.py** - LLM Integration
Manages Claude API communication with automatic fallback.

**Features:**
- ✅ Claude API integration
- ✅ Automatic fallback to test data
- ✅ Configurable models and parameters
- ✅ Streaming responses
- ✅ Error handling

**Usage:**
```python
from llm_handler import LLMHandler

llm = LLMHandler()
response = llm.get_response(
    prompt="Your question",
    system_prompt="You are helpful"
)
```

### 5. **score_manager.py** - Score Tracking
Persists scores to JSON file.

**Features:**
- ✅ Score persistence
- ✅ Game statistics
- ✅ Play history
- ✅ Score aggregation

### 6. **logger.py** - Logging
Logs to file and console.

**Usage:**
```python
from logger import Logger
logger = Logger()
logger.info("User event")
logger.error("An error occurred")
```

### 7. **Games/base_game.py** - Base Game Class
Abstract class for all games.

```python
from games.base_game import BaseGame

class MyGame(BaseGame):
    def __init__(self):
        super().__init__(
            name="mygame",
            description="My game description",
            use_llm=True  # Enable LLM for this game
        )
    
    def play(self):
        """Main game loop - must return score"""
        self.ui.assistant("Welcome!")
        score = 0
        # Game logic here
        return score  # Must return int score
```

### 8. **Games/game_registry.py** - Game Management
Auto-discovers and loads games.

```python
from games.game_registry import GameRegistry

registry = GameRegistry()
game = registry.get_game("number")  # Get by name
games = registry.get_all_games()    # Get all games
```

### 9. **test_games.py** - Automated Testing
Test games without LLM or interactive input.

```bash
# Quick smoke tests
python test_games.py --mode quick

# Comprehensive tests
python test_games.py --mode comprehensive

# Test specific game
python test_games.py --game riddle --inputs keyboard quit
```

---

## 📚 Creating New Games

### Quick Method: Use the LLM Template

1. **Read the template:**
   ```
   Games/llmTemplate.md
   ```

2. **Ask Claude (using the template):**
   - Describe your game
   - Provide game logic
   - List test data

3. **Save as `{game_name}_game.py`**
   ```
   Games/my_new_game.py
   ```

4. **Play immediately:**
   ```
   > play my_new_game
   ```

### Example: Create a Quiz Game

**Minimal Template:**
```python
from games.base_game import BaseGame

class Game(BaseGame):
    def __init__(self):
        super().__init__(
            name="quiz",
            description="Answer trivia questions",
            use_llm=True
        )
        self.questions = [
            {"q": "Capital of France?", "a": "paris"},
            {"q": "2+2?", "a": "4"},
        ]
    
    def play(self):
        score = 0
        for q in self.questions:
            self.ui.bubble("You")
            answer = input().strip().lower()
            
            if answer == q["a"]:
                self.ui.success("Correct!")
                score += 10
            else:
                self.ui.error(f"Wrong! Answer: {q['a']}")
        
        return score
    
    def get_test_response(self):
        return self.questions[0]["q"]

def create_game():
    return Game()
```

**Save as:** `Games/quiz_game.py`

**Play with:**
```
> play quiz
```

---

## 🤖 LLM Features

### Enabled/Disabled
```python
# In config.py
"llm_enabled": True,              # Enable/disable LLM globally
"use_llm_for_games": True,        # Enable LLM for games
"use_test_data": True,            # Fallback mode
```

### In Games
```python
# Always falls back gracefully
response = self.ask_llm_with_fallback(
    prompt="Your question",
    system_prompt="System instructions"
)

# Force test data
response = self.get_llm_response(prompt, use_test=True)

# Stream responses
for chunk in self.llm.stream_response(prompt):
    print(chunk, end="")
```

### No API Key? No Problem!
- Games automatically fall back to test data
- Set test data in `get_test_response()` method
- Application still works 100%

---

## 📊 Testing

### Quick Test
```bash
python test_games.py --mode quick
```

### Comprehensive Test
```bash
python test_games.py --mode comprehensive
```

### Test Specific Game
```bash
python test_games.py --game number --inputs 50 quit
```

### Test with Custom Inputs
```python
from test_games import GameTester

tester = GameTester()
result = tester.test_game("riddle", ["keyboard", "quit"])
print(result)
```

---

## 📝 Configuration Reference

### Typing & UI
```python
CONFIG = {
    "typing_delay": 0.05,          # Seconds between chars
    "use_typing_effect": True,      # Enable animation
}
```

### LLM Settings
```python
CONFIG = {
    "llm_enabled": True,            # Enable/disable LLM
    "llm_provider": "anthropic",    # Provider (anthropic, mock)
    "llm_model": "claude-opus-4-5", # Model to use
    "llm_max_tokens": 1000,         # Max response length
    "llm_temperature": 0.7,         # Creativity level
}
```

### Game Settings
```python
CONFIG = {
    "game_dir": "Games",            # Where games are stored
    "use_llm_for_games": True,      # Enable LLM in games
    "use_test_data": True,          # Fallback to test data
}
```

---

## 🎮 Game Examples

### Number Game
- Guess a number 1-100
- Score based on attempts
- Test data: Built-in algorithm

### Riddle Game
- Solve riddles
- 3 attempts per riddle
- LLM generates unique riddles OR uses built-in test data
- Hints available

---

## 🔐 API Keys

### Setting API Key
```bash
# Option 1: Environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: In config.py (not recommended for production)
CONFIG["anthropic_api_key"] = "sk-ant-..."
```

### What if no API key?
- LLM is disabled
- Games automatically use test data
- Everything still works!

---

## 📋 Checklist for New Games

- [ ] Inherit from `BaseGame`
- [ ] Implement `play()` method (returns int score)
- [ ] Implement `get_test_response()` method
- [ ] Name class `Game`
- [ ] Add `create_game()` function
- [ ] Save as `{name}_game.py` in Games directory
- [ ] Test with `python test_games.py --game {name}`
- [ ] Add to version control

---

## 🐛 Troubleshooting

### Game not loading?
```bash
# Check game list
python main.py
> games

# Check for syntax errors
python -m py_compile Games/my_game.py
```

### LLM not working?
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Check config
python -c "from config import CONFIG; print(CONFIG['llm_enabled'])"

# Game falls back to test data automatically
```

### Scores not saving?
```bash
# Check file permissions
ls -la scores.json

# Reset scores (optional)
python -c "from score_manager import ScoreManager; ScoreManager().reset_scores()"
```

---

## 📚 File Templates

### New Game Template
See: `Games/llmTemplate.md`

### Game Test Template
```python
# In test_games.py, create custom tests:
test = create_custom_test(
    game_name="riddle",
    inputs=["keyboard", "quit"],
    description="Test riddle with answer"
)
result = run_custom_test(test)
```

---

## 🚀 Advanced Usage

### Custom LLM Provider
```python
from llm_handler import LLMHandler

class MyLLMHandler(LLMHandler):
    def _init_anthropic(self):
        # Custom initialization
        pass
```

### Custom UI Theme
```python
from ui_manager import UIManager

class MyUI(UIManager):
    def bubble(self, title):
        # Custom bubble design
        print(f">>> {title} <<<")
```

### Game Plugins
Add your own game loader:
```python
from games.game_registry import GameRegistry

registry = GameRegistry()
registry.register_game("custom", my_game_instance)
```

---

## 📊 Score Persistence

Scores saved to `scores.json`:
```json
{
  "number": {
    "total": 150,
    "wins": 2,
    "last_played": "2024-01-01T12:00:00",
    "history": [
      {"points": 100, "timestamp": "2024-01-01T12:00:00"},
      {"points": 50, "timestamp": "2024-01-01T13:00:00"}
    ]
  }
}
```

---

## 🤝 Contributing

### Adding a Game
1. Create game file: `Games/my_game.py`
2. Inherit from `BaseGame`
3. Implement required methods
4. Test with `test_games.py`
5. Add documentation

### Improving Core
1. Modular design - one concern per module
2. Maintain backward compatibility
3. Add tests in `test_games.py`
4. Update documentation

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🎯 Roadmap

- [ ] Web UI version
- [ ] Multiplayer support
- [ ] Game difficulty levels
- [ ] Achievement system
- [ ] Game categories/themes
- [ ] Custom game themes
- [ ] Community game sharing

---

## 💡 Tips

1. **Use LLM Template** for creating games with Claude
2. **Always implement test data** for offline play
3. **Test without LLM** to ensure game works
4. **Score persistence** is automatic
5. **Logs** are saved to `Logs/` directory
6. **Command-line testing** available in `test_games.py`

---

## 🆘 Support

- Check `Games/llmTemplate.md` for game creation help
- Review existing games for examples
- Run tests to debug: `python test_games.py --mode comprehensive`
- Check logs: `cat Logs/vibeterminal-*.log`

---

**Happy gaming! 🎮**
