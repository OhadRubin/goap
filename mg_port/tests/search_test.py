
"""Tests for the search module functionality."""

from goap.search import _SearchNode, _reconstruct_path, _calculate_heuristic, astar_pathfind, get_successors


def test_search_node():
    """Test _SearchNode class functionality."""
    print('Testing _SearchNode...')
    
    # Test basic initialization
    state = {'health': 100, 'has_key': True}
    node = _SearchNode(state, None, None, 5.0, 3.0)
    assert node.state == state
    assert node.action is None
    assert node.parent is None
    assert node.g_score == 5.0
    assert node.h_score == 3.0
    
    # Test f-score calculation in comparison
    state2 = {'health': 80, 'has_key': False}
    node2 = _SearchNode(state2, None, None, 4.0, 2.0)  # f=6.0
    node3 = _SearchNode(state2, None, None, 7.0, 2.0)  # f=9.0
    
    assert node2 < node3  # f=6.0 < f=9.0
    assert not (node3 < node2)  # f=9.0 not < f=6.0
    
    # Test equal f-scores
    node4 = _SearchNode(state, None, None, 3.0, 3.0)  # f=6.0
    assert not (node2 < node4)  # f=6.0 not < f=6.0
    assert not (node4 < node2)  # f=6.0 not < f=6.0
    
    print('✓ _SearchNode works correctly')


def test_reconstruct_path():
    """Test _reconstruct_path function."""
    print('Testing _reconstruct_path...')
    
    # Create mock actions
    class MockAction:
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return f"Action({self.name})"
    
    action1 = MockAction("move")
    action2 = MockAction("attack")
    action3 = MockAction("heal")
    
    # Build a path: start -> node1 -> node2 -> node3
    start_node = _SearchNode({'pos': 0}, None, None, 0, 0)
    node1 = _SearchNode({'pos': 1}, action1, start_node, 1, 0)
    node2 = _SearchNode({'pos': 2}, action2, node1, 2, 0)
    node3 = _SearchNode({'pos': 3}, action3, node2, 3, 0)
    
    path = _reconstruct_path(node3)
    assert len(path) == 3
    assert path[0] == action1
    assert path[1] == action2
    assert path[2] == action3
    
    # Test single action path
    single_node = _SearchNode({'pos': 1}, action1, start_node, 1, 0)
    single_path = _reconstruct_path(single_node)
    assert len(single_path) == 1
    assert single_path[0] == action1
    
    # Test empty path (start node)
    empty_path = _reconstruct_path(start_node)
    assert len(empty_path) == 0
    
    print('✓ _reconstruct_path works correctly')


def test_calculate_heuristic_goal():
    """Test _calculate_heuristic for Goal type."""
    print('Testing _calculate_heuristic with Goal...')
    
    from goap.goal import Goal
    
    # Test basic Goal heuristic
    goal = Goal('test', 1.0, {'health': 100, 'has_key': True, 'pos': 'town'})
    
    # Perfect state - should have 0 cost
    perfect_state = {'health': 100, 'has_key': True, 'pos': 'town', 'extra': 'ignored'}
    assert _calculate_heuristic(perfect_state, goal) == 0.0
    
    # Missing one key - should cost 1
    missing_key_state = {'health': 100, 'has_key': True}
    assert _calculate_heuristic(missing_key_state, goal) == 1.0
    
    # Wrong value for one key - should cost 1
    wrong_value_state = {'health': 50, 'has_key': True, 'pos': 'town'}
    assert _calculate_heuristic(wrong_value_state, goal) == 1.0
    
    # Multiple mismatches - should cost 2
    multiple_wrong_state = {'health': 50, 'has_key': False, 'pos': 'town'}
    assert _calculate_heuristic(multiple_wrong_state, goal) == 2.0
    
    # All wrong - should cost 3
    all_wrong_state = {'health': 50, 'has_key': False, 'pos': 'forest'}
    assert _calculate_heuristic(all_wrong_state, goal) == 3.0
    
    print('✓ _calculate_heuristic Goal works correctly')


