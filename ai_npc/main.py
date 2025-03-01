#!/usr/bin/env python3
"""
LLM-Controlled NPCs - Main Game Module
A story-driven sandbox adventure game with NPCs controlled by a Large Language Model.
"""

import sys
import pygame
from ai_npc.core.game_world import GameWorld
from ai_npc.core.player import Player
from ai_npc.config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BACKGROUND_COLOR

class Game:
    """Main game class that manages the game loop and high-level game state."""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game components
        self.world = GameWorld()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def handle_events(self):
        """Process all game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
            # Pass events to the player for handling
            self.player.handle_event(event)
    
    def update(self):
        """Update game state."""
        # Update player
        self.player.update()
        
        # Update world and NPCs
        self.world.update(self.player)
    
    def render(self):
        """Render the game screen."""
        # Clear the screen
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw the world
        self.world.draw(self.screen)
        
        # Draw the player
        self.player.draw(self.screen)
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run() 