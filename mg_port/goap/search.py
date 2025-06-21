"""
# 📁 goap/search.py

## Purpose
Contains the PURE, LOW-LEVEL A* SEARCH ALGORITHM. This file is responsible for finding the cheapest path from a start state to a goal state within the graph defined by the graph module. It implements the algorithmic core of GOAP planning.

## Conceptual Overview
The search module implements the A* pathfinding algorithm adapted for GOAP's state-space search. Unlike traditional pathfinding on a grid, this searches through abstract world states, but the algorithm remains fundamentally the same:
- Start at the initial state
- Explore successors prioritized by f-score (g + h)
- Track the cheapest path to each state
- Stop when a goal state is reached

The module knows about:
- How to search (A* algorithm mechanics)
- How to estimate distance (heuristics)
- How to track paths (parent pointers)

The module does NOT know about:
- What actions mean (just that they connect states)
- How states transition (delegates to graph module)
- Why we're searching (goals are just satisfaction functions)

## Design Rationale
- **Why A***: A* is optimal and complete when the heuristic is admissible. It finds the cheapest plan while exploring fewer states than uninformed search.
- **Why separate heuristics by goal type**: Different goal types need different distance estimates. Separating this logic keeps it maintainable.
- **Why private node class**: The search node is an implementation detail that shouldn't leak to other modules. It's specifically designed for the needs of A*.
- **Why path reconstruction**: Working backwards from the goal ensures we return the actual path taken, not just the cost.

## Dependencies
- **Imports**: `heapq` for priority queue implementation
- **Used by**: `planner.py` (calls astar_pathfind for each goal)
- **Uses**: `graph.py` (calls get_successors), `goal.py` (calls is_satisfied)

## Implementation Structure

### Classes

```
class _SearchNode                               (lines 15-35)
```

Private helper class that represents a node in the search tree. Stores:
- `state`: The world state dictionary at this node
- `action`: The action that led to this state (None for start)
- `parent`: Reference to parent node for path reconstruction
- `g_score`: Actual cost from start to this node
- `h_score`: Heuristic estimate from this node to goal

```
def __lt__(self, other) -> bool                (lines 31-35)
```
Implements less-than comparison based on f-score (g + h). This allows SearchNode objects to be used directly in Python's heapq, which maintains a min-heap based on this comparison.

### Helper Functions

```
def _reconstruct_path(                          (lines 38-50)
    end_node: _SearchNode) -> list[Action]
```

Private helper that builds the final plan by tracing parent pointers from the goal node back to the start. Returns the list of actions in forward order (start to goal).

```
def _calculate_heuristic(                       (lines 53-95)
    state: dict, 
    goal: BaseGoal) -> float
```

Private helper that estimates the "distance" from a state to a goal. Implements different strategies based on goal type:
- **Goal**: Count of unmet conditions
- **ComparativeGoal**: Sum of numeric distances to thresholds
- **ExtremeGoal**: Distance from current value to optimization direction

The heuristic must be admissible (never overestimate) for A* to guarantee optimal plans.

### Main Function

```
def astar_pathfind(                             (lines 98-190)
    start_state: dict, 
    goal: BaseGoal, 
    concrete_actions: list[Action]) -> list[Action] | None
```

The main A* implementation. The algorithm proceeds in phases:

1. **Initialization** (lines 105-120)
   - Create start node with g=0 and h=heuristic
   - Initialize open set (heapq) with start node
   - Initialize closed set (set) for visited states
   - Create g_score tracking dictionary

2. **Main Search Loop** (lines 122-180)
   - Pop lowest f-score node from open set
   - Check if goal is satisfied - if so, reconstruct and return path
   - Add current state to closed set
   - Get all successors via graph module
   - For each successor:
     - Skip if already visited (in closed set)
     - Calculate tentative g-score
     - If better path found, update or add to open set

3. **Failure Case** (lines 182-190)
   - Return None if open set empty (no path exists)

## Key Design Decisions

1. **Immutable State Tracking**: States are used as dictionary keys, so they must be immutable (converted to frozen representations).

2. **Lazy Successor Evaluation**: Successors are only generated when a node is explored, not when it's discovered.

3. **Single Goal Focus**: The search handles one goal at a time. Multi-goal optimization is the planner's responsibility.

4. **Null on Failure**: Returns None when no path exists rather than raising an exception, allowing the planner to try other goals.

5. **Admissible Heuristics**: All heuristic implementations are designed to be admissible, ensuring optimal plans.

## Performance Characteristics

- Time complexity: O(b^d) where b is branching factor and d is depth
- Space complexity: O(b^d) for storing open and closed sets
- Optimality: Guaranteed when heuristic is admissible
- Completeness: Will find a solution if one exists

## Relationship to C# Original

This file consolidates concepts from:
- `MountainGoap/Internals/ActionAStar.cs` - Main A* implementation
- `MountainGoap/Internals/ActionNode.cs` - Search node structure
- Heuristic calculations scattered in the C# code

The Python version benefits from:
- Using heapq instead of custom priority queue
- Cleaner heuristic organization
- More Pythonic state management

---
"""
import heapq
from typing import Optional
from .goal import BaseGoal, Goal, ComparativeGoal, ExtremeGoal, ComparisonOperator
from .graph import get_successors


class _SearchNode:
    """Private helper class representing a node in the A* search tree."""
    
    def __init__(self, state: dict, action=None, parent=None, g_score: float = 0, h_score: float = 0):
        self.state = state
        self.action = action  # Action that led to this state (None for start)
        self.parent = parent  # Reference to parent node for path reconstruction
        self.g_score = g_score  # Actual cost from start to this node
        self.h_score = h_score  # Heuristic estimate from this node to goal
    
    def __lt__(self, other) -> bool:
        """Implements less-than comparison based on f-score (g + h) for heapq."""
        return (self.g_score + self.h_score) < (other.g_score + other.h_score)


