"""
Configuration settings for VibeTerminal
Centralized configuration management
"""

CONFIG = {
    # Application metadata
    "app_name": "VibeTerminal",
    "version": "Chat UI Edition - Modular",
    
    # UI/Terminal settings
    "typing_delay": 0.01,  # Seconds between characters in stream effect
    "use_typing_effect": True,  # Enable/disable typing animation
    
    # Logging
    "log_dir": "Logs",
    "log_level": "DEBUG",
    
    # LLM Configuration
    "llm_enabled": True,
    "llm_provider": "anthropic",  # Options: anthropic, mock
    # "llm_model": "claude-opus-4-5",
    # "llm_model": "llama3.2:1b",
    # "llm_model": "llama3.2",
    "llm_model": "llama2-uncensored:7b",
    "ollama_url": "http://localhost:11434/api/chat",
    # "llm_max_tokens": 1000,
    # "llm_temperature": 0.7,
    
    # Game settings
    "game_dir": "Games",
    "use_llm_for_games": True,  # Use LLM for dynamic game responses
    "use_test_data": True,  # Fallback to test data if LLM unavailable
    
    # API Keys (use environment variables in production)
    "anthropic_api_key": None,  # Set via environment variable
}

# Load API keys from environment
# import os

# if os.getenv("ANTHROPIC_API_KEY"):
#     CONFIG["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY")
