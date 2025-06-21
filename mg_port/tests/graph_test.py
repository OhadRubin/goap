
"""
Tests for the graph module's get_successors function.

This module tests the core graph functionality that generates valid state 
transitions from the current state by applying available actions.
"""

from goap.graph import get_successors


class MockAction:
    """Mock Action class for testing graph functionality."""
    
    def __init__(self, name: str, cost: float, preconditions: dict, effects: dict, is_possible_result: bool = True):
        """Initialize a mock action for testing.
        
        Args:
            name: Action identifier
            cost: Cost of executing this action
            preconditions: Dictionary of required world state conditions
            effects: Dictionary of state changes this action produces
            is_possible_result: Override for is_possible() return value
        """
        self.name = name
        self.cost = cost
        self.preconditions = preconditions.copy()
        self.effects = effects.copy()
        self._is_possible_result = is_possible_result
        self._call_count_is_possible = 0
        self._call_count_apply_effects = 0
    
    def is_possible(self, state: dict) -> bool:
        """Check if action can be executed. Mock implementation for testing."""
        self._call_count_is_possible += 1
        
        if not self._is_possible_result:
            return False
            
        # Check preconditions
        for key, value in self.preconditions.items():
            if key not in state or state[key] != value:
                return False
        return True
    
    def apply_effects(self, state: dict) -> dict:
        """Apply effects and return new state. Mock implementation for testing."""
        self._call_count_apply_effects += 1
        new_state = state.copy()
        new_state.update(self.effects)
        return new_state
    
    def get_cost(self, state: dict) -> float:
        """Dynamic cost method for testing."""
        return self.cost * 2  # Different from base cost for testing


class MockActionWithDynamicCost:
    """Mock action that only has get_cost method."""
    
    def __init__(self, name: str, dynamic_cost: float, preconditions: dict, effects: dict):
        self.name = name
        self.preconditions = preconditions
        self.effects = effects
        self._dynamic_cost = dynamic_cost
    
    def is_possible(self, state: dict) -> bool:
        return all(state.get(k) == v for k, v in self.preconditions.items())
    
    def apply_effects(self, state: dict) -> dict:
        new_state = state.copy()
        new_state.update(self.effects)
        return new_state
    
    def get_cost(self, state: dict) -> float:
        return self._dynamic_cost


class MockActionNoCost:
    """Mock action with no cost information."""
    
    def __init__(self, name: str, preconditions: dict, effects: dict):
        self.name = name
        self.preconditions = preconditions
        self.effects = effects
    
    def is_possible(self, state: dict) -> bool:
        return all(state.get(k) == v for k, v in self.preconditions.items())
    
    def apply_effects(self, state: dict) -> dict:
        new_state = state.copy()
        new_state.update(self.effects)
        return new_state


def test_basic_functionality():
    """Test basic get_successors functionality."""
    
    # Test with empty actions list
    current_state = {"health": 100, "has_key": False}
    empty_actions = []
    successors = get_successors(current_state, empty_actions)
    assert successors == [], "Empty actions should return empty successors"
    
    # Test with single valid action
    actions = [MockAction("open_door", 1.0, {"has_key": True}, {"door_open": True})]
    current_state = {"health": 100, "has_key": True}
    successors = get_successors(current_state, actions)
    assert len(successors) == 1, "Should have one successor"
    action, new_state, cost = successors[0]
    assert action.name == "open_door"
    assert new_state["door_open"] == True
    assert new_state["has_key"] == True  # Original state preserved
    assert cost == 2.0  # MockAction.get_cost returns cost * 2
    
    # Test with invalid action (preconditions not met)
    current_state = {"health": 100, "has_key": False}  # Missing key
    successors = get_successors(current_state, actions)
    assert successors == [], "Invalid action should return no successors"
    


