"""
Test script to validate non-blocking NPC task updates.

This script creates multiple NPCs and simulates them requesting tasks
simultaneously to verify that the game doesn't freeze during LLM queries.
"""

import pygame
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_npc.core.npc import NPC
from ai_npc.core.player import Player
from ai_npc.config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, FPS

class World:
    """Simple world class for testing."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []  # No objects in this simple test
        self.npcs = []     # Will be populated in the test
    
    def get_objects_near(self, x, y, distance):
        """Get objects near a position."""
        return []  # No objects in this simple test
    
    def get_npcs_near(self, x, y, distance):
        """Get NPCs near a position."""
        return [npc for npc in self.npcs 
                if ((npc.x - x)**2 + (npc.y - y)**2)**0.5 < distance]

def main():
    """Main test function."""
    pygame.init()
    pygame.font.init()
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NPC Non-blocking Test")
    clock = pygame.time.Clock()
    
    # Create world
    world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create player
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # Create multiple NPCs
    num_npcs = 10  # Create 10 NPCs for testing
    npc_types = ["villager", "guard", "merchant"]
    
    for i in range(num_npcs):
        # Position NPCs evenly in a circle around the center
        import math
        angle = 2 * math.pi * i / num_npcs
        radius = 150
        x = SCREEN_WIDTH // 2 + radius * math.cos(angle)
        y = SCREEN_HEIGHT // 2 + radius * math.sin(angle)
        
        # Alternate NPC types
        npc_type = npc_types[i % len(npc_types)]
        
        # Create NPC
        npc = NPC(f"NPC-{i+1}", x, y, npc_type)
        world.npcs.append(npc)
    
    # Performance tracking
    frame_times = []
    last_time = time.time()
    
    # Main game loop
    running = True
    while running:
        # Calculate frame time for FPS display
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        frame_times.append(dt)
        if len(frame_times) > 60:
            frame_times.pop(0)
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update player based on keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            player.move(1, 0)
        if keys[pygame.K_UP]:
            player.move(0, -1)
        if keys[pygame.K_DOWN]:
            player.move(0, 1)
        
        # Update NPCs
        for npc in world.npcs:
            npc.update(player, world)
        
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw player
        player.draw(screen)
        
        # Draw NPCs
        for npc in world.npcs:
            npc.draw(screen)
        
        # Draw performance info
        font = pygame.font.SysFont('Arial', 16)
        if frame_times:
            avg_frame_time = sum(frame_times) / len(frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))
        
        # Draw waiting/pending requests count
        waiting_count = sum(1 for npc in world.npcs if npc.waiting_for_task)
        waiting_text = font.render(f"Waiting for tasks: {waiting_count}/{len(world.npcs)}", True, (255, 255, 255))
        screen.blit(waiting_text, (10, 30))
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Cleanup
    pygame.quit()
    
    # Print performance statistics
    if frame_times:
        avg_frame_time = sum(frame_times) / len(frame_times)
        min_fps = 1.0 / max(frame_times) if max(frame_times) > 0 else 0
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        print(f"Average FPS: {avg_fps:.1f}")
        print(f"Minimum FPS: {min_fps:.1f}")
        print(f"Average frame time: {avg_frame_time * 1000:.1f} ms")

if __name__ == "__main__":
    main() 