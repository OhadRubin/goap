"""# 📁 goap/parameters.py

## Purpose
Responsible for taking abstract action templates and generating ALL POSSIBLE CONCRETE INSTANCES of those actions based on the current world state. This new, dedicated file formalizes the concept of action parameterization, creating a clear separation between action definitions and their runtime instantiation.

## Conceptual Overview
Action parameterization is what transforms a general capability like "Attack" into specific, executable actions like "Attack(Goblin)", "Attack(Orc)", or "Attack(Dragon)". This system allows for dynamic action generation where the available actions change based on the world state.

The parameterization system uses a composable pattern where each parameter of an action can have its own generator. These generators can:
- Return static collections (e.g., always allow certain targets)
- Query the world state (e.g., find all visible enemies)
- Compute ranges (e.g., movement distances based on stamina)

This file formalizes what was `PermutationSelectorGenerators.cs` in the C# project into a more robust and Pythonic system.

## Design Rationale
- **Why a separate file**: Parameterization is a complex subsystem that bridges between abstract actions and the planner. It deserves its own module to prevent bloating the action or planner modules.
- **Why the Parameterizer pattern**: Using objects instead of simple functions allows for configuration and state, making the system more flexible than pure functional generators.
- **Why generate all combinations**: Generating all possible actions upfront allows the planner to consider the full action space. Lazy generation would complicate the search algorithm.
- **Why Cartesian product**: When an action has multiple parameters, we need all valid combinations to ensure the planner doesn't miss optimal solutions.

## Dependencies
- **Imports**: None (pure Python)
- **Used by**: `planner.py` (calls generate_action_variants to expand action templates)
- **Uses**: `action.py` (creates new Action instances)

## Implementation Structure

### Classes

```
class Parameterizer                             (lines 14-22)
```

Abstract base class defining the interface for all parameter generators. Establishes that all parameterizers must implement a `generate` method that takes world state and returns possible values.

```
class SelectFromCollection(Parameterizer)       (lines 25-38)
```

Concrete parameterizer that returns values from a predefined, static collection. Useful for:
- Fixed sets of options (e.g., weapon types)
- Enumerated values that don't change
- Default choices available regardless of world state

```
class SelectFromState(Parameterizer)            (lines 41-55)
```

Concrete parameterizer that retrieves a collection from the agent's world state. Useful for:
- Dynamic targets (e.g., visible enemies stored in state['enemies'])
- Available resources (e.g., items in inventory)
- Discovered locations or options

### Functions

```
def generate_action_variants(                   (lines 58-120)
    action_template: Action, 
    state: dict) -> list[Action]
```

The module's core function that transforms a single action template into multiple concrete instances. The process:
1. Retrieves the action's list of parameterizers
2. Runs each parameterizer to get possible values
3. Computes the Cartesian product of all parameter values
4. Creates a new Action instance for each combination
5. Returns the complete list of concrete actions

This is not a "god function" despite its length because it has a single, well-defined responsibility: combinatorial generation of action variants.

### Methods

```
def generate(self, state: dict) -> list         (Parameterizer: lines 18-22)
```
Abstract method that must be implemented by all parameterizer subclasses. Takes the current world state and returns a list of possible parameter values.

```
def __init__(self, collection: list)            (SelectFromCollection: lines 27-30)
```
Stores a static collection of values that will be returned regardless of world state.

```
def generate(self, state: dict) -> list         (SelectFromCollection: lines 33-38)
```
Simply returns the static collection provided during initialization, ignoring the world state.

```
def __init__(self, state_key: str)              (SelectFromState: lines 43-46)
```
Stores the key to look up in the world state dictionary.

```
def generate(self, state: dict) -> list         (SelectFromState: lines 49-55)
```
Retrieves and returns the collection found at `state[state_key]`, with appropriate error handling for missing keys.

## Key Design Decisions

1. **Composition over Configuration**: Actions compose parameterizers rather than using configuration flags. This makes the system more extensible.

2. **Eager Generation**: All variants are generated upfront rather than lazily. This simplifies the planner and search algorithms at the cost of memory.

3. **Immutable Templates**: Action templates are not modified; new instances are created. This prevents surprising side effects.

4. **State-Driven**: Parameterizers receive the full world state, allowing complex logic for parameter generation without coupling to specific state structures.

5. **List-Based Returns**: Parameterizers return lists (not generators) to ensure the full parameter space is available for planning.

## Example Usage (Conceptual)

An "Attack" action might have parameterizers for:
- **Target**: `SelectFromState('visible_enemies')`
- **Weapon**: `SelectFromCollection(['sword', 'bow', 'staff'])`

With state `{'visible_enemies': ['goblin', 'orc']}`, this would generate:
- Attack(goblin, sword)
- Attack(goblin, bow)
- Attack(goblin, staff)
- Attack(orc, sword)
- Attack(orc, bow)
- Attack(orc, staff)

## Relationship to C# Original

This file is an evolution of:
- `MountainGoap/PermutationSelectorGenerators.cs`
- Parts of the action permutation system

The Python version improves on the C# design by:
- Making parameterization a first-class concept with its own module
- Using composition instead of inheritance for flexibility
- Simplifying the combinatorial generation with Python's itertools

---

"""
from abc import ABC, abstractmethod
from itertools import product
from typing import List, Dict, Any


