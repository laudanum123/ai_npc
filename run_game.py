#!/usr/bin/env python3
"""
Run script for the LLM-Controlled NPCs game.
This script launches the game and handles command-line arguments.
"""

import sys
import argparse
from ai_npc.main import Game


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="LLM-Controlled NPCs Game")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


def main():
    """Main entry point for the game."""
    args = parse_args()
    
    if args.debug:
        print("Debug mode enabled")
    
    # Start the game
    print("Starting LLM-Controlled NPCs Game...")
    game = Game()
    game.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
        sys.exit(0) 