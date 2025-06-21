"""# 📁 goap/agent.py

## Purpose
The MAIN PUBLIC-FACING CLASS that integrates all other components. This file defines the Agent class, which manages state, coordinates planning and execution, and provides the primary interface for users of the library. It acts as the conductor that orchestrates all the GOAP subsystems.

## Conceptual Overview
The Agent is the living entity that uses GOAP to achieve its goals. It:
- Maintains its understanding of the world (state)
- Has desires it wants to achieve (goals)
- Knows what it can do (actions)
- Can perceive its environment (sensors)
- Executes plans to achieve its goals

The agent follows a sense-plan-act cycle:
1. **Sense**: Run sensors to update world state
2. **Plan**: If needed, find the best plan for the most important goal
3. **Act**: Execute the next action in the current plan

This cycle repeats continuously, allowing the agent to respond to changing conditions and pursue its goals intelligently.

## Design Rationale
- **Why a class**: Unlike the stateless planner and search functions, the agent has persistent state that needs to be maintained between steps.
- **Why single step() method**: Provides a simple interface for game integration - just call step() each frame/turn.
- **Why private helper methods**: Separates the public API from implementation details, making the class easier to use and modify.
- **Why co-locate StepMode**: This enum directly controls the step() method's behavior and has no meaning outside this context.

## Dependencies
- **Imports**: `from enum import Enum`
- **Used by**: User code (this is the main public interface)
- **Uses**: All other modules - `planner.py`, `action.py`, `goal.py`, `sensor.py`

## Implementation Structure

### Enumerations

```
class StepMode(Enum)                           (lines 15-19)
    DEFAULT                                     (line 17)
    ONE_ACTION                                  (line 18)
```

Controls how the step() method behaves:
- `DEFAULT`: Normal operation - sense, plan if needed, act
- `ONE_ACTION`: Force one action execution even if planning is needed

### Classes

```
class Agent                                     (lines 22-130)
```

The main agent class that users instantiate and interact with. Stores:
- `name`: Identifier for the agent
- `state`: Dictionary representing the agent's world knowledge
- `actions`: List of action templates the agent can perform
- `goals`: List of goals the agent wants to achieve
- `sensors`: List of sensors for perceiving the world
- `current_plan`: The active plan being executed (internal)

### Methods

```
def __init__(self,                             (lines 25-45)
    name: str,
    initial_state: dict,
    actions: list[Action],
    goals: list[BaseGoal],
    sensors: list[Sensor])
```

Initializes the agent with all its components. Also sets up internal attributes like `current_plan = None`. The agent takes ownership of all provided components.

```
def step(self,                                 (lines 48-80)
    mode: StepMode = StepMode.DEFAULT) -> None
```

The primary public method and main entry point for agent activity. Orchestrates the sense-plan-act cycle:
1. Always runs sensors via `_run_sensors()`
2. Checks if a new plan is needed (no plan or plan invalidated)
3. If planning needed and mode allows, calls `_find_new_plan()`
4. If plan exists, calls `_execute_current_action()`

This method is designed to be called once per game frame/turn.

```
def _run_sensors(self) -> None                 (lines 83-90)
```

Private helper that iterates through all sensors and calls their run() method, passing the agent's state dictionary. This ensures the agent's world knowledge is up-to-date before planning or acting.

```
def _find_new_plan(self) -> None               (lines 93-102)
```

Private helper that:
1. Calls the planner module's `orchestrate_planning()` function
2. Passes self as the agent parameter
3. Updates `self.current_plan` with the result (may be None)

This method encapsulates all interaction with the planning system.

```
def _execute_current_action(self) -> None      (lines 105-130)
```

Private helper that manages plan execution:
1. Pops the next action from the current plan
2. Calls the action's executor function
3. Handles the returned ExecutionStatus:
   - `SUCCEEDED`: Action complete, already removed from plan
   - `FAILED`: Clear the entire plan (needs replanning)
   - `EXECUTING`: Keep action in plan for next step

## Key Design Decisions

1. **State Ownership**: The agent owns and manages its state dictionary. Sensors modify it directly, while actions receive copies.

2. **Plan as List**: The current plan is a simple list of actions that's consumed from the front. This makes execution logic straightforward.

3. **Lazy Planning**: Plans are only generated when needed (no plan or plan failed), not every step. This improves performance.

4. **Single Responsibility**: The agent coordinates but delegates - it doesn't implement planning, searching, or action logic itself.

5. **Failure Handling**: When an action fails, the entire plan is abandoned. This ensures the agent replans with fresh information.

## Integration Patterns

The agent is designed to integrate easily with game loops:
```python
# Game initialization
agent = Agent(name="Guard", ...)

# Game loop
while game_running:
    agent.step()  # That's it!
```

## Event Hooks (Future Extension)

While not implemented in the base version, the agent is the natural place for event hooks:
- `on_planning_started`
- `on_plan_found` / `on_planning_failed`
- `on_action_started` / `on_action_completed`
- `on_goal_achieved`

## Relationship to C# Original

This file corresponds to:
- `MountainGoap/Agent.cs` - The main agent class
- Parts of the execution logic from various C# files
- The step mode concept from the C# implementation

The Python version simplifies by:
- Using dictionary-based state instead of complex type systems
- Cleaner plan execution logic
- More Pythonic method organization
"""
from enum import Enum


class StepMode(Enum):
    DEFAULT = "default"
    ONE_ACTION = "one_action"


class Agent:
    def __init__(self):
        pass
    
    def step(self):
        pass
    
    def _run_sensors(self):
        pass
    
    def _find_new_plan(self):
        pass
    
    def _execute_current_action(self):
        pass