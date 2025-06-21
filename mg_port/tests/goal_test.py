"""Tests for goal.py module using pytest conventions."""

from goap.goal import (
    ComparisonOperator,
    ComparisonValuePair,
    BaseGoal,
    Goal,
    ComparativeGoal,
    ExtremeGoal
)


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


def test_edge_cases():
    """Test edge cases and corner conditions."""
    print('Testing edge cases...')
    
    # Test empty desired states
    empty_goal = Goal('empty', 1.0, {})
    assert empty_goal.is_satisfied({}) == True
    assert empty_goal.is_satisfied({'any': 'data'}) == True
    print('✓ Empty desired states work')
    
    # Test None value handling
    none_goal = Goal('none_test', 1.0, {'key': None})
    assert none_goal.is_satisfied({'key': None}) == True
    assert none_goal.is_satisfied({'key': 'value'}) == False
    assert none_goal.is_satisfied({}) == False
    print('✓ None value handling works')
    
    # Test NOT_EQUALS operator (Python enhancement)
    not_eq_conditions = {
        'status': ComparisonValuePair(ComparisonOperator.NOT_EQUALS, 'dead')
    }
    not_eq_goal = ComparativeGoal('not_dead', 1.0, not_eq_conditions)
    assert not_eq_goal.is_satisfied({'status': 'alive'}) == True
    assert not_eq_goal.is_satisfied({'status': 'dead'}) == False
    print('✓ NOT_EQUALS operator works')
    
    # Test invalid comparison types
    invalid_conditions = {
        'mixed': ComparisonValuePair(ComparisonOperator.GREATER_THAN, 'string')
    }
    invalid_goal = ComparativeGoal('invalid', 1.0, invalid_conditions)
    assert invalid_goal.is_satisfied({'mixed': 42}) == False  # Type mismatch
    print('✓ Invalid comparison type handling works')
    
    # Test undefined operator
    undefined_conditions = {
        'test': ComparisonValuePair(ComparisonOperator.UNDEFINED, 10)
    }
    undefined_goal = ComparativeGoal('undefined', 1.0, undefined_conditions)
    assert undefined_goal.is_satisfied({'test': 10}) == False
    print('✓ Undefined operator handling works')
    
    # Test auto-generated names
    unnamed_goal = Goal()
    assert unnamed_goal.name.startswith('Goal ')
    assert len(unnamed_goal.name) > 5  # Should have UUID
    print('✓ Auto-generated names work')
    
    print('All edge case tests passed!')


def test_performance_characteristics():
    """Test performance characteristics for large states."""
    print('Testing performance characteristics...')
    import time
    
    # Create large desired state
    large_state = {f'key_{i}': i for i in range(1000)}
    large_goal = Goal('large', 1.0, large_state)
    
    # Test matching performance
    start_time = time.time()
    result = large_goal.is_satisfied(large_state)
    end_time = time.time()
    
    assert result == True
    assert end_time - start_time < 0.1  # Should be fast
    print('✓ Large state performance acceptable')
    
    # Test comparative goal performance
    large_conditions = {
        f'val_{i}': ComparisonValuePair(ComparisonOperator.GREATER_THAN, i)
        for i in range(100)
    }
    large_comp_goal = ComparativeGoal('large_comp', 1.0, large_conditions)
    large_comp_state = {f'val_{i}': i + 1 for i in range(100)}
    
    start_time = time.time()
    result = large_comp_goal.is_satisfied(large_comp_state)
    end_time = time.time()
    
    assert result == True
    assert end_time - start_time < 0.1  # Should be fast
    print('✓ Large comparative goal performance acceptable')
    
    print('All performance tests passed!')


# if __name__ == "__main__":
    
#     test_basic_functionality()
#     test_inheritance()
#     test_edge_cases()
#     test_performance_characteristics()