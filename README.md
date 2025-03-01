# LLM-Controlled NPCs

A story-driven sandbox adventure game with Non-Player Characters (NPCs) dynamically controlled by a Large Language Model (LLM).

## Game Concept

In this game, NPCs receive high-level action commands (e.g., "Patrol the village," "Find food," "Trade with villagers") directly from an LLM. NPCs autonomously interpret and perform tasks based on received instructions and dynamically adapt to the game environment.

## Features

- **LLM-Controlled NPCs**: NPCs receive dynamic behavior instructions from a language model
- **Autonomous Task Execution**: NPCs continue executing tasks independently
- **Dynamic Behavior**: NPCs adapt based on the environment and player interactions
- **Emergent Storytelling**: Create unpredictable, dynamic narratives through NPC behaviors
- **Non-Blocking AI Processing**: LLM requests are processed asynchronously, preventing game freezes

## Requirements

- Python 3.12 or higher
- pygame
- openai (for API integration)
- python-dotenv

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-npc.git
   cd ai-npc
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -e .
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file and add your OpenAI API key.

## Running the Game

Start the game with:

```
python run_game.py
```

Controls:
- **W/A/S/D or Arrow Keys**: Move the player
- **ESC**: Quit the game

## Testing Non-Blocking LLM Updates

You can test the non-blocking LLM update system with:

```
python -m ai_npc.tests.test_non_blocking
```

This test creates multiple NPCs and simulates them requesting tasks simultaneously to verify that the game doesn't freeze during LLM queries.

## Development

### Project Structure

- `ai_npc/`: Main package directory
  - `core/`: Core game components
    - `game_world.py`: Game environment and objects
    - `player.py`: Player character implementation
    - `npc.py`: NPC implementation
    - `llm_controller.py`: LLM integration for NPC behavior
  - `config/`: Configuration files
    - `settings.py`: Game settings and parameters
  - `assets/`: Game assets (graphics, audio, etc.)
  - `tests/`: Test modules
    - `test_non_blocking.py`: Test for non-blocking LLM updates

## LLM Integration

The game integrates with language models (like OpenAI's GPT) to control NPC behavior. If an API key is not available, the game will fall back to mock LLM responses.

### Non-Blocking LLM Updates

To prevent the game from freezing when multiple NPCs request new tasks from the LLM, we've implemented a non-blocking queuing system:

1. NPCs request task updates asynchronously
2. Requests are placed in a queue and processed in the background
3. NPCs continue their current tasks while waiting for new instructions
4. Visual indicators show when an NPC is waiting for a new task
5. Only one NPC communicates with the LLM at a time, preventing API throttling

This ensures smooth gameplay even with many NPCs requiring frequent updates from the LLM.

### Communication Protocol

NPCs query the LLM with their current state and context:

```json
{
  "npc_id": "npc_001",
  "npc_type": "guard",
  "current_task": "Guard the town gate",
  "last_completed_task": "Warn villagers of approaching danger",
  "current_state": "idle",
  "environment_context": "evening, raining, low visibility",
  "player_interaction": "none"
}
```

The LLM responds with a new task:

```json
{
  "new_task": "Light torches around the gate and patrol the perimeter"
}
```

## License

[MIT License](LICENSE)

## Credits

- Game Engine: [pygame](https://www.pygame.org/)
- LLM Integration: [OpenAI API](https://openai.com/)
