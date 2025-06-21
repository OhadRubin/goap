import sys
import os

# Add parent directory to path to import goap modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from goap.action import Action, ExecutionStatus


def test_execution_status():
    """Test ExecutionStatus enum functionality."""
    print("Testing ExecutionStatus enum...")

    # Test enum values
    assert ExecutionStatus.SUCCEEDED.value == "succeeded"
    assert ExecutionStatus.FAILED.value == "failed"
    assert ExecutionStatus.EXECUTING.value == "executing"

    # Test enum comparison
    status = ExecutionStatus.SUCCEEDED
    assert status == ExecutionStatus.SUCCEEDED
    assert status != ExecutionStatus.FAILED

    print("✓ ExecutionStatus enum works correctly")


def test_action_initialization():
    """Test Action class initialization with various parameters."""
    print("Testing Action initialization...")

    def test_executor():
        return ExecutionStatus.SUCCEEDED

    # Test basic initialization
    action1 = Action(
        name="basic_action",
        cost=2.5,
        preconditions={"key1": "value1"},
        effects={"key2": "value2"},
        executor=test_executor,
    )

    assert action1.name == "basic_action"
    assert action1.cost == 2.5
    assert action1.preconditions == {"key1": "value1"}
    assert action1.effects == {"key2": "value2"}
    assert action1.executor == test_executor
    assert action1.parameterizers == []

    # Test initialization with parameterizers
    test_parameterizers = [lambda x: ["param1", "param2"]]
    action2 = Action(
        name="param_action",
        cost=1.0,
        preconditions={},
        effects={},
        executor=test_executor,
        parameterizers=test_parameterizers,
    )

    assert action2.parameterizers == test_parameterizers

    # Test that preconditions and effects are copied (not referenced)
    original_preconditions = {"health": 100}
    original_effects = {"health": 50}

    action3 = Action(
        name="copy_test",
        cost=1.0,
        preconditions=original_preconditions,
        effects=original_effects,
        executor=test_executor,
    )

    # Modify original dictionaries
    original_preconditions["health"] = 200
    original_effects["health"] = 150

    # Action should have copies, not references
    assert action3.preconditions["health"] == 100
    assert action3.effects["health"] == 50

    print("✓ Action initialization works correctly")


def test_is_possible():
    """Test Action.is_possible() method with various precondition types."""
    print("Testing is_possible() method...")

    def dummy_executor():
        return ExecutionStatus.SUCCEEDED

    # Test simple key-value preconditions
    action = Action(
        name="simple_preconditions",
        cost=1.0,
        preconditions={"has_key": True, "location": "home"},
        effects={},
        executor=dummy_executor,
    )

    # Valid state
    valid_state = {"has_key": True, "location": "home", "extra": "data"}
    assert action.is_possible(
        valid_state
    ), "Should be possible with all preconditions met"

    # Missing key
    missing_key_state = {"location": "home"}
    assert not action.is_possible(
        missing_key_state
    ), "Should not be possible with missing key"

    # Wrong value
    wrong_value_state = {"has_key": False, "location": "home"}
    assert not action.is_possible(
        wrong_value_state
    ), "Should not be possible with wrong value"

    # Test comparative preconditions
    comp_action = Action(
        name="comparative_action",
        cost=1.0,
        preconditions={
            "health": "> 50",
            "score": "<= 100",
            "level": ">= 5",
            "energy": "< 90",
            "name": "== player1",
        },
        effects={},
        executor=dummy_executor,
    )

    # Valid comparative state
    valid_comp_state = {
        "health": 75,
        "score": 85,
        "level": 10,
        "energy": 60,
        "name": "player1",
    }
    assert comp_action.is_possible(
        valid_comp_state
    ), "Should be possible with all comparative conditions met"

    # Invalid health (too low)
    invalid_health_state = valid_comp_state.copy()
    invalid_health_state["health"] = 30
    assert not comp_action.is_possible(
        invalid_health_state
    ), "Should not be possible with low health"

    # Invalid score (too high)
    invalid_score_state = valid_comp_state.copy()
    invalid_score_state["score"] = 120
    assert not comp_action.is_possible(
        invalid_score_state
    ), "Should not be possible with high score"

    # Invalid level (too low)
    invalid_level_state = valid_comp_state.copy()
    invalid_level_state["level"] = 3
    assert not comp_action.is_possible(
        invalid_level_state
    ), "Should not be possible with low level"

    # Invalid energy (too high)
    invalid_energy_state = valid_comp_state.copy()
    invalid_energy_state["energy"] = 95
    assert not comp_action.is_possible(
        invalid_energy_state
    ), "Should not be possible with high energy"

    # Invalid name
    invalid_name_state = valid_comp_state.copy()
    invalid_name_state["name"] = "player2"
    assert not comp_action.is_possible(
        invalid_name_state
    ), "Should not be possible with wrong name"

    print("✓ is_possible() method works correctly")