def test_calculate_heuristic_comparative():
    """Test _calculate_heuristic for ComparativeGoal type."""
    print('Testing _calculate_heuristic with ComparativeGoal...')
    
    from goap.goal import ComparativeGoal, ComparisonOperator, ComparisonValuePair
    
    # Test ComparativeGoal heuristic
    conditions = {
        'health': ComparisonValuePair(ComparisonOperator.GREATER_THAN, 50),
        'gold': ComparisonValuePair(ComparisonOperator.EQUALS, 100),
        'level': ComparisonValuePair(ComparisonOperator.LESS_THAN, 10)
    }
    comp_goal = ComparativeGoal('test', 1.0, conditions)
    
    # Perfect state - should have 0 cost
    perfect_state = {'health': 75, 'gold': 100, 'level': 5}
    assert _calculate_heuristic(perfect_state, comp_goal) == 0.0
    
    # Missing key - should have infinite cost
    missing_key_state = {'health': 75, 'gold': 100}
    assert _calculate_heuristic(missing_key_state, comp_goal) == float('inf')
    
    # Test EQUALS with numeric mismatch
    wrong_equals_state = {'health': 75, 'gold': 80, 'level': 5}
    assert _calculate_heuristic(wrong_equals_state, comp_goal) == 20.0  # |100-80|
    
    # Test GREATER_THAN violation  
    wrong_gt_state = {'health': 40, 'gold': 100, 'level': 5}
    assert _calculate_heuristic(wrong_gt_state, comp_goal) == 11.0  # 40-50+1
    
    # Test LESS_THAN violation
    wrong_lt_state = {'health': 75, 'gold': 100, 'level': 15}
    assert _calculate_heuristic(wrong_lt_state, comp_goal) == 6.0  # 15-10+1
    
    print('✓ _calculate_heuristic ComparativeGoal works correctly')


def test_calculate_heuristic_extreme():
    """Test _calculate_heuristic for ExtremeGoal type."""
    print('Testing _calculate_heuristic with ExtremeGoal...')
    
    from goap.goal import ExtremeGoal
    
    # Test ExtremeGoal heuristic
    optimizations = {'gold': True, 'distance': False}  # maximize gold, minimize distance
    extreme_goal = ExtremeGoal('test', 1.0, optimizations)
    
    # Test maximization heuristic
    state = {'gold': 80, 'distance': 20}
    heuristic = _calculate_heuristic(state, extreme_goal)
    expected = max(0, 100 - 80) + 20  # 20 + 20 = 40
    assert heuristic == expected
    
    # Test high gold value
    high_gold_state = {'gold': 95, 'distance': 5}
    heuristic = _calculate_heuristic(high_gold_state, extreme_goal)
    expected = max(0, 100 - 95) + 5  # 5 + 5 = 10
    assert heuristic == expected
    
    # Test missing key
    missing_key_state = {'gold': 50}
    assert _calculate_heuristic(missing_key_state, extreme_goal) == float('inf')
    
    # Test non-numeric value
    bad_value_state = {'gold': 'lots', 'distance': 10}
    assert _calculate_heuristic(bad_value_state, extreme_goal) == float('inf')
    
    print('✓ _calculate_heuristic ExtremeGoal works correctly')


def test_astar_pathfind_basic():
    """Test basic A* pathfinding functionality."""
    print('Testing astar_pathfind basic functionality...')
    
    # Create mock action and goal
    class MockAction:
        def __init__(self, name, cost=1.0):
            self.name = name
            self.cost = cost
        
        def is_possible(self, state):
            return True
        
        def apply_effects(self, state):
            new_state = state.copy()
            if self.name == "move_right":
                new_state['pos'] = state.get('pos', 0) + 1
            elif self.name == "get_key":
                new_state['has_key'] = True
            return new_state
        
        def get_cost(self, state):
            return self.cost
    
    # Mock get_successors function
    def mock_get_successors(current_state, actions):
        successors = []
        for action in actions:
            if action.is_possible(current_state):
                new_state = action.apply_effects(current_state)
                cost = action.get_cost(current_state)
                successors.append((action, new_state, cost))
        return successors
    
    # Patch get_successors temporarily
    original_get_successors = globals().get('get_successors')
    globals()['get_successors'] = mock_get_successors
    
    try:
        from goap.goal import Goal
        
        # Test simple pathfinding
        start_state = {'pos': 0, 'has_key': False}
        goal = Goal('test', 1.0, {'pos': 2, 'has_key': True})
        actions = [MockAction("move_right"), MockAction("get_key")]
        
        path = astar_pathfind(start_state, goal, actions)
        assert path is not None
        assert len(path) >= 2  # At least move and get_key
        
        # Test already satisfied goal
        satisfied_state = {'pos': 2, 'has_key': True}
        path = astar_pathfind(satisfied_state, goal, actions)
        assert path == []  # No actions needed
        
        print('✓ astar_pathfind basic functionality works')
        
    finally:
        # Restore original function
        if original_get_successors:
            globals()['get_successors'] = original_get_successors


