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
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, Any, Union
import uuid


class ComparisonOperator(Enum):
    """Comparison operators for ComparativeGoal conditions."""
    UNDEFINED = "undefined"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUALS = "less_than_or_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUALS = "greater_than_or_equals"


@dataclass
class ComparisonValuePair:
    """Pairs a comparison operator with a value for ComparativeGoal conditions."""
    operator: ComparisonOperator
    value: Any
    
    def __init__(self, operator: ComparisonOperator = ComparisonOperator.UNDEFINED, value: Any = None):
        self.operator = operator
        self.value = value


class BaseGoal(ABC):
    """Abstract base class for all goal types."""
    
    def __init__(self, name: str = None, weight: float = 1.0):
        """Initialize a base goal with name and weight.
        
        Args:
            name: Goal identifier. If None, generates a unique name.
            weight: Relative importance of this goal (higher = more important).
        """
        self.name = name if name is not None else f"Goal {uuid.uuid4()}"
        self.weight = weight
    
    @abstractmethod
    def is_satisfied(self, state: Dict[str, Any]) -> bool:
        """Check if this goal is satisfied by the given world state.
        
        Args:
            state: Current world state dictionary.
            
        Returns:
            True if the goal is satisfied, False otherwise.
        """
        pass


class Goal(BaseGoal):
    """Concrete goal for achieving exact world states."""
    
    def __init__(self, name: str = None, weight: float = 1.0, desired_state: Dict[str, Any] = None):
        """Initialize an exact-state goal.
        
        Args:
            name: Goal identifier.
            weight: Relative importance of this goal.
            desired_state: Dictionary of key-value pairs that must all match the world state.
        """
        super().__init__(name, weight)
        self.desired_state = desired_state if desired_state is not None else {}
    
    def is_satisfied(self, state: Dict[str, Any]) -> bool:
        """Check if all desired state conditions are met.
        
        Args:
            state: Current world state dictionary.
            
        Returns:
            True if all key-value pairs in desired_state match the world state.
        """
        for key, desired_value in self.desired_state.items():
            if key not in state:
                return False
            
            current_value = state[key]
            
            # Handle None values specially
            if current_value is None and current_value != desired_value:
                return False
            
            # Use equals comparison for non-None values
            if current_value is not None and current_value != desired_value:
                return False
                
        return True


class ComparativeGoal(BaseGoal):
    """Concrete goal for achieving states relative to threshold values."""
    
    def __init__(self, name: str = None, weight: float = 1.0, conditions: Dict[str, ComparisonValuePair] = None):
        """Initialize a comparative goal.
        
        Args:
            name: Goal identifier.
            weight: Relative importance of this goal.
            conditions: Dictionary mapping state keys to comparison conditions.
        """
        super().__init__(name, weight)
        self.conditions = conditions if conditions is not None else {}
    
    def is_satisfied(self, state: Dict[str, Any]) -> bool:
        """Check if all comparison conditions are met.
        
        Args:
            state: Current world state dictionary.
            
        Returns:
            True if all comparison conditions evaluate to True.
        """
        for key, comparison in self.conditions.items():
            if key not in state:
                return False
                
            current_value = state[key]
            target_value = comparison.value
            operator = comparison.operator
            
            # Undefined operator always fails
            if operator == ComparisonOperator.UNDEFINED:
                return False
            
            # Handle different comparison operators
            if operator == ComparisonOperator.EQUALS:
                if current_value != target_value:
                    return False
            elif operator == ComparisonOperator.NOT_EQUALS:
                if current_value == target_value:
                    return False
            elif operator == ComparisonOperator.LESS_THAN:
                if not self._is_less_than(current_value, target_value):
                    return False
            elif operator == ComparisonOperator.LESS_THAN_OR_EQUALS:
                if not self._is_less_than_or_equals(current_value, target_value):
                    return False
            elif operator == ComparisonOperator.GREATER_THAN:
                if not self._is_greater_than(current_value, target_value):
                    return False
            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUALS:
                if not self._is_greater_than_or_equals(current_value, target_value):
                    return False
                    
        return True
    
    def _is_less_than(self, a: Any, b: Any) -> bool:
        """Check if a < b for comparable types."""
        if a is None or b is None:
            return False
        try:
            return a < b
        except (TypeError, ValueError):
            return False
    
    def _is_less_than_or_equals(self, a: Any, b: Any) -> bool:
        """Check if a <= b for comparable types."""
        if a is None or b is None:
            return False
        try:
            return a <= b
        except (TypeError, ValueError):
            return False
    
    def _is_greater_than(self, a: Any, b: Any) -> bool:
        """Check if a > b for comparable types."""
        if a is None or b is None:
            return False
        try:
            return a > b
        except (TypeError, ValueError):
            return False
    
    def _is_greater_than_or_equals(self, a: Any, b: Any) -> bool:
        """Check if a >= b for comparable types."""
        if a is None or b is None:
            return False
        try:
            return a >= b
        except (TypeError, ValueError):
            return False


