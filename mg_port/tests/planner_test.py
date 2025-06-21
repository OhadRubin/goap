
"""Test suite for the GOAP planner module using pytest conventions."""

import pytest
from unittest.mock import patch
from goap.planner import _calculate_plan_utility, _find_plan_for_goal, orchestrate_planning
from goap.parameters import generate_action_variants
from goap.search import astar_pathfind


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_calculate_plan_utility():
    """Test the _calculate_plan_utility function with various cost/weight combinations."""
    
    # Mock goal with weight
    class MockGoal:
        def __init__(self, weight):
            self.weight = weight
    
    # Test normal cases
    goal = MockGoal(100.0)
    utility = _calculate_plan_utility(50.0, goal)
    assert utility == 2.0, f"Expected 2.0, got {utility}"
    
    # Test zero-cost plan (should return infinity)
    utility = _calculate_plan_utility(0.0, goal)
    assert utility == float('inf'), f"Expected inf, got {utility}"
    
    # Test negative cost (should return infinity)
    utility = _calculate_plan_utility(-10.0, goal)
    assert utility == float('inf'), f"Expected inf, got {utility}"
    
    # Test high-weight goal with expensive plan
    high_weight_goal = MockGoal(1000.0)
    utility = _calculate_plan_utility(100.0, high_weight_goal)
    assert utility == 10.0, f"Expected 10.0, got {utility}"
    
    # Test low-weight goal with cheap plan
    low_weight_goal = MockGoal(1.0)
    utility = _calculate_plan_utility(0.5, low_weight_goal)
    assert utility == 2.0, f"Expected 2.0, got {utility}"
    
    # Test fractional weights and costs
    fractional_goal = MockGoal(2.5)
    utility = _calculate_plan_utility(1.25, fractional_goal)
    assert utility == 2.0, f"Expected 2.0, got {utility}"


@patch('goap.planner.astar_pathfind')
def test_find_plan_for_goal(mock_astar):
    """Test the _find_plan_for_goal function with mock search results.""" 
    
    # Test successful delegation
    mock_astar.return_value = ['result_action1', 'result_action2']
    result = _find_plan_for_goal('test_goal', {'key': 'value'}, ['action1', 'action2'])
    
    assert result == ['result_action1', 'result_action2']
    mock_astar.assert_called_once_with({'key': 'value'}, 'test_goal', ['action1', 'action2'])
    
    # Reset mock
    mock_astar.reset_mock()
    
    # Test failed delegation
    mock_astar.return_value = None
    result = _find_plan_for_goal('impossible_goal', {'health': 0}, ['no_actions'])
    
    assert result is None
    mock_astar.assert_called_once_with({'health': 0}, 'impossible_goal', ['no_actions'])


@patch('goap.planner._find_plan_for_goal')
@patch('goap.planner.generate_action_variants')
def test_orchestrate_planning_basic(mock_generate, mock_find_plan):
    """Test basic orchestrate_planning functionality."""
    
    # Mock action with cost
    class MockAction:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
        
        def __repr__(self):
            return f"MockAction({self.name}, {self.cost})"
        
        def is_possible(self, state):
            return True
        
        def apply_effects(self, state):
            return state.copy()  # Return copy for testing
    
    # Mock goal with weight
    class MockGoal:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight
        
        def is_satisfied(self, state):
            return False  # For testing purposes
    
    # Mock agent
    class MockAgent:
        def __init__(self, actions, goals, state):
            self.actions = actions  # Action templates
            self.goals = goals
            self.state = state
    
    # Mock action template
    class MockActionTemplate:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
    
    # Set up mocks
    mock_generate.return_value = [MockAction("concrete_test_action", 5.0)]
    mock_find_plan.return_value = [MockAction("step1", 10.0), MockAction("step2", 20.0)]
    
    # Create test data
    template = MockActionTemplate("test_action", 5.0)
    goal = MockGoal("test_goal", 100.0)
    agent = MockAgent([template], [goal], {"health": 100})
    
    # Test planning
    result = orchestrate_planning(agent)
    assert result is not None
    assert len(result) == 2
    assert result[0].cost == 10.0
    assert result[1].cost == 20.0


