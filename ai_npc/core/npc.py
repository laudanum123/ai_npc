"""
NPC module for AI-controlled characters in the game.
This module provides the base NPC class and behavior handling.
"""

import time
import random
import math
import pygame
from ai_npc.config.settings import NPC_COLORS, NPC_SIZE, NPC_SPEED, NPC_UPDATE_INTERVAL
from ai_npc.core.llm_controller import LLMController


class NPC:
    """Base class for all NPCs in the game."""
    
    def __init__(self, npc_id, x, y, npc_type="villager"):
        """Initialize an NPC with a position and type."""
        self.npc_id = npc_id
        self.x = x
        self.y = y
        self.width = NPC_SIZE
        self.height = NPC_SIZE
        self.speed = NPC_SPEED
        self.npc_type = npc_type
        self.color = NPC_COLORS.get(npc_type, (255, 255, 255))  # Default to white if type not found
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Behavior state
        self.current_task = "idle"
        self.last_completed_task = None
        self.current_state = "idle"
        self.target_x = None
        self.target_y = None
        
        # LLM update timing
        self.last_llm_update = time.time() * 1000  # Current time in milliseconds
        self.llm_controller = LLMController()
        self.waiting_for_task = False  # Flag to track if we're waiting for an LLM response
        
        # Font for displaying name
        self.font = pygame.font.SysFont('Arial', 12)
    
    def update(self, player, world):
        """Update the NPC's state and position."""
        current_time = time.time() * 1000
        
        # Check if we have a cached response from the LLM
        cached_response = self.llm_controller.get_cached_response(self.npc_id)
        if cached_response and self.waiting_for_task:
            # Process the response
            if "new_task" in cached_response:
                self.current_task = cached_response["new_task"]
                print(f"NPC {self.npc_id} received new task: {self.current_task}")
            
            # Clear the cache and reset the waiting flag
            self.llm_controller.clear_cache(self.npc_id)
            self.waiting_for_task = False
            self.last_llm_update = current_time
        
        # Check if it's time to update the NPC's task via LLM
        elif not self.waiting_for_task and current_time - self.last_llm_update >= NPC_UPDATE_INTERVAL:
            self.queue_task_update(player, world)
        
        # Execute the current task
        self.execute_task(player, world)
    
    def queue_task_update(self, player, world):
        """Queue a task update request to the LLM controller."""
        environment_context = self.get_environment_context(world)
        player_interaction = self.get_player_interaction(player)
        
        # Prepare the query for the LLM
        query = {
            "npc_id": self.npc_id,
            "npc_type": self.npc_type,
            "current_task": self.current_task,
            "last_completed_task": self.last_completed_task,
            "current_state": self.current_state,
            "environment_context": environment_context,
            "player_interaction": player_interaction
        }
        
        # Queue the request
        self.llm_controller.queue_npc_task_request(self.npc_id, query, self.task_update_callback)
        self.waiting_for_task = True
    
    def task_update_callback(self, response):
        """Callback function for when a task update response is received."""
        # This is called by the LLM controller's processing thread
        # The response is automatically cached, and we'll process it in the update method
        pass
    
    def update_task_from_llm(self, player, world):
        """
        Synchronous version of task update (for backwards compatibility).
        This is a blocking call and should be avoided in favor of queue_task_update.
        """
        environment_context = self.get_environment_context(world)
        player_interaction = self.get_player_interaction(player)
        
        # Prepare the query for the LLM
        query = {
            "npc_id": self.npc_id,
            "npc_type": self.npc_type,
            "current_task": self.current_task,
            "last_completed_task": self.last_completed_task,
            "current_state": self.current_state,
            "environment_context": environment_context,
            "player_interaction": player_interaction
        }
        
        # Get the response from the LLM (blocking call)
        response = self.llm_controller.get_npc_task(query)
        
        # Update the NPC's task based on the LLM response
        if response and "new_task" in response:
            self.current_task = response["new_task"]
            print(f"NPC {self.npc_id} received new task: {self.current_task}")
    
    def execute_task(self, player, world):
        """Execute the current task."""
        task_lower = self.current_task.lower()
        
        # Handle task descriptions that might have a colon (function call format)
        if ":" in task_lower:
            base_task, description = task_lower.split(":", 1)
            task_lower = base_task.strip()
        
        # Check for function-style task names (with underscores)
        if "follow_player" in task_lower:
            self.follow_player(player)
            return
        elif "guard_position" in task_lower:
            self.guard_position()
            return
        elif "tend_crops" in task_lower:
            self.tend_crops(world)
            return
        elif "rest_at_home" in task_lower:
            self.rest_at_home(world)
            return
        elif "talk_to_others" in task_lower:
            self.talk_to_others(world)
            return
        elif "inspect_surroundings" in task_lower:
            self.inspect_surroundings(world)
            return
        elif "sell_wares" in task_lower:
            self.sell_wares(world)
            return
        elif "manage_inventory" in task_lower:
            self.manage_inventory(world)
            return
        elif "greet_nearby" in task_lower:
            self.greet_nearby(player, world)
            return
        
        # Check for common task patterns as before, for backward compatibility
        # and for handling more natural language descriptions
        
        # Movement patterns
        if "patrol" in task_lower:
            self.patrol(world)
        elif any(word in task_lower for word in ["follow", "approach", "chase"]) and "player" in task_lower:
            self.follow_player(player)
        elif any(word in task_lower for word in ["guard", "protect", "watch", "stand"]):
            self.guard_position()
        elif any(word in task_lower for word in ["wander", "explore", "roam", "walk"]):
            self.wander(world)
        
        # Villager specific actions
        elif self.npc_type == "villager" and any(word in task_lower for word in ["farm", "crops", "tend", "harvest"]):
            self.tend_crops(world)
        elif self.npc_type == "villager" and any(word in task_lower for word in ["rest", "sleep", "home"]):
            self.rest_at_home(world)
        elif self.npc_type == "villager" and any(word in task_lower for word in ["talk", "chat", "gossip"]):
            self.talk_to_others(world)
            
        # Guard specific actions
        elif self.npc_type == "guard" and any(word in task_lower for word in ["inspect", "investigate"]):
            self.inspect_surroundings(world)
            
        # Merchant specific actions
        elif self.npc_type == "merchant" and any(word in task_lower for word in ["sell", "trade", "market"]):
            self.sell_wares(world)
        elif self.npc_type == "merchant" and any(word in task_lower for word in ["restock", "inventory", "goods", "arrange"]):
            self.manage_inventory(world)
            
        # Interaction patterns
        elif any(word in task_lower for word in ["greet", "wave", "welcome"]):
            self.greet_nearby(player, world)
            
        # Default behavior if no patterns match
        elif "idle" in task_lower or "wait" in task_lower:
            self.idle()
        else:
            # If no specific implementation, default to wandering
            self.wander(world)
    
    def patrol(self, world):
        """Patrol behavior: move between predefined points."""
        # Simple implementation: if no target or reached target, pick a new one
        if self.target_x is None or self.target_y is None or self.has_reached_target():
            # Choose a new random target within the world bounds
            self.target_x = random.randint(0, world.width - self.width)
            self.target_y = random.randint(0, world.height - self.height)
        
        self.move_toward_target()
    
    def follow_player(self, player):
        """Follow the player at a distance."""
        player_pos = player.get_position()
        # Keep some distance from the player
        distance = 50
        angle = random.uniform(0, 2 * 3.14159)  # Random angle
        self.target_x = player_pos[0] + distance * math.cos(angle)
        self.target_y = player_pos[1] + distance * math.sin(angle)
        self.move_toward_target()
    
    def guard_position(self):
        """Stay in the current position and look around."""
        # For now, just stay in place or make small movements
        if random.random() < 0.02:  # Occasionally shift position slightly
            self.target_x = self.x + random.randint(-10, 10)
            self.target_y = self.y + random.randint(-10, 10)
            self.move_toward_target()
    
    def wander(self, world):
        """Wander randomly within the world."""
        # Change direction occasionally
        if random.random() < 0.02 or self.target_x is None or self.has_reached_target():
            self.target_x = random.randint(0, world.width - self.width)
            self.target_y = random.randint(0, world.height - self.height)
        
        self.move_toward_target()
    
    def idle(self):
        """Do nothing, just stand in place."""
        pass
    
    # New implementation methods for more specific tasks
    
    def tend_crops(self, world):
        """Villager behavior: tend to crops in the field."""
        # Find a "natural" area (for now, near trees)
        trees = [obj for obj in world.objects if obj.obj_type == "tree"]
        if trees and (self.target_x is None or self.has_reached_target()):
            # Pick a random tree to go near
            target_tree = random.choice(trees)
            # Get a position near but not on the tree
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            self.target_x = target_tree.x + offset_x
            self.target_y = target_tree.y + offset_y
        
        self.move_toward_target()
    
    def rest_at_home(self, world):
        """Villager behavior: go home and rest."""
        # Find a "house" to rest in
        houses = [obj for obj in world.objects if obj.obj_type == "house"]
        if houses and (self.target_x is None or self.has_reached_target()):
            # Pick a random house
            target_house = random.choice(houses)
            # Go inside the house
            self.target_x = target_house.x + target_house.width // 2
            self.target_y = target_house.y + target_house.height // 2
        
        self.move_toward_target()
    
    def talk_to_others(self, world):
        """Villager behavior: talk to other NPCs."""
        # Find another NPC to talk to
        other_npcs = [npc for npc in world.npcs if npc != self]
        if other_npcs and (self.target_x is None or self.has_reached_target()):
            # Pick a random NPC
            target_npc = random.choice(other_npcs)
            # Move closer to them
            self.target_x = target_npc.x
            self.target_y = target_npc.y
        
        self.move_toward_target()
    
    def inspect_surroundings(self, world):
        """Guard behavior: inspect the surroundings."""
        # Move to various points of interest
        points_of_interest = world.objects + world.npcs
        if points_of_interest and (self.target_x is None or self.has_reached_target()):
            # Pick a random object or NPC to inspect
            target = random.choice(points_of_interest)
            # Get a position near but not on the target
            self.target_x = target.x + random.randint(-30, 30)
            self.target_y = target.y + random.randint(-30, 30)
        
        self.move_toward_target()
    
    def sell_wares(self, world):
        """Merchant behavior: sell items at a market or busy area."""
        # Find a good spot to sell (near houses or other NPCs)
        sell_spots = [obj for obj in world.objects if obj.obj_type == "house"] + world.npcs
        if sell_spots and (self.target_x is None or self.has_reached_target()):
            # Pick a random spot
            target_spot = random.choice(sell_spots)
            # Get a position near the spot
            self.target_x = target_spot.x + random.randint(-50, 50)
            self.target_y = target_spot.y + random.randint(-50, 50)
        
        self.move_toward_target()
    
    def manage_inventory(self, world):
        """Merchant behavior: manage inventory or arrange goods."""
        # Stay in one place and "manage inventory"
        if self.target_x is None:
            # Find a suitable spot
            self.target_x = random.randint(100, world.width - 100)
            self.target_y = random.randint(100, world.height - 100)
            
        # Once at the spot, just stay there (simulating inventory management)
        if not self.has_reached_target():
            self.move_toward_target()
    
    def greet_nearby(self, player, world):
        """Social behavior: greet nearby entities."""
        # Check if player is nearby
        player_pos = player.get_position()
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 100:
            # If player is nearby, turn towards them
            self.target_x = player_pos[0]
            self.target_y = player_pos[1]
            # But don't move too close
            if distance > 60:
                self.move_toward_target()
        else:
            # Otherwise, look for other NPCs to greet
            self.talk_to_others(world)
    
    def move_toward_target(self):
        """Move the NPC toward its target position."""
        if self.target_x is None or self.target_y is None:
            return
        
        # Calculate direction vector
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        # Normalize the vector and multiply by speed
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            dx = (dx / distance) * self.speed
            dy = (dy / distance) * self.speed
        
        # Update position
        self.x += dx
        self.y += dy
        
        # Update rectangle for collision detection
        self.rect.x = self.x
        self.rect.y = self.y
    
    def has_reached_target(self):
        """Check if the NPC has reached its target position."""
        if self.target_x is None or self.target_y is None:
            return True
        
        # Calculate distance to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        # Return True if close enough to target
        return distance < self.speed
    
    def get_environment_context(self, world):
        """Get information about the NPC's surroundings."""
        # Get nearby objects
        nearby_objects = world.get_objects_near(self.x, self.y, 100)
        object_types = [obj.obj_type for obj in nearby_objects]
        
        # Get nearby NPCs
        nearby_npcs = world.get_npcs_near(self.x, self.y, 100)
        npc_types = [npc.npc_type for npc in nearby_npcs if npc != self]
        
        # Build environment description
        environment = f"position: ({int(self.x)}, {int(self.y)})"
        
        if object_types:
            environment += f", nearby objects: {', '.join(object_types)}"
        
        if npc_types:
            environment += f", nearby NPCs: {', '.join(npc_types)}"
            
        return environment
    
    def get_player_interaction(self, player):
        """Get information about the NPC's interaction with the player."""
        player_pos = player.get_position()
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 50:
            return "player very close"
        elif distance < 100:
            return "player nearby"
        elif distance < 200:
            return "player visible"
        else:
            return "none"
    
    def draw(self, surface):
        """Draw the NPC on the given surface."""
        # Draw the NPC as a colored rectangle
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw the NPC's name above it
        name_text = self.font.render(f"{self.npc_id}: {self.current_task}", True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.top - 10))
        surface.blit(name_text, name_rect)
        
        # Indicate if waiting for a task update
        if self.waiting_for_task:
            # Draw a small indicator (e.g., a dot) to show the NPC is waiting for a task update
            pygame.draw.circle(surface, (255, 255, 0), (self.rect.right + 5, self.rect.top), 3) 