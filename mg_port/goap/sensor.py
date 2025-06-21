"""# 📁 goap/sensor.py

## Purpose
Defines the mechanism for an agent to PERCEIVE and update its understanding of the world. This file provides the Sensor class, which acts as the bridge between the AI's internal state representation and the external game environment.

## Conceptual Overview
Sensors in GOAP are the agent's way of gathering information about the world. They are simple wrappers around callback functions that are executed each step to update the agent's world state with fresh information. 

Unlike actions which change the world, sensors only change the agent's knowledge about the world. This distinction is crucial - sensors are read-only operations from the world's perspective but write operations from the agent's state perspective.

## Design Rationale
- **Why a separate file**: Despite being simple, sensors represent a distinct GOAP concept - perception. Keeping them separate maintains conceptual clarity and allows sensor logic to evolve independently.
- **Why callback-based**: The callback pattern allows game-specific sensing logic to be injected without the GOAP library needing to know about the game's implementation details.
- **Why such a simple class**: The simplicity is intentional. Sensors have one job - run a function that updates state. This focused design prevents feature creep and maintains the single responsibility principle.
- **Why pass state to callback**: The callback receives the agent's state dictionary directly, allowing it to read current values and update them based on game conditions.

## Dependencies
- **Imports**: None (pure Python)
- **Used by**: `agent.py` (stores sensor list and runs them each step)
- **Uses**: None (leaf module)

## Implementation Structure

### Classes

```
class Sensor                                    (lines 11-28)
```

The Sensor class is a straightforward wrapper that serves as a named container for a perception callback. It holds:
- `name`: Identifier for the sensor (e.g., "vision", "health_monitor")
- `callback`: A callable function that updates world state

### Methods

```
def __init__(self, name: str,                  (lines 14-19)
            callback: callable)
```
Initializes a sensor with an identifying name and a callback function. The callback should have the signature `callback(agent_state: dict) -> None` and is provided by the user of the library.

```
def run(self, agent_state: dict) -> None       (lines 22-28)
```
Executes the stored callback function, passing it the agent's current state dictionary. The callback is expected to:
- Read from the game world/environment
- Update the agent_state dictionary with new information
- Not return any value (modifications happen in-place)

## Key Design Decisions

1. **In-place State Modification**: The callback modifies the agent's state dictionary directly rather than returning a new state. This is more efficient and aligns with how sensors conceptually work - they update existing knowledge rather than creating new knowledge from scratch.

2. **No Built-in Sensor Types**: Unlike actions and goals which have type hierarchies, all sensors are instances of the same class. The variety comes from the callbacks, not from subclassing.

3. **Separation from Actions**: Sensors and actions are kept strictly separate even though both involve callbacks. This maintains the conceptual distinction between perception (sensors) and behavior (actions).

4. **Name as Identifier**: Each sensor has a name primarily for debugging and logging purposes. The GOAP system itself doesn't use sensor names for any logic.

## Usage Examples (Conceptual)

While the library doesn't include implementations, sensors would typically be used for:
- **Health Monitor**: Read current health from game and update agent's state
- **Enemy Detector**: Check surroundings and update known enemy positions
- **Resource Scanner**: Identify available resources in the environment
- **Time Tracker**: Update agent's knowledge of game time/turn count

## Relationship to C# Original

This file corresponds to:
- `MountainGoap/Sensor.cs` - The main Sensor class
- Parts of the callback system from `CallbackDelegates`

The Python version simplifies the C# approach by:
- Using Python's first-class functions instead of delegates
- Eliminating any complex type signatures through duck typing
- Keeping the implementation minimal and focused

## Integration with Agent Lifecycle

In the agent's `step()` method, sensors are run first, before planning or action execution. This ensures:
1. The agent always plans with the most current information
2. Sensor updates can invalidate existing plans (e.g., enemy appeared)
3. The world state is consistent throughout the planning phase

The execution order is critical: Sense → Plan → Act.
"""
class Sensor:
    def __init__(self, name: str, callback: callable):
        """Initialize a sensor with an identifying name and callback function.
        
        Args:
            name: Identifier for the sensor (e.g., "vision", "health_monitor")
            callback: A callable function that updates world state.
                     Should have signature: callback(agent_state: dict) -> None
        """
        self.name = name
        self.callback = callback
    
    def run(self, agent_state: dict) -> None:
        """Execute the stored callback function with the agent's current state.
        
        The callback is expected to:
        - Read from the game world/environment
        - Update the agent_state dictionary with new information
        - Not return any value (modifications happen in-place)
        
        Args:
            agent_state: The agent's current state dictionary to update
        """
        self.callback(agent_state)