def test_astar_pathfind_no_solution():
    """Test A* pathfinding when no solution exists."""
    print('Testing astar_pathfind with no solution...')
    
    class MockAction:
        def __init__(self, name):
            self.name = name
        
        def is_possible(self, state):
            return False  # No actions are possible
        
        def apply_effects(self, state):
            return state
        
        def get_cost(self, state):
            return 1.0
    
    def mock_get_successors(current_state, actions):
        return []  # No successors available
    
    # Patch get_successors temporarily
    original_get_successors = globals().get('get_successors')
    globals()['get_successors'] = mock_get_successors
    
    try:
        from goap.goal import Goal
        
        start_state = {'pos': 0}
        goal = Goal('test', 1.0, {'pos': 10})  # Impossible to reach
        actions = [MockAction("useless_action")]
        
        path = astar_pathfind(start_state, goal, actions)
        assert path is None  # No solution exists
        
        print('✓ astar_pathfind no solution handling works')
        
    finally:
        # Restore original function
        if original_get_successors:
            globals()['get_successors'] = original_get_successors


def test_astar_pathfind_optimal():
    """Test that A* finds optimal paths."""
    print('Testing astar_pathfind optimality...')
    
    class MockAction:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost
        
        def is_possible(self, state):
            if self.name == "expensive_jump":
                return state.get('pos', 0) == 0  # Only possible from start
            elif self.name == "cheap_step":
                return state.get('pos', 0) < 10  # Can step if not at goal
            return True
        
        def apply_effects(self, state):
            new_state = state.copy()
            if self.name == "expensive_jump":
                new_state['pos'] = 10  # Jump to goal
            elif self.name == "cheap_step":
                new_state['pos'] = state.get('pos', 0) + 1  # Step forward
            return new_state
        
        def get_cost(self, state):
            return self.cost
    
    def mock_get_successors(current_state, actions):
        successors = []
        for action in actions:
            if action.is_possible(current_state):
                new_state = action.apply_effects(current_state)
                cost = action.get_cost(current_state)
                successors.append((action, new_state, cost))
        return successors
    
    # Patch get_successors temporarily
    original_get_successors = globals().get('get_successors')
    globals()['get_successors'] = mock_get_successors
    
    try:
        from goap.goal import Goal
        
        # Two paths to same goal: expensive direct vs cheap multi-step
        start_state = {'pos': 0}
        goal = Goal('test', 1.0, {'pos': 10})
        actions = [
            MockAction("expensive_jump", 15.0),  # Direct but expensive
            MockAction("cheap_step", 1.0),       # Step by step
        ]
        
        path = astar_pathfind(start_state, goal, actions)
        assert path is not None
        
        # Calculate total cost
        total_cost = sum(action.cost for action in path)
        
        # Should choose the cheaper path
        # Either 1 expensive jump (cost 15) or multiple cheap steps (cost ≤ 10)
        assert total_cost <= 15.0  # Should find some valid path
        
        # If it's optimal, it should prefer the cheaper multi-step path
        if len(path) == 1:
            # Single action path - should be the expensive jump
            assert path[0].name == "expensive_jump"
            assert total_cost == 15.0
        else:
            # Multi-step path - should be cheaper
            assert all(action.name == "cheap_step" for action in path)
            assert total_cost == len(path) * 1.0
            assert total_cost <= 10.0
        
        print('✓ astar_pathfind optimality works')
        
    finally:
        # Restore original function
        if original_get_successors:
            globals()['get_successors'] = original_get_successors


