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
        
        Tasks should be short, clear instructions like "Patrol the village", "Find food", 
        "Trade with villagers", "Follow the player", etc.
        
        IMPORTANT: Your response MUST be a valid JSON object with ONLY a 'new_task' field containing 
        the task instruction. Example response:
        {"new_task": "Patrol the village"}
        
        Do not include any explanations, markdown formatting, or backticks in your response.
        Return ONLY the JSON object.
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
        
        Based on this information, what should the NPC do next?
        Remember to respond ONLY with a valid JSON object containing the 'new_task' field.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=0.7,
            timeout=LLM_API_TIMEOUT,
            response_format={"type": "json_object"}  # Request JSON format specifically
        )
        
        # Extract and parse the response
        try:
            content = response.choices[0].message.content
            # Remove any backticks or markdown formatting that might be present
            content = content.strip('`')
            if content.startswith('json'):
                content = content[4:]  # Remove 'json' language marker if present
            content = content.strip()
            
            # Try to parse as JSON
            parsed = json.loads(content)
            return parsed
        except (json.JSONDecodeError, AttributeError) as e:
            # If the response is not valid JSON, use more robust extraction
            print(f"Error parsing LLM response as JSON: {e}")
            print(f"Raw content: {content}")
            
            # Try different extraction methods
            
            # Look for JSON pattern
            json_pattern = r'{.*?"new_task".*?:.*?"(.*?)".*?}'
            json_match = re.search(json_pattern, content, re.DOTALL)
            if json_match:
                return {"new_task": json_match.group(1)}
                
            # Look for "new_task" followed by a string
            task_pattern = r'"new_task"["\s:]+([^"]+?)["\s}]'
            task_match = re.search(task_pattern, content)
            if task_match:
                return {"new_task": task_match.group(1).strip()}
                
            # Simple text extraction if contains "new_task"
            if "new_task" in content:
                parts = content.split("new_task")
                if len(parts) > 1:
                    # Extract the text after "new_task", removing common delimiters
                    task_text = parts[1].strip('":,. \n}{')
                    return {"new_task": task_text}
            
            # If all else fails, extract any quoted text that might be a task
            quoted_text = re.search(r'"([^"]+)"', content)
            if quoted_text:
                return {"new_task": quoted_text.group(1)}
                
            # Last resort fallback
            return {"new_task": "idle"}
    
    def _get_mock_response(self, query):
        """Generate a mock response when the API is not available."""
        # Simulate API latency
        time.sleep(0.2)
        
        # List of possible tasks based on NPC type
        tasks = {
            "villager": [
                "Wander around the village",
                "Talk to other villagers",
                "Tend to crops in the field",
                "Rest at home",
                "Visit the market",
                "Prepare food",
                "Idle by the fountain"
            ],
            "guard": [
                "Patrol the village perimeter",
                "Guard the town gate",
                "Inspect suspicious activity",
                "Stand guard at the castle",
                "Follow the player at a distance",
                "Check on other guards",
                "Rest at the barracks"
            ],
            "merchant": [
                "Sell wares at the market",
                "Restock inventory",
                "Advertise special deals",
                "Negotiate with suppliers",
                "Travel between villages",
                "Count profits",
                "Pack up shop for the day"
            ]
        }
        
        # Get tasks for the NPC type, or use a default list
        npc_type = query.get("npc_type", "villager")
        available_tasks = tasks.get(npc_type, tasks["villager"])
        
        # If the player is nearby, potentially interact with them
        if query.get("player_interaction") == "player nearby":
            if random.random() < 0.4:  # 40% chance to interact with nearby player
                if npc_type == "guard":
                    available_tasks.append("Follow the player")
                    available_tasks.append("Watch the player carefully")
                elif npc_type == "merchant":
                    available_tasks.append("Offer goods to the player")
                    available_tasks.append("Approach the player to trade")
                else:
                    available_tasks.append("Greet the player")
                    available_tasks.append("Wave at the player")
        
        # Choose a random task, but avoid repeating the current task if possible
        current_task = query.get("current_task")
        if current_task in available_tasks and len(available_tasks) > 1:
            available_tasks.remove(current_task)
        
        new_task = random.choice(available_tasks)
        
        return {"new_task": new_task} 