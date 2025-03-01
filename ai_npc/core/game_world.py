"""
Game world module for managing the game environment and NPCs.
"""

import random
import pygame
from ai_npc.config.settings import WORLD_WIDTH, WORLD_HEIGHT, OBJECT_TYPES
from ai_npc.core.npc import NPC


class GameObject:
    """Base class for all objects in the game world."""
    
    def __init__(self, x, y, width, height, obj_type, color):
        """Initialize a game object with position, size, type, and color."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.obj_type = obj_type
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, surface):
        """Draw the object on the given surface."""
        pygame.draw.rect(surface, self.color, self.rect)


class GameWorld:
    """Class representing the game world and all its contents."""
    
    def __init__(self):
        """Initialize the game world with NPCs and objects."""
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.npcs = []
        self.objects = []
        
        # Create some initial NPCs
        self._create_npcs()
        
        # Create some environmental objects
        self._create_objects()
    
    def _create_npcs(self):
        """Create initial NPCs in the world."""
        # Create a few villagers
        for i in range(3):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            self.npcs.append(NPC(f"villager_{i}", x, y, "villager"))
        
        # Create a guard
        x = random.randint(100, self.width - 100)
        y = random.randint(100, self.height - 100)
        self.npcs.append(NPC("guard_0", x, y, "guard"))
        
        # Create a merchant
        x = random.randint(100, self.width - 100)
        y = random.randint(100, self.height - 100)
        self.npcs.append(NPC("merchant_0", x, y, "merchant"))
    
    def _create_objects(self):
        """Create environmental objects in the world."""
        # Create some trees
        for _ in range(20):
            x = random.randint(0, self.width - 32)
            y = random.randint(0, self.height - 32)
            self.objects.append(GameObject(x, y, 32, 32, "tree", OBJECT_TYPES["tree"]))
        
        # Create some rocks
        for _ in range(10):
            x = random.randint(0, self.width - 24)
            y = random.randint(0, self.height - 24)
            self.objects.append(GameObject(x, y, 24, 24, "rock", OBJECT_TYPES["rock"]))
        
        # Create some houses
        for _ in range(5):
            x = random.randint(0, self.width - 64)
            y = random.randint(0, self.height - 64)
            self.objects.append(GameObject(x, y, 64, 64, "house", OBJECT_TYPES["house"]))
    
    def update(self, player):
        """Update all NPCs and objects in the world."""
        # Update NPCs
        for npc in self.npcs:
            npc.update(player, self)
        
        # Check for collisions with the world boundary
        for npc in self.npcs:
            npc.x = max(0, min(npc.x, self.width - npc.width))
            npc.y = max(0, min(npc.y, self.height - npc.height))
            npc.rect.x = npc.x
            npc.rect.y = npc.y
        
        # Check player collision with world boundary
        player.x = max(0, min(player.x, self.width - player.width))
        player.y = max(0, min(player.y, self.height - player.height))
        player.rect.x = player.x
        player.rect.y = player.y
    
    def draw(self, surface):
        """Draw all objects and NPCs in the world."""
        # Draw environmental objects
        for obj in self.objects:
            obj.draw(surface)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(surface)
    
    def get_objects_near(self, x, y, radius):
        """Get all objects within a radius of the given position."""
        nearby = []
        for obj in self.objects:
            dx = obj.x - x
            dy = obj.y - y
            distance = (dx**2 + dy**2)**0.5
            if distance <= radius:
                nearby.append(obj)
        return nearby
    
    def get_npcs_near(self, x, y, radius):
        """Get all NPCs within a radius of the given position."""
        nearby = []
        for npc in self.npcs:
            dx = npc.x - x
            dy = npc.y - y
            distance = (dx**2 + dy**2)**0.5
            if distance <= radius:
                nearby.append(npc)
        return nearby 