def test_multiple_actions():
    """Test get_successors with multiple actions."""
    
    actions = [
        MockAction("heal", 2.0, {"health": 50}, {"health": 100}),
        MockAction("unlock", 1.0, {"has_key": True}, {"door_locked": False}),  
        MockAction("attack", 3.0, {"has_weapon": True}, {"enemy_dead": True})
    ]
    
    # State where only heal is possible
    current_state = {"health": 50, "has_key": False, "has_weapon": False}
    successors = get_successors(current_state, actions)
    assert len(successors) == 1
    assert successors[0][0].name == "heal"
    
    # State where heal and unlock are possible
    current_state = {"health": 50, "has_key": True, "has_weapon": False}
    successors = get_successors(current_state, actions)
    assert len(successors) == 2
    action_names = [s[0].name for s in successors]
    assert "heal" in action_names
    assert "unlock" in action_names
    
    # State where all actions are possible
    current_state = {"health": 50, "has_key": True, "has_weapon": True}
    successors = get_successors(current_state, actions)
    assert len(successors) == 3
    action_names = [s[0].name for s in successors]
    assert "heal" in action_names
    assert "unlock" in action_names
    assert "attack" in action_names
    


def test_state_immutability():
    """Test that original state is not modified."""
    
    actions = [MockAction("modify", 1.0, {"can_modify": True}, {"value": 999, "new_key": "added"})]
    current_state = {"can_modify": True, "value": 1, "existing_key": "original"}
    original_state = current_state.copy()
    
    successors = get_successors(current_state, actions)
    
    # Original state should be unchanged
    assert current_state == original_state, "Original state was modified"
    
    # New state should have changes
    new_state = successors[0][1]
    assert new_state["value"] == 999
    assert new_state["new_key"] == "added"
    assert new_state["existing_key"] == "original"  # Preserved
    assert new_state["can_modify"] == True  # Preserved
    


def test_cost_handling():
    """Test different cost calculation methods."""
    
    # Test static cost (cost attribute)
    static_action = MockAction("static", 5.0, {}, {"result": "static"})
    
    # Test dynamic cost (get_cost method)
    dynamic_action = MockActionWithDynamicCost("dynamic", 3.0, {}, {"result": "dynamic"})
    
    # Test no cost information
    no_cost_action = MockActionNoCost("no_cost", {}, {"result": "no_cost"})
    
    actions = [static_action, dynamic_action, no_cost_action]
    current_state = {}
    
    successors = get_successors(current_state, actions)
    assert len(successors) == 3
    
    # Find each successor by action name
    costs_by_name = {s[0].name: s[2] for s in successors}
    
    # Static cost should use get_cost method (cost * 2)
    assert costs_by_name["static"] == 10.0, f"Expected 10.0, got {costs_by_name['static']}"
    
    # Dynamic cost should use get_cost method
    assert costs_by_name["dynamic"] == 3.0, f"Expected 3.0, got {costs_by_name['dynamic']}"
    
    # No cost should default to 1.0
    assert costs_by_name["no_cost"] == 1.0, f"Expected 1.0, got {costs_by_name['no_cost']}"
    
    # Test precedence: get_cost should override cost attribute
    action_with_both = MockAction("both", 10.0, {}, {"result": "both"})
    # This action has both cost (10.0) and get_cost (returns 20.0)
    successors = get_successors(current_state, [action_with_both])
    assert successors[0][2] == 20.0, "get_cost should take precedence over cost attribute"
    


def test_action_interface_integration():
    """Test integration with action interface methods."""
    
    action = MockAction("test", 1.0, {"ready": True}, {"done": True})
    current_state = {"ready": True, "other": "value"}
    
    # Action should be called correctly
    successors = get_successors(current_state, [action])
    
    # Verify methods were called
    assert action._call_count_is_possible == 1, "is_possible should be called once"
    assert action._call_count_apply_effects == 1, "apply_effects should be called once"
    
    # Test action that fails is_possible
    failing_action = MockAction("fail", 1.0, {"ready": True}, {"done": True}, is_possible_result=False)
    successors = get_successors(current_state, [failing_action])
    
    assert len(successors) == 0, "Failing action should produce no successors"
    assert failing_action._call_count_is_possible == 1, "is_possible should still be called"
    assert failing_action._call_count_apply_effects == 0, "apply_effects should not be called"
    


