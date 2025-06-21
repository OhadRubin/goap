"""# 📁 goap/goal.py

## Purpose
Defines what an agent WANTS TO ACHIEVE. This file contains the base goal interface and all concrete implementations for different types of objectives. It isolates all goal-related logic, consolidating the various goal types from the C# project.

## Conceptual Overview
Goals in GOAP represent desired world states or conditions that drive agent behavior. The system supports three distinct types of goals:
- **Exact State Goals**: Achieve specific world states (e.g., "door is open")
- **Comparative Goals**: Meet threshold conditions (e.g., "health >= 50")
- **Extreme Goals**: Optimize values (e.g., "maximize gold" or "minimize distance")

Each goal has a weight that represents its importance relative to other goals. The planner uses these weights along with action costs to determine which goal to pursue and how to achieve it.

## Design Rationale
- **Why separate goal types**: Different goal types require different satisfaction logic and heuristic calculations. The type hierarchy makes this explicit.
- **Why co-locate ComparisonOperator and ComparisonValuePair**: These data structures are used exclusively by ComparativeGoal and have no meaning outside this context. This follows the principle of co-locating related code.
- **Why weights**: Goals need relative priorities so the planner can make trade-offs between expensive plans for important goals vs. cheap plans for less important goals.
- **Why ExtremeGoal never satisfies**: Extreme goals provide direction for optimization rather than terminal conditions. They influence the heuristic function in the search algorithm.

## Dependencies
- **Imports**: `from dataclasses import dataclass`, `from enum import Enum`
- **Used by**: `agent.py` (stores goal list), `planner.py` (evaluates goals), `search.py` (checks satisfaction and calculates heuristics)
- **Uses**: None (leaf module)

## Implementation Structure

### Enumerations

```
class ComparisonOperator(Enum)                  (lines 14-22)
    EQUALS                                      (line 16)
    NOT_EQUALS                                  (line 17)
    LESS_THAN                                   (line 18)
    GREATER_THAN                                (line 19)
    ... (and so on)
```

The `ComparisonOperator` enum defines all possible comparison operations for ComparativeGoal conditions. This consolidates the C# ComparisonOperator enum and supports flexible threshold-based goals.

### Data Classes

```
@dataclass
class ComparisonValuePair                       (lines 25-30)
    operator: ComparisonOperator                (line 27)
    value: any                                  (line 28)
```

A simple data class that bundles a comparison operator with a value. This is used exclusively by ComparativeGoal to specify conditions like "greater than 50" in a structured way.

### Classes

```
class BaseGoal                                  (lines 33-45)
```

Abstract base class establishing the common interface for all goals. Every goal must have:
- A `name` for identification
- A `weight` for relative importance
- An `is_satisfied` method to check if the goal is met

```
class Goal(BaseGoal)                           (lines 48-68)
```

Concrete implementation for achieving exact world states. Stores:
- `desired_state`: A dictionary of key-value pairs that must all be present in the world state
- Used for binary conditions like "has_key: true" or "door_open: false"

```
class ComparativeGoal(BaseGoal)                (lines 71-115)
```

Concrete implementation for achieving states relative to values. Stores:
- `conditions`: Dictionary mapping state keys to ComparisonValuePair objects
- Supports flexible conditions like "health >= 50" or "distance < 10"
- The satisfaction logic evaluates each condition using the specified operator

```
class ExtremeGoal(BaseGoal)                    (lines 118-128)
```

Concrete implementation for maximizing or minimizing numeric values. Stores:
- `optimizations`: Dictionary mapping state keys to boolean values (True for maximize, False for minimize)
- Never actually "satisfied" - provides direction for the planning heuristic
- Examples: "maximize gold", "minimize distance_to_target"

### Methods

```
def __init__(self, name: str, weight: float)   (BaseGoal: lines 35-40)
```
Base constructor that all goal types inherit. Establishes the common attributes.

```
def is_satisfied(self, state: dict) -> bool    (BaseGoal: lines 43-45)
```
Abstract method that each goal type must implement. Returns True if the given world state meets the goal's conditions.

```
def __init__(self, name: str, weight: float,   (Goal: lines 50-57)
            desired_state: dict)
```
Constructor for exact state goals. The `desired_state` parameter is a dictionary of required world state conditions.

```
def is_satisfied(self, state: dict) -> bool    (Goal: lines 60-68)
```
Checks if the target `desired_state` is a subset of the current world state. All key-value pairs in desired_state must match exactly.

```
def __init__(self, name: str, weight: float,   (ComparativeGoal: lines 73-81)
            conditions: dict[str, ComparisonValuePair])
```
Constructor for comparative goals. The `conditions` parameter maps state keys to comparison requirements.

```
def is_satisfied(self, state: dict) -> bool    (ComparativeGoal: lines 84-115)
```
Evaluates the conditions against the current state using the specified comparison operators. Contains logic for each operator type (equals, greater than, etc.).

```
def __init__(self, name: str, weight: float,   (ExtremeGoal: lines 120-125)
            optimizations: dict[str, bool])
```
Constructor for extreme goals. The `optimizations` parameter indicates whether to maximize (True) or minimize (False) each value.

```
def is_satisfied(self, state: dict) -> bool    (ExtremeGoal: lines 127-128)
```
Always returns False. Extreme goals influence planning through heuristics rather than providing terminal conditions.

## Key Design Decisions

1. **Type Hierarchy**: Using inheritance with BaseGoal allows the planner and search to work with goals polymorphically while each type implements its own satisfaction logic.

2. **Co-located Support Types**: ComparisonOperator and ComparisonValuePair live in this file rather than a separate types.py because they're meaningless without ComparativeGoal.

3. **Weight as Core Attribute**: Every goal has a weight, making priority a first-class concept in the planning system.

4. **Dictionary-based Conditions**: Like actions, goals use dictionaries for flexibility without requiring a fixed world state schema.

5. **Extreme Goals as Heuristic Guides**: The design choice for extreme goals to never be "satisfied" is intentional - they provide optimization direction rather than termination conditions.

## Relationship to C# Original

This file consolidates several C# files:
- `MountainGoap/Goals/Goal.cs` - The base goal concept
- `MountainGoap/Goals/Goals.cs` - Standard exact-state goals  
- `MountainGoap/Goals/ComparativeGoal.cs` - Threshold-based goals
- `MountainGoap/Goals/ExtremeGoal.cs` - Optimization goals
- Various comparison-related types from the C# project

The Python version benefits from:
- Simpler syntax with dataclasses
- More natural dictionary operations
- Cleaner polymorphism without C#'s interface complexity

---


"""
from enum import Enum


class ComparisonOperator(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"


class ComparisonValuePair:
    def __init__(self):
        self.operator = None
        self.value = None


class BaseGoal:
    def __init__(self):
        pass
    
    def is_satisfied(self):
        pass


class Goal:
    def __init__(self):
        pass
    
    def is_satisfied(self):
        pass


class ComparativeGoal:
    def __init__(self):
        pass
    
    def is_satisfied(self):
        pass


class ExtremeGoal:
    def __init__(self):
        pass
    
    def is_satisfied(self):
        pass