def test_apply_effects():
    """Test Action.apply_effects() method with various effect types."""
    print("Testing apply_effects() method...")

    def dummy_executor():
        return ExecutionStatus.SUCCEEDED

    # Test simple value assignments
    simple_action = Action(
        name="simple_effects",
        cost=1.0,
        preconditions={},
        effects={"door_open": True, "location": "tavern", "inventory_count": 5},
        executor=dummy_executor,
    )

    initial_state = {"door_open": False, "location": "home", "health": 100}
    new_state = simple_action.apply_effects(initial_state)

    # Check that effects were applied
    assert new_state["door_open"] == True
    assert new_state["location"] == "tavern"
    assert new_state["inventory_count"] == 5

    # Check that original state is unchanged
    assert initial_state["door_open"] == False
    assert initial_state["location"] == "home"

    # Check that unaffected values remain
    assert new_state["health"] == 100

    # Test arithmetic effects
    arith_action = Action(
        name="arithmetic_effects",
        cost=1.0,
        preconditions={},
        effects={"health": "+25", "mana": "-10", "experience": "+100", "damage": "-5"},
        executor=dummy_executor,
    )

    arith_initial_state = {"health": 75, "mana": 50, "experience": 200, "damage": 20}

    arith_new_state = arith_action.apply_effects(arith_initial_state)

    # Check arithmetic operations
    assert arith_new_state["health"] == 100  # 75 + 25
    assert arith_new_state["mana"] == 40  # 50 - 10
    assert arith_new_state["experience"] == 300  # 200 + 100
    assert arith_new_state["damage"] == 15  # 20 - 5

    # Check original state unchanged
    assert arith_initial_state["health"] == 75

    # Test mixed effects
    mixed_action = Action(
        name="mixed_effects",
        cost=1.0,
        preconditions={},
        effects={"health": "+10", "has_key": True, "gold": "-50", "location": "shop"},
        executor=dummy_executor,
    )

    mixed_initial_state = {
        "health": 90,
        "has_key": False,
        "gold": 200,
        "location": "home",
    }
    mixed_new_state = mixed_action.apply_effects(mixed_initial_state)

    assert mixed_new_state["health"] == 100  # arithmetic
    assert mixed_new_state["has_key"] == True  # simple assignment
    assert mixed_new_state["gold"] == 150  # arithmetic
    assert mixed_new_state["location"] == "shop"  # simple assignment

    # Test arithmetic on non-existent keys
    missing_key_action = Action(
        name="missing_key_effects",
        cost=1.0,
        preconditions={},
        effects={"non_existent": "+10"},
        executor=dummy_executor,
    )

    empty_state = {}
    result_state = missing_key_action.apply_effects(empty_state)

    # Should treat as simple assignment when key doesn't exist
    assert result_state["non_existent"] == "+10"

    # Test invalid arithmetic (non-numeric values)
    invalid_arith_action = Action(
        name="invalid_arithmetic",
        cost=1.0,
        preconditions={},
        effects={"text_field": "+10"},
        executor=dummy_executor,
    )

    text_state = {"text_field": "hello"}
    invalid_result = invalid_arith_action.apply_effects(text_state)

    # Should fall back to simple assignment
    assert invalid_result["text_field"] == "+10"

    print("✓ apply_effects() method works correctly")


def test_state_immutability():
    """Test that apply_effects returns new state without modifying original."""
    print("Testing state immutability...")

    def dummy_executor():
        return ExecutionStatus.SUCCEEDED

    action = Action(
        name="immutability_test",
        cost=1.0,
        preconditions={},
        effects={"health": "+50", "location": "new_place", "items": 10},
        executor=dummy_executor,
    )

    original_state = {
        "health": 100,
        "location": "old_place",
        "items": 5,
        "other": "data",
    }
    new_state = action.apply_effects(original_state)

    # Original state should be unchanged
    assert original_state["health"] == 100
    assert original_state["location"] == "old_place"
    assert original_state["items"] == 5
    assert original_state["other"] == "data"

    # New state should have changes
    assert new_state["health"] == 150
    assert new_state["location"] == "new_place"
    assert new_state["items"] == 10
    assert new_state["other"] == "data"  # Unchanged values copied

    # States should be different objects
    assert original_state is not new_state

    print("✓ State immutability works correctly")


def test_comparison_edge_cases():
    """Test edge cases in comparison operations."""
    print("Testing comparison edge cases...")

    def dummy_executor():
        return ExecutionStatus.SUCCEEDED

    # Test invalid comparison strings
    invalid_comp_action = Action(
        name="invalid_comparisons",
        cost=1.0,
        preconditions={
            "invalid1": "invalid_operator 50",
            "invalid2": "> invalid_number",
            "invalid3": ">> 50",  # Double operator
            "malformed": "50 >",  # Backwards
        },
        effects={},
        executor=dummy_executor,
    )

    test_state = {"invalid1": 100, "invalid2": 100, "invalid3": 100, "malformed": 100}

    # All invalid comparisons should fail
    assert not invalid_comp_action.is_possible(
        test_state
    ), "Invalid comparisons should fail"

    # Test boundary conditions
    boundary_action = Action(
        name="boundary_test",
        cost=1.0,
        preconditions={
            "exact_match": ">= 100",
            "just_under": "> 99",
            "just_over": "< 101",
        },
        effects={},
        executor=dummy_executor,
    )

    boundary_state = {"exact_match": 100, "just_under": 100, "just_over": 100}
    assert boundary_action.is_possible(
        boundary_state
    ), "Boundary conditions should work"

    print("✓ Comparison edge cases handled correctly")