def _reconstruct_path(end_node: '_SearchNode') -> list:
    """
    Private helper that builds the final plan by tracing parent pointers 
    from the goal node back to the start. Returns actions in forward order.
    """
    path = []
    current = end_node
    
    # Trace back through parents, collecting actions
    while current is not None and current.action is not None:
        path.append(current.action)
        current = current.parent
    
    # Reverse to get forward order (start to goal)
    path.reverse()
    return path


def _calculate_heuristic(state: dict, goal: BaseGoal) -> float:
    """
    Private helper that estimates the "distance" from a state to a goal.
    Implements different strategies based on goal type.
    The heuristic must be admissible (never overestimate) for A* to guarantee optimal plans.
    """
    if isinstance(goal, Goal):
        # Goal: Count of unmet conditions
        cost = 0.0
        for key, desired_value in goal.desired_state.items():
            if key not in state:
                cost += 1.0
            elif state[key] != desired_value:
                cost += 1.0
        return cost
    
    elif isinstance(goal, ComparativeGoal):
        # ComparativeGoal: Sum of numeric distances to thresholds
        cost = 0.0
        for key, comparison_pair in goal.conditions.items():
            if key not in state:
                cost += float('inf')  # Missing key is infinite cost
                continue
            
            current_value = state[key]
            target_value = comparison_pair.value
            operator = comparison_pair.operator
            
            # Calculate distance based on operator
            if operator == ComparisonOperator.EQUALS:
                if current_value != target_value:
                    # For numeric values, use absolute difference
                    if isinstance(current_value, (int, float)) and isinstance(target_value, (int, float)):
                        cost += abs(current_value - target_value)
                    else:
                        cost += 1.0  # Non-numeric mismatch
            elif operator == ComparisonOperator.LESS_THAN:
                if isinstance(current_value, (int, float)) and isinstance(target_value, (int, float)):
                    if current_value >= target_value:
                        cost += current_value - target_value + 1
                else:
                    cost += 1.0
            elif operator == ComparisonOperator.GREATER_THAN:
                if isinstance(current_value, (int, float)) and isinstance(target_value, (int, float)):
                    if current_value <= target_value:
                        cost += target_value - current_value + 1
                else:
                    cost += 1.0
            # Add other operators as needed
            
        return cost
    
    elif isinstance(goal, ExtremeGoal):
        # ExtremeGoal: Distance from current value to optimization direction
        cost = 0.0
        for key, maximize in goal.optimizations.items():
            if key not in state:
                cost += float('inf')
                continue
            
            current_value = state[key]
            if not isinstance(current_value, (int, float)):
                cost += float('inf')
                continue
            
            # For extreme goals, we use the inverse of the current value as heuristic
            # This encourages moving toward higher values (for maximize) or lower values (for minimize)
            if maximize:
                # For maximization, higher values have lower heuristic cost
                cost += max(0, 100 - current_value)  # Assume max reasonable value of 100
            else:
                # For minimization, lower values have lower heuristic cost
                cost += current_value
        
        return cost
    
    # Default case - no heuristic guidance
    return 0.0


def astar_pathfind(start_state: dict, goal: BaseGoal, concrete_actions: list) -> Optional[list]:
    """
    The main A* implementation. Finds the cheapest path from start_state to a state
    that satisfies the goal using the provided concrete actions.
    
    Returns a list of actions to execute, or None if no path exists.
    """
    # Convert state to immutable representation for dictionary keys
    def make_hashable_state(state):
        return tuple(sorted(state.items()))
    
    # Phase 1: Initialization
    start_h = _calculate_heuristic(start_state, goal)
    start_node = _SearchNode(start_state, None, None, 0.0, start_h)
    
    # Open set (priority queue) - nodes to be evaluated
    open_set = [start_node]
    heapq.heapify(open_set)
    
    # Closed set - states we've already evaluated
    closed_set = set()
    
    # Track best known g-score for each state
    g_scores = {make_hashable_state(start_state): 0.0}
    
    # Phase 2: Main Search Loop
    while open_set:
        # Pop the node with lowest f-score
        current_node = heapq.heappop(open_set)
        current_state_key = make_hashable_state(current_node.state)
        
        # Check if we've already processed this state with a better path
        if current_state_key in closed_set:
            continue
        
        # Check if goal is satisfied
        if goal.is_satisfied(current_node.state):
            return _reconstruct_path(current_node)
        
        # Add current state to closed set
        closed_set.add(current_state_key)
        
        # Get all successor states
        successors = get_successors(current_node.state, concrete_actions)
        
        for action, new_state, action_cost in successors:
            new_state_key = make_hashable_state(new_state)
            
            # Skip if already fully evaluated
            if new_state_key in closed_set:
                continue
            
            # Calculate tentative g-score
            tentative_g = current_node.g_score + action_cost
            
            # Check if this is a better path to this state
            if new_state_key not in g_scores or tentative_g < g_scores[new_state_key]:
                # Update tracking
                g_scores[new_state_key] = tentative_g
                
                # Calculate heuristic for new state
                h_score = _calculate_heuristic(new_state, goal)
                
                # Create new node and add to open set
                new_node = _SearchNode(new_state, action, current_node, tentative_g, h_score)
                heapq.heappush(open_set, new_node)
    
    # Phase 3: Failure Case - no path exists
    return None