@patch('goap.planner._find_plan_for_goal')
@patch('goap.planner.generate_action_variants')
def test_orchestrate_planning_multi_goal(mock_generate, mock_find_plan):
    """Test orchestrate_planning with multiple goals and utility optimization."""
    
    class MockAction:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
        
        def __repr__(self):
            return f"MockAction({self.name}, {self.cost})"
        
        def is_possible(self, state):
            return True
        
        def apply_effects(self, state):
            return state.copy()  # Return copy for testing
    
    class MockGoal:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight
        
        def is_satisfied(self, state):
            return False  # For testing purposes
    
    class MockAgent:
        def __init__(self, actions, goals, state):
            self.actions = actions
            self.goals = goals
            self.state = state
    
    class MockActionTemplate:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
    
    # Set up mocks
    mock_generate.return_value = [MockAction("concrete_test_action", 5.0)]
    
    # Return different plans for different goals
    def side_effect_find_plan(goal, state, actions):
        if goal.name == "high_weight_goal":
            return [MockAction("expensive_step", 100.0)]  # Utility = 1000/100 = 10
        elif goal.name == "low_weight_goal":
            return [MockAction("cheap_step", 1.0)]        # Utility = 10/1 = 10
        elif goal.name == "best_goal":
            return [MockAction("efficient_step", 5.0)]    # Utility = 100/5 = 20 (best!)
        return None
    
    mock_find_plan.side_effect = side_effect_find_plan
    
    # Create test data with multiple goals
    template = MockActionTemplate("test_action", 5.0)
    goals = [
        MockGoal("high_weight_goal", 1000.0),
        MockGoal("low_weight_goal", 10.0),
        MockGoal("best_goal", 100.0)  # This should win with highest utility
    ]
    agent = MockAgent([template], goals, {"health": 100})
    
    # Test planning
    result = orchestrate_planning(agent)
    assert result is not None
    assert len(result) == 1
    assert result[0].name == "efficient_step"  # Should select the plan with best utility


@patch('goap.planner._find_plan_for_goal')
@patch('goap.planner.generate_action_variants')
def test_orchestrate_planning_no_valid_plans(mock_generate, mock_find_plan):
    """Test orchestrate_planning when no valid plans exist."""
    
    class MockAction:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
    
    class MockGoal:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight
        
        def is_satisfied(self, state):
            return False  # For testing purposes
    
    class MockAgent:
        def __init__(self, actions, goals, state):
            self.actions = actions
            self.goals = goals
            self.state = state
    
    class MockActionTemplate:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
    
    # Set up mocks
    mock_generate.return_value = [MockAction("concrete_test_action", 5.0)]
    mock_find_plan.return_value = None  # Always return None (no plans found)
    
    # Create test data
    template = MockActionTemplate("test_action", 5.0)
    goal = MockGoal("impossible_goal", 100.0)
    agent = MockAgent([template], [goal], {"health": 100})
    
    # Test planning
    result = orchestrate_planning(agent)
    assert result is None


