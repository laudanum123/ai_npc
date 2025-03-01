"""
LLM Controller module for interfacing with the language model API.
Handles sending queries and processing responses for NPC behavior.
"""

import os
import json
import time
import random
import re
from dotenv import load_dotenv
from ai_npc.config.settings import LLM_API_TIMEOUT, LLM_MAX_TOKENS

# Load environment variables (for API keys)
load_dotenv()


class LLMController:
    """Controller class for interacting with the language model API."""
    
    def __init__(self):
        """Initialize the LLM controller."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_mock = True if not self.api_key else False
        
        if self.use_mock:
            print("Warning: No OpenAI API key found. Using mock LLM responses.")
        else:
            # Import OpenAI library only if API key is available
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("Error: OpenAI library not installed. Using mock LLM responses.")
                self.use_mock = True
                
        # Define the available NPC action tools/functions
        self.npc_action_tools = [
            {
                "type": "function",
                "function": {
                    "name": "assign_task_to_npc",
                    "description": "Assign a task to an NPC based on their type, state, and environment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "npc_id": {
                                "type": "string",
                                "description": "The ID of the NPC"
                            },
                            "task": {
                                "type": "string",
                                "description": "The task to assign to the NPC",
                                "enum": [
                                    # Common tasks for all NPCs
                                    "patrol", 
                                    "follow_player", 
                                    "guard_position", 
                                    "wander", 
                                    "idle",
                                    "greet_nearby",
                                    
                                    # Villager-specific tasks
                                    "tend_crops",
                                    "rest_at_home",
                                    "talk_to_others",
                                    
                                    # Guard-specific tasks
                                    "inspect_surroundings",
                                    
                                    # Merchant-specific tasks
                                    "sell_wares",
                                    "manage_inventory"
                                ]
                            },
                            "task_description": {
                                "type": "string",
                                "description": "A short description of how the NPC should perform the task"
                            }
                        },
                        "required": ["npc_id", "task"]
                    }
                }
            }
        ]
    
    def get_npc_task(self, query):
        """
        Get a new task for an NPC based on the query.
        
        Args:
            query (dict): The query containing NPC state and context
            
        Returns:
            dict: The response containing the new task for the NPC
        """
        if self.use_mock:
            return self._get_mock_response(query)
        
        try:
            return self._get_openai_response(query)
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._get_mock_response(query)
    
    def _get_openai_response(self, query):
        """Send a query to the OpenAI API and get a response."""
        # Create a system prompt that explains the task
        system_prompt = """
        You are an AI controlling NPCs in a video game. Your job is to give NPCs appropriate tasks
        based on their current state and environment.
        
        Each NPC type has specific tasks they can perform:
        
        ALL NPCs can:
        - patrol: Move between different points in the area
        - follow_player: Follow the player character at a distance
        - guard_position: Stay in one place, possibly making small movements to look around
        - wander: Move randomly around the world
        - idle: Stay still and do nothing
        - greet_nearby: Greet nearby entities, especially the player
        
        VILLAGERS can also:
        - tend_crops: Find fields (represented by trees) and work there
        - rest_at_home: Find a house to rest in
        - talk_to_others: Find other NPCs to talk to
        
        GUARDS can also:
        - inspect_surroundings: Move to and check different objects and NPCs in the area
        
        MERCHANTS can also:
        - sell_wares: Find a good spot to sell items, often near houses or other NPCs
        - manage_inventory: Stay in one place and manage their inventory
        
        Use the function to assign an appropriate task based on the NPC's type, current state, and environment.
        """
        
        # Convert query to a user message
        user_message = f"""
        NPC state:
        - ID: {query['npc_id']}
        - Type: {query['npc_type']}
        - Current task: {query['current_task']}
        - Last completed task: {query['last_completed_task']}
        - Current state: {query['current_state']}
        - Environment: {query['environment_context']}
        - Player interaction: {query['player_interaction']}
        
        Based on this information, assign a new task to the NPC using the function provided.
        Choose a task that makes sense for this type of NPC in their current situation.
        """
        
        # Call the OpenAI API with function calling
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=self.npc_action_tools,
            tool_choice={"type": "function", "function": {"name": "assign_task_to_npc"}},
            max_tokens=LLM_MAX_TOKENS,
            temperature=0.7,
            timeout=LLM_API_TIMEOUT
        )
        
        # Extract and parse the response
        try:
            # Get the function call from the response
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "assign_task_to_npc":
                # Parse the arguments as JSON
                args = json.loads(tool_call.function.arguments)
                task = args.get("task", "idle")
                description = args.get("task_description", "")
                
                # Format a user-friendly task description from the function call
                if description:
                    full_task = f"{task.replace('_', ' ')}: {description}"
                else:
                    full_task = task.replace('_', ' ')
                
                return {"new_task": full_task}
            
            # Fallback if the function call format is unexpected
            return {"new_task": "idle"}
            
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            # Log the error and fall back to text extraction
            print(f"Error parsing LLM function call: {e}")
            print(f"Raw response: {response}")
            
            # Attempt to extract useful content from a text response if function call failed
            content = response.choices[0].message.content
            if content:
                # Try different extraction methods as before
                task_match = re.search(r'task["\s:]+([^"]+?)["\s}]', content)
                if task_match:
                    return {"new_task": task_match.group(1).strip()}
            
            # Last resort fallback
            return {"new_task": "idle"}
    
    def _get_mock_response(self, query):
        """Generate a mock response when the API is not available."""
        # Simulate API latency
        time.sleep(0.2)
        
        # Define the available tasks for each NPC type
        available_tasks = {
            "common": [
                "patrol",
                "follow player", 
                "guard position", 
                "wander",
                "idle",
                "greet nearby"
            ],
            "villager": [
                "tend crops",
                "rest at home",
                "talk to others"
            ],
            "guard": [
                "inspect surroundings"
            ],
            "merchant": [
                "sell wares",
                "manage inventory"
            ]
        }
        
        # Get NPC type and prepare task list
        npc_type = query.get("npc_type", "villager")
        
        # Start with common tasks for all NPCs
        task_options = available_tasks["common"].copy()
        
        # Add type-specific tasks
        if npc_type in available_tasks:
            task_options.extend(available_tasks[npc_type])
        
        # If the player is nearby, increase chance of interactive tasks
        if query.get("player_interaction") in ["player nearby", "player very close"]:
            interactive_tasks = ["follow player", "greet nearby"]
            # Add these tasks multiple times to increase their probability
            for _ in range(3):  # Add 3 copies to increase probability
                task_options.extend(interactive_tasks)
        
        # Choose a random task, but avoid repeating the current task if possible
        current_task = query.get("current_task")
        if current_task in task_options and len(task_options) > 1:
            # Try to remove the exact match
            task_options.remove(current_task)
            
            # Also try to avoid similar tasks (e.g., if current is "patrol the village", avoid other patrol tasks)
            current_base_task = current_task.split()[0] if " " in current_task else current_task
            task_options = [t for t in task_options if not t.startswith(current_base_task)]
        
        # If we've removed too many options, restore the common tasks
        if not task_options:
            task_options = available_tasks["common"]
        
        # Choose a random task from the options
        new_task = random.choice(task_options)
        
        return {"new_task": new_task} 