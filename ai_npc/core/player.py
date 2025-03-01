"""
Player module for the game.
Handles player movement, rendering, and interactions.
"""

import pygame
from ai_npc.config.settings import PLAYER_COLOR, PLAYER_SPEED, PLAYER_SIZE


class Player:
    """Player character class."""
    
    def __init__(self, x, y):
        """Initialize the player at the given position."""
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Movement flags
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
    
    def handle_event(self, event):
        """Handle player input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = True
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = True
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = True
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = True
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = False
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = False
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = False
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = False
    
    def update(self):
        """Update player position based on input."""
        # Update position based on movement flags
        if self.moving_up:
            self.y -= self.speed
        if self.moving_down:
            self.y += self.speed
        if self.moving_left:
            self.x -= self.speed
        if self.moving_right:
            self.x += self.speed
        
        # Update the rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, surface):
        """Draw the player on the given surface."""
        pygame.draw.rect(surface, self.color, self.rect)
    
    def get_position(self):
        """Return the player's current position."""
        return (self.x, self.y)
    
    def get_rect(self):
        """Return the player's rectangle for collision detection."""
        return self.rect 