def test_complex_state_transitions():
    """Test complex state transitions with multiple state variables."""
    
    actions = [
        MockAction("gather_wood", 2.0, {"location": "forest"}, {"wood": 10, "energy": -5}),
        MockAction("craft_axe", 3.0, {"wood": 10, "metal": 5}, {"has_axe": True, "wood": 0, "metal": 0}),
        MockAction("chop_tree", 1.0, {"has_axe": True}, {"wood": 20, "energy": -10})
    ]
    
    # Initial state - can only gather wood
    current_state = {"location": "forest", "wood": 0, "metal": 5, "energy": 100, "has_axe": False}
    successors = get_successors(current_state, actions)
    
    assert len(successors) == 1
    assert successors[0][0].name == "gather_wood"
    
    # After gathering wood - can craft axe
    new_state = successors[0][1]
    successors = get_successors(new_state, actions)
    
    # Should be able to gather more wood and craft axe
    action_names = [s[0].name for s in successors]
    assert "gather_wood" in action_names
    assert "craft_axe" in action_names
    assert len(successors) == 2
    
    # Find craft_axe successor
    craft_successor = next(s for s in successors if s[0].name == "craft_axe")
    after_craft_state = craft_successor[1]
    
    # After crafting axe - can chop trees
    successors = get_successors(after_craft_state, actions)
    action_names = [s[0].name for s in successors]
    assert "chop_tree" in action_names
    


def test_edge_cases():
    """Test edge cases and error conditions."""
    
    # Test with None state - this will actually work since we iterate over empty actions
    # The function is robust enough to handle None state with empty actions
    successors = get_successors(None, [])
    assert successors == [], "None state with empty actions should return empty list"
    
    # Test with None actions
    try:
        get_successors({}, None)
        assert False, "Should handle None actions gracefully"  
    except (TypeError, AttributeError):
        pass  # Expected to fail
    
    # Test with empty state
    actions = [MockAction("empty_test", 1.0, {}, {"created": True})]
    successors = get_successors({}, actions)
    assert len(successors) == 1
    assert successors[0][1]["created"] == True
    
    # Test with action that has empty effects
    actions = [MockAction("no_effect", 1.0, {}, {})]
    current_state = {"existing": "value"}
    successors = get_successors(current_state, actions)
    assert len(successors) == 1
    assert successors[0][1] == current_state  # State unchanged
    


def test_performance_characteristics():
    """Test basic performance characteristics."""
    
    # Create many actions to test scaling
    actions = []
    for i in range(100):
        actions.append(MockAction(f"action_{i}", 1.0, {"trigger": True}, {f"result_{i}": True}))
    
    current_state = {"trigger": True}
    successors = get_successors(current_state, actions)
    
    # All actions should be valid
    assert len(successors) == 100
    
    # Verify each action was processed correctly
    for i, (action, new_state, cost) in enumerate(successors):
        assert action.name == f"action_{i}"
        assert f"result_{i}" in new_state
        assert cost == 2.0  # MockAction.get_cost returns cost * 2
    


def test_comparison_with_csharp_behavior():
    """Test behavior compared to C# ActionGraph.Neighbors."""
    
    # Simulate C# ActionGraph.Neighbors behavior
    # C# version checks IsPossible and then ApplyEffects for each action
    
    actions = [
        MockAction("move_north", 1.0, {"position": "center"}, {"position": "north"}),
        MockAction("move_south", 1.0, {"position": "center"}, {"position": "south"}),
        MockAction("attack", 2.0, {"has_weapon": True, "enemy_present": True}, {"enemy_dead": True})
    ]
    
    # Test state where only movement is possible (like C# would handle)
    current_state = {"position": "center", "has_weapon": False, "enemy_present": True}
    successors = get_successors(current_state, actions)
    
    # Should get 2 movement actions, no attack
    assert len(successors) == 2
    action_names = [s[0].name for s in successors]
    assert "move_north" in action_names
    assert "move_south" in action_names
    assert "attack" not in action_names
    
    # Test state where all actions are possible
    current_state = {"position": "center", "has_weapon": True, "enemy_present": True}
    successors = get_successors(current_state, actions)
    
    # Should get all 3 actions
    assert len(successors) == 3
    action_names = [s[0].name for s in successors]
    assert "move_north" in action_names
    assert "move_south" in action_names  
    assert "attack" in action_names
    
    # Verify costs are preserved (C# behavior)
    costs_by_name = {s[0].name: s[2] for s in successors}
    assert costs_by_name["move_north"] == 2.0  # MockAction returns cost * 2
    assert costs_by_name["move_south"] == 2.0
    assert costs_by_name["attack"] == 4.0  # 2.0 * 2