def test_error_handling():
    """Test error handling in various scenarios."""
    print("Testing error handling...")

    def dummy_executor():
        return ExecutionStatus.SUCCEEDED

    # Test action with no preconditions
    no_precond_action = Action(
        name="no_preconditions",
        cost=1.0,
        preconditions={},
        effects={"result": "success"},
        executor=dummy_executor,
    )

    assert no_precond_action.is_possible(
        {}
    ), "Action with no preconditions should always be possible"
    assert no_precond_action.is_possible(
        {"any": "state"}
    ), "Action with no preconditions should work with any state"

    # Test action with no effects
    no_effects_action = Action(
        name="no_effects",
        cost=1.0,
        preconditions={"ready": True},
        effects={},
        executor=dummy_executor,
    )

    initial_state = {"ready": True, "value": 10}
    result_state = no_effects_action.apply_effects(initial_state)

    # Should return unchanged copy
    assert result_state == initial_state
    assert result_state is not initial_state  # But still a copy

    print("✓ Error handling works correctly")


def test_integration_readiness():
    """Test that Action class is ready for integration with other components."""
    print("Testing integration readiness...")

    def test_executor():
        return ExecutionStatus.SUCCEEDED

    # Create action similar to what would be used in real GOAP system
    heal_action = Action(
        name="Heal",
        cost=2.0,
        preconditions={"health": "< 50", "has_potion": True},
        effects={"health": "+30", "has_potion": False},
        executor=test_executor,
        parameterizers=[lambda state: ["minor_potion", "major_potion"]],
    )

    # Test that it has all expected attributes for integration
    assert hasattr(heal_action, "name")
    assert hasattr(heal_action, "cost")
    assert hasattr(heal_action, "preconditions")
    assert hasattr(heal_action, "effects")
    assert hasattr(heal_action, "executor")
    assert hasattr(heal_action, "parameterizers")

    # Test that methods work as expected
    assert callable(heal_action.is_possible)
    assert callable(heal_action.apply_effects)
    assert callable(heal_action.executor)

    # Test realistic scenario
    injured_state = {"health": 25, "has_potion": True, "location": "dungeon"}

    assert heal_action.is_possible(
        injured_state
    ), "Heal should be possible when injured with potion"

    healed_state = heal_action.apply_effects(injured_state)
    assert healed_state["health"] == 55, "Health should increase by 30"
    assert healed_state["has_potion"] == False, "Potion should be consumed"
    assert healed_state["location"] == "dungeon", "Unaffected state should remain"

    # Test execution status return
    status = heal_action.executor()
    assert status == ExecutionStatus.SUCCEEDED

    print("✓ Integration readiness verified")


def test_action_comprehensive():
    """Run all comprehensive tests."""
    print("Running comprehensive Action tests...")

    test_execution_status()
    test_action_initialization()
    test_is_possible()
    test_apply_effects()
    test_state_immutability()
    test_comparison_edge_cases()
    test_error_handling()
    test_integration_readiness()

    print("✓ All comprehensive tests passed!")


def test_action_basic():
    """Test basic action functionality (original test)."""
    print("Running basic functionality test...")

    def dummy_executor():
        return ExecutionStatus.SUCCEEDED

    # Create a simple action
    action = Action(
        name="test_action",
        cost=1.0,
        preconditions={"has_key": True, "health": "> 30"},
        effects={"door_open": True, "health": "+10"},
        executor=dummy_executor,
    )

    # Test preconditions with valid state
    valid_state = {"has_key": True, "health": 50}
    assert action.is_possible(valid_state), "Action should be possible with valid state"

    # Test preconditions with invalid state
    invalid_state = {"has_key": False, "health": 50}
    assert not action.is_possible(
        invalid_state
    ), "Action should not be possible without key"

    # Test preconditions with low health
    low_health_state = {"has_key": True, "health": 20}
    assert not action.is_possible(
        low_health_state
    ), "Action should not be possible with low health"

    # Test effects application
    initial_state = {"has_key": True, "health": 40, "door_open": False}
    new_state = action.apply_effects(initial_state)
    assert new_state["door_open"] == True, "Door should be open after effect"
    assert new_state["health"] == 50, "Health should increase by 10"
    assert initial_state["health"] == 40, "Original state should be unchanged"

    print("✓ Basic functionality test passed!")


# if __name__ == "__main__":
#     print("=" * 50)
#     print("GOAP Action Implementation Tests")
#     print("=" * 50)

#     test_action_basic()
#     print()
#     test_action_comprehensive()

#     print("\n" + "=" * 50)
#     print("All Action tests completed successfully!")
#     print("=" * 50)