@patch('goap.planner._find_plan_for_goal')
@patch('goap.planner.generate_action_variants')
def test_orchestrate_planning_zero_cost_plan(mock_generate, mock_find_plan):
    """Test orchestrate_planning with zero-cost plans (infinite utility)."""
    
    class MockAction:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
        
        def __repr__(self):
            return f"MockAction({self.name}, {self.cost})"
        
        def is_possible(self, state):
            return True
        
        def apply_effects(self, state):
            return state.copy()  # Return copy for testing
    
    class MockGoal:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight
        
        def is_satisfied(self, state):
            return False  # For testing purposes
    
    class MockAgent:
        def __init__(self, actions, goals, state):
            self.actions = actions
            self.goals = goals
            self.state = state
    
    class MockActionTemplate:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
    
    # Set up mocks
    mock_generate.return_value = [MockAction("concrete_test_action", 5.0)]
    
    # Return different plans for different goals
    def side_effect_find_plan(goal, state, actions):
        if goal.name == "free_goal":
            return [MockAction("free_step", 0.0)]  # Zero cost = infinite utility
        elif goal.name == "expensive_goal":
            return [MockAction("expensive_step", 100.0)]  # Finite utility
        return None
    
    mock_find_plan.side_effect = side_effect_find_plan
    
    # Create test data with multiple goals
    template = MockActionTemplate("test_action", 5.0)
    goals = [
        MockGoal("expensive_goal", 1000.0),  # High weight but expensive
        MockGoal("free_goal", 1.0)          # Low weight but free (should win)
    ]
    agent = MockAgent([template], goals, {"health": 100})
    
    # Test planning
    result = orchestrate_planning(agent)
    assert result is not None
    assert len(result) == 1
    assert result[0].name == "free_step"  # Should select the zero-cost plan
    assert result[0].cost == 0.0


@patch('goap.planner._find_plan_for_goal')
@patch('goap.planner.generate_action_variants')
def test_orchestrate_planning_action_generation_integration(mock_generate, mock_find_plan):
    """Test orchestrate_planning integration with parameter generation."""
    
    class MockAction:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
        
        def __repr__(self):
            return f"MockAction({self.name}, {self.cost})"
        
        def is_possible(self, state):
            return True
        
        def apply_effects(self, state):
            return state.copy()  # Return copy for testing
    
    class MockGoal:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight
        
        def is_satisfied(self, state):
            return False  # For testing purposes
    
    class MockAgent:
        def __init__(self, actions, goals, state):
            self.actions = actions
            self.goals = goals
            self.state = state
    
    class MockActionTemplate:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
    
    # Set up mocks
    def side_effect_generate(template, state):
        return [MockAction(f"concrete_{template.name}", template.cost)]
    
    mock_generate.side_effect = side_effect_generate
    mock_find_plan.return_value = [MockAction("result_step", 10.0)]
    
    # Create test data with multiple action templates
    templates = [
        MockActionTemplate("attack", 5.0),
        MockActionTemplate("move", 2.0),
        MockActionTemplate("heal", 8.0)
    ]
    goal = MockGoal("test_goal", 100.0)
    agent = MockAgent(templates, [goal], {"location": "forest", "health": 50})
    
    # Test planning
    result = orchestrate_planning(agent)
    
    # Verify generate_action_variants was called for each template
    assert mock_generate.call_count == 3
    
    # Verify the calls were made with correct templates and state
    calls = mock_generate.call_args_list
    template_names = [call[0][0].name for call in calls]
    assert "attack" in template_names
    assert "move" in template_names
    assert "heal" in template_names
    
    # Verify state was passed correctly
    for call in calls:
        state = call[0][1]
        assert state["location"] == "forest"
        assert state["health"] == 50
    
    # Verify concrete actions were passed to find_plan
    assert mock_find_plan.call_count == 1
    find_plan_call = mock_find_plan.call_args_list[0]
    concrete_actions = find_plan_call[0][2]  # Third argument is the actions list
    assert len(concrete_actions) == 3
    action_names = [action.name for action in concrete_actions]
    assert "concrete_attack" in action_names
    assert "concrete_move" in action_names
    assert "concrete_heal" in action_names



# Note: When using pytest, you can run all tests with: pytest planner_tests.py
# Individual tests can be run with: pytest planner_tests.py::test_function_name

# if __name__ == "__main__":
#     # This allows the file to be run directly for manual testing
#     # In pytest, this block is ignored
#     pytest.main([__file__, "-v"])