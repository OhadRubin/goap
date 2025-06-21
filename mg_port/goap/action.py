"""# 📁 goap/action.py

## Purpose
Defines the abstract template for actions - representing what an agent CAN DO without specifying concrete targets or parameters. This file is dedicated exclusively to the Action concept, which is a fundamental building block of GOAP.

## Conceptual Overview
Actions in GOAP represent agent capabilities - they are templates that define a category of behavior an agent can perform. The key insight is that actions are separate from their specific parameters. For example, "Attack" is an action template that becomes concrete instances like "Attack(Goblin)" or "Attack(Orc)" through the parameterization system.

This file consolidates the C# `Action.cs` and the `ExecutionStatus` enum. The action's core logic is provided as a callable `executor` during initialization, keeping the action definition separate from its implementation.

## Design Rationale
- **Why a separate file**: Actions are a fundamental GOAP concept deserving isolation. This makes the codebase more modular and allows action logic to evolve independently.
- **Why templates vs instances**: This separation allows for dynamic action generation based on world state, a key feature of the original C# implementation.
- **Why co-locate ExecutionStatus**: This enum is intrinsically tied to the lifecycle and return value of an action's executor - it represents the only valid return values from any action execution.

## Dependencies
- **Imports**: `from enum import Enum`
- **Used by**: `agent.py` (for execution), `parameters.py` (for variant generation), `graph.py` (for state transitions)
- **Uses**: None (leaf module - this is intentional to avoid circular dependencies)

## Implementation Structure

### Enumerations

```
class ExecutionStatus(Enum)                    (lines 13-19)
    SUCCEEDED                                   (line 15)
    FAILED                                      (line 16)
    EXECUTING                                   (line 17)
```

The `ExecutionStatus` enum represents the possible outcomes of executing an action. These values are fundamentally tied to action execution and must be returned by all executor functions:
- `SUCCEEDED`: Action completed successfully, remove from plan
- `FAILED`: Action failed, abandon current plan
- `EXECUTING`: Action still in progress, keep in plan for next step

### Classes

```
class Action                                    (lines 22-98)
```

The Action class is the primary content of this file. It stores:
- The action's `name` (identifier)
- Base `cost` (used for planning, may be modified by parameters)
- `preconditions` dictionary (world state requirements)
- `postconditions`/`effects` dictionary (changes to world state)
- `executor` callable (the actual logic to run)
- `parameterizers` list (for generating concrete variants)

### Methods

```
def __init__(self, name: str, cost: float,     (lines 25-45)
            preconditions: dict, effects: dict,
            executor: callable, 
            parameterizers: list | None)
```
Initializes an action template. The method accepts all the defining characteristics of an action. The `parameterizers` parameter is optional (defaults to None) to support both simple, parameter-free actions and complex parameterized ones.

```
def is_possible(self, state: dict) -> bool     (lines 48-75)
```
Checks if the action's preconditions are met by a given world state. This method is used by the graph module to determine if a state transition is valid. It contains sub-logic to evaluate:
- Standard key-value preconditions (e.g., `has_key: true`)
- Comparative preconditions (e.g., `health > 50`)
- Arithmetic preconditions (if implemented)

The condition logic handles different types of conditions that were present in the C# implementation.

```
def apply_effects(self, state: dict) -> dict   (lines 78-98)
```
Takes a world state and returns a NEW state dictionary with the action's effects applied. This method:
- Creates a copy of the input state (important for immutability in the search algorithm)
- Applies simple value assignments (e.g., `door_open: true`)
- Handles arithmetic modifications (e.g., `health: +10`)
- Is used by the graph module to simulate the outcome of taking this action

## Key Design Decisions

1. **Immutability**: The `apply_effects` method returns a new state rather than modifying the input, which is crucial for the search algorithm's correctness.

2. **Callable Executor**: Rather than subclassing for each action type, the implementation uses composition - actions store a callable executor function. This is more Pythonic and flexible than the inheritance-heavy C# approach.

3. **Dictionary-based State**: Preconditions and effects use dictionaries, allowing for flexible world state representation without requiring a fixed schema.

4. **Co-location of ExecutionStatus**: Unlike the C# project which had various enums in separate files, ExecutionStatus lives here because it's meaningless outside the context of action execution.

## Relationship to C# Original

This file primarily consolidates:
- `MountainGoap/Action.cs` - The main Action class
- Parts of `CallbackDelegates` folder - The executor callback signature
- The ExecutionStatus enum (location varies in C# structure)

The Python version simplifies the C# approach by using Python's dynamic typing and first-class functions instead of delegates and complex type hierarchies.

---"""

from enum import Enum
from typing import Dict, Any


class ExecutionStatus(Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXECUTING = "executing"


class Action:
    def __init__(self):
        pass
    
    def is_possible(self):
        pass
    
    def apply_effects(self):
        pass