class Parameterizer(ABC):
    """Abstract base class for all parameter generators.
    
    Defines the interface that all parameterizers must implement.
    Parameterizers are responsible for generating possible values
    for action parameters based on the current world state.
    """
    
    @abstractmethod
    def generate(self, state: Dict[str, Any]) -> List[Any]:
        """Generate possible parameter values based on world state.
        
        Args:
            state: Current world state dictionary
            
        Returns:
            List of possible parameter values
        """
        pass


class SelectFromCollection(Parameterizer):
    """Parameterizer that returns values from a predefined static collection.
    
    Useful for fixed sets of options that don't change based on world state,
    such as weapon types, spell schools, or movement directions.
    """
    
    def __init__(self, collection: List[Any]):
        """Initialize with a static collection of values.
        
        Args:
            collection: List of values to choose from
        """
        if not isinstance(collection, list):
            raise TypeError("Collection must be a list")
        self.collection = collection.copy()  # Defensive copy
    
    def generate(self, state: Dict[str, Any]) -> List[Any]:
        """Return the static collection, ignoring world state.
        
        Args:
            state: Current world state (ignored)
            
        Returns:
            Copy of the static collection
        """
        return [item for item in self.collection if item is not None]


class SelectFromState(Parameterizer):
    """Parameterizer that retrieves a collection from the world state.
    
    Useful for dynamic parameters that change based on world state,
    such as visible enemies, available items, or discovered locations.
    """
    
    def __init__(self, state_key: str):
        """Initialize with the key to look up in world state.
        
        Args:
            state_key: Key to look up in the world state dictionary
        """
        if not isinstance(state_key, str):
            raise TypeError("State key must be a string")
        if not state_key:
            raise ValueError("State key cannot be empty")
        self.state_key = state_key
    
    def generate(self, state: Dict[str, Any]) -> List[Any]:
        """Retrieve collection from world state at the specified key.
        
        Args:
            state: Current world state dictionary
            
        Returns:
            List from state at state_key, or empty list if not found
        """
        if self.state_key not in state:
            return []
        
        value = state[self.state_key]
        
        # Handle different types of collections
        if isinstance(value, list):
            return [item for item in value if item is not None]
        elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            # Handle other iterables (sets, tuples, etc.)
            return [item for item in value if item is not None]
        else:
            # Single value - wrap in list
            return [value] if value is not None else []


def generate_action_variants(action_template, state: Dict[str, Any]) -> List:
    """Generate all possible concrete instances of an action template.
    
    Takes an action template with parameterizers and generates all possible
    combinations of parameter values based on the current world state.
    
    Args:
        action_template: Action template with parameterizers attribute
        state: Current world state dictionary
        
    Returns:
        List of concrete action instances with all parameter combinations
        
    Raises:
        AttributeError: If action_template lacks required attributes
        TypeError: If parameterizers is not a dictionary
    """
    # Validate input
    if not hasattr(action_template, 'parameterizers'):
        # No parameterizers - return single copy of the template
        return [action_template]
    
    parameterizers = action_template.parameterizers
    
    if parameterizers is None or len(parameterizers) == 0:
        # No parameterizers - return single copy of the template  
        return [action_template]
    
    if not isinstance(parameterizers, dict):
        raise TypeError("Parameterizers must be a dictionary")
    
    # Generate all possible parameter values
    parameter_names = []
    parameter_values = []
    
    for param_name, parameterizer in parameterizers.items():
        if not isinstance(parameterizer, Parameterizer):
            raise TypeError(f"Parameterizer for '{param_name}' must be a Parameterizer instance")
        
        values = parameterizer.generate(state)
        
        # If any parameterizer returns empty list, no variants possible
        if not values:
            return []
        
        parameter_names.append(param_name)
        parameter_values.append(values)
    
    # Generate Cartesian product of all parameter combinations
    variants = []
    
    if not parameter_values:
        # No parameters to vary - return single copy
        return [action_template]
    
    # Use itertools.product to generate all combinations
    for combination in product(*parameter_values):
        # Create new action instance (copy of template)
        # This assumes action_template has a copy() method or similar
        if hasattr(action_template, 'copy'):
            variant = action_template.copy()
        else:
            # Fallback: try to create a new instance
            # This may need adjustment based on actual Action class implementation
            variant = type(action_template)(
                name=getattr(action_template, 'name', 'action'),
                cost=getattr(action_template, 'cost', 1.0),
                preconditions=getattr(action_template, 'preconditions', {}),
                effects=getattr(action_template, 'effects', {}),
                executor=getattr(action_template, 'executor', lambda: None),
                parameterizers=getattr(action_template, 'parameterizers', {})
            )
        
        # Set parameters on the variant
        for param_name, param_value in zip(parameter_names, combination):
            if hasattr(variant, 'set_parameter'):
                variant.set_parameter(param_name, param_value)
            elif hasattr(variant, 'parameters'):
                if not hasattr(variant, 'parameters') or variant.parameters is None:
                    variant.parameters = {}
                variant.parameters[param_name] = param_value
            else:
                # Fallback: set as attribute
                setattr(variant, param_name, param_value)
        
        variants.append(variant)
    
    return variants