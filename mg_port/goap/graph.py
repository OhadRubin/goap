"""# 📁 goap/graph.py

## Purpose
Defines the RULES OF THE WORLD'S STATE TRANSITIONS. This file understands how to get from one state to another by applying actions, but has no knowledge of goals or search algorithms. It answers the fundamental question: "From this state, what states can I reach?"

## Conceptual Overview
The graph module abstracts the GOAP problem as a state transition graph where:
- Nodes are world states (dictionaries)
- Edges are actions that transform one state to another
- Edge weights are action costs

This abstraction allows the search algorithm to be completely generic - it doesn't need to know about actions, effects, or preconditions. It just needs to know how to get successor nodes, which this module provides.

The key insight is that the graph is implicitly defined and dynamically explored. We don't pre-generate all possible states; instead, we generate successors on-demand during the search.

## Design Rationale
- **Why separate from search**: Graph structure (what connects to what) is independent from graph algorithms (how to find paths). This separation allows either to be modified independently.
- **Why separate from actions**: While actions define the rules, the graph module applies those rules in the context of state transitions. This keeps action logic focused on individual capabilities.
- **Why yield successors**: The successor generation doesn't need to know which successors the search will actually explore, so it generates all valid transitions.
- **Why tuple return**: Returning (action, new_state, cost) tuples provides all the information the search needs while remaining generic.

## Dependencies
- **Imports**: None (pure Python)
- **Used by**: `search.py` (calls get_successors during A* exploration)
- **Uses**: `action.py` (calls is_possible and apply_effects)

## Implementation Structure

### Functions

```
def get_successors(                             (lines 12-55)
    current_state: dict, 
    concrete_actions: list[Action]) -> list[tuple[Action, dict, float]]
```

The module's sole public function. This is the interface between the abstract graph concept and the concrete GOAP mechanics. The function:

1. Takes the current world state and all available concrete actions
2. Iterates through every action (lines 15-50)
3. For each action:
   - Calls `action.is_possible(current_state)` to check validity
   - If valid, calls `action.apply_effects(current_state)` to compute the new state
   - Yields a tuple of (action_taken, resulting_state, action_cost)
4. Returns all valid state transitions

The function effectively answers: "What are all the places I can go from here, and how much does each step cost?"

## Key Design Decisions

1. **Dynamic Graph Generation**: Rather than pre-computing all states, the graph is explored dynamically. This is essential because the state space is potentially infinite.

2. **State Immutability**: The function relies on actions properly implementing `apply_effects` to return new states rather than modifying the current state. This prevents corruption during search.

3. **Action Validation**: Every action is checked with `is_possible` before generating a successor. This ensures the search only explores valid transitions.

4. **Cost Transparency**: Action costs are passed through directly, allowing for variable costs without the graph module needing to understand cost calculation.

5. **No Goal Knowledge**: The graph module knows nothing about goals. This clean separation allows the same graph structure to be used for any goal type.

## Performance Considerations

- This function is called many times during search (once per explored state)
- The efficiency of `is_possible` and `apply_effects` directly impacts planning performance
- Generating all successors (rather than yielding them lazily) is a deliberate choice for algorithm simplicity

## Relationship to C# Original

This file is a formalization of concepts from:
- `MountainGoap/Internals/ActionGraph.cs` - Graph structure
- Parts of `ActionAStar.cs` - Successor generation logic

The Python version creates a cleaner abstraction by:
- Separating graph structure from search algorithm completely
- Making the state transition rules explicit in one place
- Using Python's tuple returns for clean multi-value results

---

"""
def get_successors():
    pass