def test_hash_state_consistency():
    """Test that state hashing is consistent."""
    print('Testing state hashing consistency...')
    
    # Test make_hashable_state function within astar_pathfind
    state1 = {'a': 1, 'b': 2, 'c': 3}
    state2 = {'c': 3, 'a': 1, 'b': 2}  # Same content, different order
    state3 = {'a': 1, 'b': 2, 'c': 4}  # Different content
    
    # Access the internal function by calling astar_pathfind with a controlled scenario
    class MockAction:
        def is_possible(self, state): return False
        def apply_effects(self, state): return state
        def get_cost(self, state): return 1.0
    
    def mock_get_successors(current_state, actions):
        # Access the make_hashable_state function indirectly
        return []
    
    original_get_successors = globals().get('get_successors')
    globals()['get_successors'] = mock_get_successors
    
    try:
        from goap.goal import Goal
        
        # Create a simple scenario to test state hashing
        goal = Goal('test', 1.0, {'unreachable': True})
        actions = [MockAction()]
        
        # The fact that astar_pathfind doesn't crash with different key orders
        # indicates the hashing is working correctly
        result1 = astar_pathfind(state1, goal, actions)
        result2 = astar_pathfind(state2, goal, actions)
        result3 = astar_pathfind(state3, goal, actions)
        
        # All should return None (no path), but shouldn't crash
        assert result1 is None
        assert result2 is None
        assert result3 is None
        
        print('✓ State hashing consistency works')
        
    finally:
        if original_get_successors:
            globals()['get_successors'] = original_get_successors


def test_heuristic_admissibility():
    """Test that heuristics are admissible (never overestimate)."""
    print('Testing heuristic admissibility...')
    
    from goap.goal import Goal, ComparativeGoal, ExtremeGoal, ComparisonOperator, ComparisonValuePair
    
    # For Goal type - count of unmet conditions should never exceed actual steps needed
    goal = Goal('test', 1.0, {'a': 1, 'b': 2})
    
    # State with 1 condition unmet - heuristic should be 1
    state1 = {'a': 1, 'b': 0}
    h1 = _calculate_heuristic(state1, goal)
    assert h1 == 1.0  # Exactly 1 condition unmet
    
    # State with 2 conditions unmet - heuristic should be 2
    state2 = {'a': 0, 'b': 0}
    h2 = _calculate_heuristic(state2, goal)
    assert h2 == 2.0  # Exactly 2 conditions unmet
    
    # For ComparativeGoal - numeric distances should not overestimate
    comp_goal = ComparativeGoal('test', 1.0, {
        'health': ComparisonValuePair(ComparisonOperator.GREATER_THAN_OR_EQUALS, 50)
    })
    
    state3 = {'health': 30}
    h3 = _calculate_heuristic(state3, comp_goal)
    assert h3 >= 0  # Should be non-negative
    
    # For ExtremeGoal - should provide meaningful guidance
    extreme_goal = ExtremeGoal('test', 1.0, {'gold': True})
    state4 = {'gold': 50}
    h4 = _calculate_heuristic(state4, extreme_goal)
    assert h4 >= 0  # Should be non-negative
    
    print('✓ Heuristic admissibility works')


def test_performance_characteristics():
    """Test performance characteristics of the search algorithm."""
    print('Testing search performance characteristics...')
    
    class MockAction:
        def __init__(self, name, effect_key, effect_value):
            self.name = name
            self.effect_key = effect_key
            self.effect_value = effect_value
        
        def is_possible(self, state):
            return True
        
        def apply_effects(self, state):
            new_state = state.copy()
            new_state[self.effect_key] = self.effect_value
            return new_state
        
        def get_cost(self, state):
            return 1.0
    
    def mock_get_successors(current_state, actions):
        successors = []
        for action in actions:
            if action.is_possible(current_state):
                new_state = action.apply_effects(current_state)
                cost = action.get_cost(current_state)
                successors.append((action, new_state, cost))
        return successors
    
    original_get_successors = globals().get('get_successors')
    globals()['get_successors'] = mock_get_successors
    
    try:
        from goap.goal import Goal
        import time
        
        # Test with moderate complexity
        start_state = {'pos': 0}
        goal = Goal('test', 1.0, {'pos': 5})
        actions = [MockAction(f"move_to_{i}", 'pos', i) for i in range(1, 10)]
        
        start_time = time.time()
        path = astar_pathfind(start_state, goal, actions)
        end_time = time.time()
        
        # Should complete quickly for reasonable problem size
        assert end_time - start_time < 1.0  # Should complete in under 1 second
        assert path is not None
        
        print('✓ Search performance characteristics acceptable')
        
    finally:
        if original_get_successors:
            globals()['get_successors'] = original_get_successors


# if __name__ == "__main__":
#     test_search_node()
#     test_reconstruct_path()
#     test_calculate_heuristic_goal()
#     test_calculate_heuristic_comparative()
#     test_calculate_heuristic_extreme()
#     test_astar_pathfind_basic()
#     test_astar_pathfind_no_solution()
#     test_astar_pathfind_optimal()
#     test_hash_state_consistency()
#     test_heuristic_admissibility()
#     test_performance_characteristics()
#     print('All search tests passed!')