"""# 📁 goap/planner.py

## Purpose
Contains the HIGH-LEVEL STRATEGIC PLANNER. This file orchestrates the overall planning process, deciding which goal is the most important to pursue and coordinating the search for plans. It sits between the parameterization and search steps, managing the multi-goal optimization problem.

## Conceptual Overview
The planner is responsible for the "big picture" of GOAP planning. While the search algorithm finds paths for individual goals, the planner:
- Evaluates all of the agent's goals
- Generates concrete actions from templates
- Requests plans for each viable goal
- Calculates the utility of each plan
- Selects the best plan based on goal weights and action costs

This creates a two-level optimization: the planner optimizes across goals while the search optimizes paths to individual goals. This separation allows for sophisticated goal selection strategies without complicating the path-finding algorithm.

## Design Rationale
- **Why not a class**: The planner is stateless - it's a pure function that transforms inputs to outputs. Making it a class would add unnecessary complexity.
- **Why separate from search**: Planning (which goal?) and searching (how to achieve it?) are distinct problems with different optimization criteria.
- **Why utility-based selection**: Using utility (weight/cost) allows natural trade-offs between important expensive goals and cheap less-important goals.
- **Why generate all actions first**: Generating the full action space once prevents redundant parameterization when checking multiple goals.

## Dependencies
- **Imports**: Functions from other modules
- **Used by**: `agent.py` (calls orchestrate_planning to get new plans)
- **Uses**: `parameters.py` (generate_action_variants), `search.py` (astar_pathfind), goal classes from `goal.py`

## Implementation Structure

### Helper Functions

```
def _calculate_plan_utility(                    (lines 15-22)
    plan_cost: float, 
    goal: BaseGoal) -> float
```

Private helper that calculates the utility of a plan. The typical implementation uses `goal.weight / plan_cost`, creating a natural trade-off between goal importance and plan expense. Higher weight goals can justify more expensive plans.

```
def _find_plan_for_goal(                        (lines 25-45)
    goal: BaseGoal, 
    start_state: dict, 
    concrete_actions: list[Action]) -> list[Action] | None
```

Private helper that delegates the actual pathfinding to the search module for a single goal. This separation:
- Keeps the main planning logic clean
- Allows for different search algorithms to be substituted
- Handles the None return case when no plan exists

### Main Functions

```
def orchestrate_planning(                       (lines 48-125)
    agent: Agent) -> list[Action] | None
```

The public-facing function of the module. This is the entry point called by agents when they need a new plan. The function follows a clear process:

1. **Action Generation Phase** (lines 55-65)
   - Iterates through the agent's abstract action templates
   - Calls `generate_action_variants` for each template
   - Builds a complete list of all possible concrete actions in the current state

2. **Goal Evaluation Phase** (lines 67-115)
   - Loops through each of the agent's goals
   - Calls `_find_plan_for_goal` to get a potential plan
   - If a plan exists, calculates its utility using `_calculate_plan_utility`
   - Tracks the best plan found so far

3. **Plan Selection Phase** (lines 117-125)
   - Returns the plan with the highest utility
   - Returns None if no valid plans were found for any goal

## Key Design Decisions

1. **Functional Design**: Using functions instead of classes makes the planner easier to test and reason about. State is passed through parameters rather than stored.

2. **Utility Function Abstraction**: The utility calculation is extracted to allow for different strategies (e.g., weight/cost, weight-cost, or more complex formulas).

3. **Best-First Selection**: The planner always returns the single best plan rather than a ranked list. This simplifies the agent's execution logic.

4. **Null-Safe Design**: The planner gracefully handles cases where no plans exist, returning None rather than raising exceptions.

5. **Separation of Concerns**: The planner knows about goals and utility but delegates pathfinding to the search module. This prevents the planning logic from becoming a "god function."

## Integration Notes

The planner acts as the critical bridge between:
- **Upward to Agent**: Provides the high-level planning service
- **Downward to Search**: Delegates the detailed pathfinding
- **Sideways to Parameters**: Uses the parameterization system

This positioning makes it a natural orchestration point without giving it too many responsibilities.

## Relationship to C# Original

This file corresponds primarily to:
- `MountainGoap/Internals/Planner.cs` - The main planning orchestration

The Python version improves clarity by:
- Separating goal evaluation from path search
- Making the utility calculation explicit
- Using functional design instead of complex class hierarchies

---

"""
from .parameters import generate_action_variants
from .search import astar_pathfind


def _calculate_plan_utility(plan_cost: float, goal) -> float:
    """
    Calculate the utility of a plan for a given goal.
    
    Args:
        plan_cost: Total cost of the plan
        goal: The goal being evaluated
        
    Returns:
        The utility score (higher is better)
        
    Note:
        Utility is calculated as goal.weight / plan_cost, creating a natural
        trade-off between goal importance and plan expense. Higher weight goals
        can justify more expensive plans.
    """
    if plan_cost <= 0:
        return float('inf')  # Free plans have infinite utility
    return goal.weight / plan_cost


def _find_plan_for_goal(goal, start_state: dict, concrete_actions: list):
    """
    Find a plan to achieve a specific goal using A* search.
    
    Args:
        goal: The goal to achieve
        start_state: Current world state 
        concrete_actions: List of all concrete actions available
        
    Returns:
        List of actions representing the plan, or None if no plan exists
        
    Note:
        This helper delegates the actual pathfinding to the search module,
        keeping the main planning logic clean and allowing for different
        search algorithms to be substituted.
    """
    return astar_pathfind(start_state, goal, concrete_actions)


def orchestrate_planning(agent):
    """
    The main planning function that finds the best plan for an agent.
    
    Args:
        agent: The agent that needs a plan
        
    Returns:
        List of actions representing the best plan, or None if no valid plans exist
        
    Note:
        This function follows a three-phase process:
        1. Action Generation: Create all possible concrete actions
        2. Goal Evaluation: Find plans for each goal and calculate utilities
        3. Plan Selection: Return the plan with highest utility
    """
    # Phase 1: Action Generation
    # Generate all possible concrete actions from the agent's action templates
    concrete_actions = []
    for action_template in agent.actions:
        action_variants = generate_action_variants(action_template, agent.state)
        concrete_actions.extend(action_variants)
    
    # Phase 2: Goal Evaluation  
    # Evaluate each goal and find the best plan
    best_plan = None
    best_utility = 0.0
    
    for goal in agent.goals:
        # Check if goal is already satisfied
        if goal.is_satisfied(agent.state):
            continue
            
        # Try to find a plan for this goal
        plan = _find_plan_for_goal(goal, agent.state, concrete_actions)
        
        if plan is not None:
            # Calculate the total cost of this plan
            plan_cost = sum(action.cost for action in plan)
            
            # Calculate the utility of this plan
            utility = _calculate_plan_utility(plan_cost, goal)
            
            # Track if this is the best plan so far
            if utility > best_utility:
                best_utility = utility
                best_plan = plan
    
    # Phase 3: Plan Selection
    # Return the plan with the highest utility (or None if no plans found)
    return best_plan