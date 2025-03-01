"""
Game settings and configuration parameters.
"""

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "LLM-Controlled NPCs"
BACKGROUND_COLOR = (50, 50, 50)  # Dark gray

# Player settings
PLAYER_SPEED = 5
PLAYER_COLOR = (0, 255, 0)  # Green
PLAYER_SIZE = 32

# NPC settings
NPC_COLORS = {
    'villager': (255, 255, 0),  # Yellow
    'guard': (255, 0, 0),       # Red
    'merchant': (0, 0, 255),    # Blue
}
NPC_SIZE = 32
NPC_SPEED = 3
NPC_UPDATE_INTERVAL = 10000  # Time in milliseconds between LLM updates for NPCs

# LLM API settings
LLM_API_TIMEOUT = 10  # Seconds to wait for API response
LLM_MAX_TOKENS = 100  # Maximum number of tokens in the LLM response

# World settings
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000
TILE_SIZE = 32

# Game objects
OBJECT_TYPES = {
    'tree': (0, 100, 0),      # Dark green
    'rock': (100, 100, 100),  # Gray
    'house': (150, 75, 0),    # Brown
} 