"""
Test Games Module for VibeTerminal
Allows testing games with pre-configured data without LLM or interactive input
Useful for CI/CD pipelines and automated testing
"""

import io
import sys
from contextlib import redirect_stdout, redirect_stdin
from games.game_registry import GameRegistry
from ui_manager import UIManager


class GameTester:
    """Automated game tester with pre-configured inputs"""
    
    def __init__(self):
        self.registry = GameRegistry()
        self.ui = UIManager()
        self.test_results = {}
    
    def test_game(self, game_name, test_inputs, force_test_mode=True):
        """
        Test a game with predefined inputs
        
        Args:
            game_name: Name of the game to test
            test_inputs: List of inputs to feed to the game
            force_test_mode: Use test data instead of LLM
        
        Returns:
            dict: Test results including score and status
        """
        game = self.registry.get_game(game_name)
        
        if not game:
            return {"status": "ERROR", "message": f"Game '{game_name}' not found"}
        
        # Configure test mode
        if force_test_mode:
            game.use_llm = False
        
        # Simulate input
        input_stream = "\n".join(test_inputs) + "\n"
        
        try:
            # Capture output
            with redirect_stdout(io.StringIO()):
                with redirect_stdin(io.StringIO(input_stream)):
                    score = game.play()
            
            result = {
                "status": "SUCCESS",
                "game": game_name,
                "score": score,
                "inputs_used": len(test_inputs)
            }
        
        except Exception as e:
            result = {
                "status": "ERROR",
                "game": game_name,
                "error": str(e),
                "inputs_used": len(test_inputs)
            }
        
        self.test_results[game_name] = result
        return result
    
    def test_all_games(self):
        """Test all registered games with minimal inputs"""
        games = self.registry.get_game_list()
        
        for game_name in games:
            # Test with "quit" to exit immediately
            self.test_game(game_name, ["quit"], force_test_mode=True)
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("GAME TEST RESULTS")
        print("=" * 60 + "\n")
        
        for game_name, result in self.test_results.items():
            status = result["status"]
            symbol = "✓" if status == "SUCCESS" else "✗"
            
            print(f"{symbol} {game_name.upper()}")
            
            if status == "SUCCESS":
                print(f"  Score: {result['score']}")
                print(f"  Inputs: {result['inputs_used']}")
            else:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
            print()
        
        # Summary
        successful = sum(1 for r in self.test_results.values() if r["status"] == "SUCCESS")
        total = len(self.test_results)
        
        print("=" * 60)
        print(f"Summary: {successful}/{total} games passed")
        print("=" * 60 + "\n")


# Predefined test scenarios for each game type

RIDDLE_GAME_TESTS = {
    "inputs": [
        "keyboard",  # Answer first riddle
        "quit"       # Quit
    ],
    "expected_score": 50  # Should get first attempt bonus
}

NUMBER_GAME_TESTS = {
    "inputs": [
        "50",   # First guess
        "75",   # Second guess
        "80",   # Continue guessing
        "quit"  # Quit
    ],
    "description": "Tests number game with multiple guesses"
}

CUSTOM_GAME_TEST_TEMPLATE = {
    "inputs": [
        # Add your test inputs here
        "user_input_1",
        "user_input_2",
        "quit"
    ],
    "description": "Custom game test",
    "expected_behavior": "Game should handle inputs gracefully"
}


def run_quick_tests():
    """Run quick smoke tests on all games"""
    tester = GameTester()
    
    print("Running quick game tests...\n")
    
    # Test number game
    print("Testing: number")
    tester.test_game("number", ["50", "quit"])
    
    # Test riddle game
    print("Testing: riddle")
    tester.test_game("riddle", ["keyboard", "quit"])
    
    tester.print_results()


def run_comprehensive_tests():
    """Run comprehensive tests on all registered games"""
    tester = GameTester()
    
    print("Running comprehensive game tests...\n")
    tester.test_all_games()
    tester.print_results()


def create_custom_test(game_name, inputs, description=""):
    """
    Create a custom test for a game
    
    Args:
        game_name: Name of the game
        inputs: List of test inputs
        description: Test description
    
    Returns:
        dict: Test configuration
    """
    return {
        "game": game_name,
        "inputs": inputs,
        "description": description
    }


def run_custom_test(test_config):
    """Run a custom test configuration"""
    tester = GameTester()
    
    print(f"Running custom test: {test_config.get('description', test_config['game'])}\n")
    
    result = tester.test_game(
        test_config["game"],
        test_config["inputs"],
        force_test_mode=True
    )
    
    tester.print_results()
    return result


# Example: Create and run a custom test
def example_custom_test():
    """Example of how to create and run a custom test"""
    
    # Create test config
    test = create_custom_test(
        game_name="riddle",
        inputs=["keyboard", "footsteps", "quit"],
        description="Riddle game with two correct answers"
    )
    
    # Run the test
    result = run_custom_test(test)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test VibeTerminal games")
    parser.add_argument(
        "--mode",
        choices=["quick", "comprehensive", "example"],
        default="quick",
        help="Test mode to run"
    )
    parser.add_argument(
        "--game",
        help="Test specific game"
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        help="Custom inputs to test"
    )
    
    args = parser.parse_args()
    
    if args.mode == "quick":
        run_quick_tests()
    elif args.mode == "comprehensive":
        run_comprehensive_tests()
    elif args.mode == "example":
        example_custom_test()
    
    if args.game and args.inputs:
        tester = GameTester()
        tester.test_game(args.game, args.inputs)
        tester.print_results()