class ExtremeGoal(BaseGoal):
    """Concrete goal for maximizing or minimizing numeric values.
    
    Note: ExtremeGoals never actually satisfy - they provide direction
    for the planning heuristic to optimize values.
    """
    
    def __init__(self, name: str = None, weight: float = 1.0, optimizations: Dict[str, bool] = None):
        """Initialize an extreme goal.
        
        Args:
            name: Goal identifier.
            weight: Relative importance of this goal.
            optimizations: Dictionary mapping state keys to optimization direction.
                         True = maximize, False = minimize.
        """
        super().__init__(name, weight)
        self.optimizations = optimizations if optimizations is not None else {}
    
    def is_satisfied(self, state: Dict[str, Any]) -> bool:
        """ExtremeGoals are never satisfied - they provide optimization direction.
        
        Args:
            state: Current world state dictionary (unused).
            
        Returns:
            Always False - extreme goals guide heuristics, not termination.
        """
        return False
    

def test_basic_functionality():
    """Test basic functionality of goal classes."""
    # Test ComparisonOperator enum
    print('Testing ComparisonOperator...')
    assert ComparisonOperator.EQUALS.value == 'equals'
    assert ComparisonOperator.GREATER_THAN.value == 'greater_than'
    assert ComparisonOperator.LESS_THAN_OR_EQUALS.value == 'less_than_or_equals'
    print('✓ ComparisonOperator works')
    
    # Test ComparisonValuePair
    print('Testing ComparisonValuePair...')
    cvp = ComparisonValuePair(ComparisonOperator.GREATER_THAN, 50)
    assert cvp.operator == ComparisonOperator.GREATER_THAN
    assert cvp.value == 50
    print('✓ ComparisonValuePair works')
    
    # Test Goal (exact state)
    print('Testing Goal...')
    goal = Goal('test_goal', 1.0, {'health': 100, 'has_key': True})
    assert goal.name == 'test_goal'
    assert goal.weight == 1.0
    assert goal.is_satisfied({'health': 100, 'has_key': True, 'extra': 'data'}) == True
    assert goal.is_satisfied({'health': 50, 'has_key': True}) == False
    assert goal.is_satisfied({'health': 100}) == False
    print('✓ Goal works')
    
    # Test ComparativeGoal
    print('Testing ComparativeGoal...')
    conditions = {
        'health': ComparisonValuePair(ComparisonOperator.GREATER_THAN_OR_EQUALS, 50),
        'score': ComparisonValuePair(ComparisonOperator.LESS_THAN, 100)
    }
    comp_goal = ComparativeGoal('comp_goal', 2.0, conditions)
    assert comp_goal.is_satisfied({'health': 75, 'score': 80}) == True
    assert comp_goal.is_satisfied({'health': 30, 'score': 80}) == False
    assert comp_goal.is_satisfied({'health': 75, 'score': 120}) == False
    print('✓ ComparativeGoal works')
    
    # Test ExtremeGoal
    print('Testing ExtremeGoal...')
    extreme_goal = ExtremeGoal('extreme_goal', 3.0, {'gold': True, 'distance': False})
    assert extreme_goal.is_satisfied({'gold': 1000, 'distance': 5}) == False
    print('✓ ExtremeGoal works')
    
    print('All tests passed!')


def test_inheritance():
    """Test inheritance structure of goal classes."""
    from abc import ABC
    
    # Test inheritance structure
    print('Testing inheritance structure...')
    assert issubclass(BaseGoal, ABC)
    assert issubclass(Goal, BaseGoal)
    assert issubclass(ComparativeGoal, BaseGoal)
    assert issubclass(ExtremeGoal, BaseGoal)
    
    # Test that BaseGoal is abstract
    try:
        base = BaseGoal()
        base.is_satisfied({})
        assert False, 'BaseGoal should be abstract'
    except TypeError:
        print('✓ BaseGoal is properly abstract')
    
    # Test polymorphism
    goals = [
        Goal('test1', 1.0, {'key': 'value'}),
        ComparativeGoal('test2', 2.0, {'num': ComparisonValuePair(ComparisonOperator.GREATER_THAN, 5)}),
        ExtremeGoal('test3', 3.0, {'gold': True})
    ]
    
    for goal in goals:
        assert isinstance(goal, BaseGoal)
        assert hasattr(goal, 'name')
        assert hasattr(goal, 'weight')
        assert hasattr(goal, 'is_satisfied')
        assert callable(goal.is_satisfied)
    
    print('✓ Polymorphism works correctly')
    print('All inheritance tests passed!')


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from goap.goal import *
    
    test_basic_functionality()
    test_inheritance()
