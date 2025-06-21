
# Import all necessary modules using absolute imports
from goap.agent import Agent, StepMode
from goap.action import Action, ExecutionStatus
from goap.goal import Goal
from goap.sensor import Sensor
from goap import planner
from unittest.mock import patch

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_basic_functionality():
    """Test basic StepMode enum and Agent initialization."""
    print('Testing StepMode enum...')
    
    # Test StepMode enum values
    assert StepMode.DEFAULT.value == "default"
    assert StepMode.ONE_ACTION.value == "one_action"
    assert len(list(StepMode)) == 2
    print('✓ StepMode enum works')
    
    print('Testing Agent initialization...')
    
    # Create mock components for testing
    
    def mock_executor(agent):
        return ExecutionStatus.SUCCEEDED
    
    def mock_sensor_run(state):
        state['sensor_ran'] = True
    
    # Create test components
    test_actions = [Action(name="test_action", cost=1.0, preconditions={}, effects={}, executor=mock_executor)]
    test_goals = [Goal(name="test_goal", desired_state={"goal_key": "goal_value"})]
    test_sensors = [Sensor(name="test_sensor", callback=mock_sensor_run)]
    initial_state = {"test_key": "test_value"}
    
    # Test agent initialization
    agent = Agent(
        name="test_agent",
        initial_state=initial_state,
        actions=test_actions,
        goals=test_goals,
        sensors=test_sensors
    )
    
    # Verify initialization
    assert agent.name == "test_agent"
    assert agent.state == initial_state
    assert agent.state is not initial_state  # Should be a copy
    assert len(agent.actions) == 1
    assert len(agent.goals) == 1
    assert len(agent.sensors) == 1
    assert agent.current_plan is None
    print('✓ Agent initialization works')
    
    print('All basic functionality tests passed!')


def test_step_method():
    """Test the step() method and sense-plan-act cycle."""
    print('Testing step() method behavior...')
    
    # Track what happens during execution
    execution_log = []
    
    def logging_sensor(state):
        execution_log.append("sensor_ran")
        state['sensor_updated'] = True
    
    def logging_action(agent):
        execution_log.append("action_executed")
        return ExecutionStatus.SUCCEEDED
    
    # Mock planner module
    class MockPlanner:
        @staticmethod
        def orchestrate_planning(agent):
            execution_log.append("planning_called")
            return [Action(name="planned_action", cost=1.0, preconditions={}, effects={}, executor=logging_action)]
    
    # Replace planner temporarily
    import sys
    from types import ModuleType
    
    mock_planner = ModuleType('planner')
    mock_planner.orchestrate_planning = MockPlanner.orchestrate_planning
    
    original_planner = sys.modules.get('goap.planner')
    sys.modules['goap.planner'] = mock_planner
    
    # Also replace the imported planner module in this module
    global planner
    original_local_planner = planner
    planner = mock_planner
    
    try:
        # Create agent
        agent = Agent(
            name="test_agent",
            initial_state={"test": "value"},
            actions=[Action(name="test_action", cost=1.0, preconditions={}, effects={}, executor=logging_action)],
            goals=[Goal(name="test_goal", desired_state={"goal": "achieved"})],
            sensors=[Sensor(name="logging_sensor", callback=logging_sensor)]
        )
        
        # Test step with no plan (should trigger planning)
        execution_log.clear()
        agent.step()
        
        # Verify sense-plan-act sequence
        expected_sequence = ["sensor_ran", "planning_called", "action_executed"]
        assert execution_log == expected_sequence
        assert agent.state.get('sensor_updated') == True
        print('✓ step() runs sensors, plans, and acts in sequence')
        
        # Test step with existing plan (should not trigger planning)
        execution_log.clear()
        agent.current_plan = [Action(name="existing_action", cost=1.0, preconditions={}, effects={}, executor=logging_action)]
        agent.step()
        
        # Should only run sensors and execute action
        expected_sequence = ["sensor_ran", "action_executed"]
        assert execution_log == expected_sequence
        print('✓ step() skips planning when plan exists')
        
        # Test ONE_ACTION mode
        execution_log.clear()
        agent.current_plan = None  # Force planning
        agent.step(StepMode.ONE_ACTION)
        
        # Should behave same as DEFAULT for planning
        expected_sequence = ["sensor_ran", "planning_called", "action_executed"]
        assert execution_log == expected_sequence
        print('✓ ONE_ACTION mode works correctly')
        
    finally:
        # Restore original planner
        if original_planner:
            sys.modules['goap.planner'] = original_planner
        else:
            sys.modules.pop('goap.planner', None)
        
        # Restore local planner import
        planner = original_local_planner
    
    print('All step method tests passed!')


def test_execution_states():
    """Test ExecutionStatus handling in action execution."""
    print('Testing ExecutionStatus handling...')
    
    def dummy_sensor(state):
        pass
    
    # Test SUCCEEDED status
    def succeeding_action(agent):
        return ExecutionStatus.SUCCEEDED
    
    agent = Agent(
        name="test_agent",
        initial_state={},
        actions=[Action(name="test", cost=1.0, preconditions={}, effects={}, executor=succeeding_action)],
        goals=[Goal(name="test_goal", desired_state={})],
        sensors=[Sensor(name="dummy_sensor", callback=dummy_sensor)]
    )
    
    # Set up plan with 2 actions
    agent.current_plan = [
        Action(name="action1", cost=1.0, preconditions={}, effects={}, executor=succeeding_action),
        Action(name="action2", cost=1.0, preconditions={}, effects={}, executor=succeeding_action)
    ]
    
    # Execute first action (should be removed)
    original_plan_length = len(agent.current_plan)
    agent._execute_current_action()
    assert len(agent.current_plan) == original_plan_length - 1
    print('✓ SUCCEEDED actions are removed from plan')
    
    # Test FAILED status
    def failing_action(agent):
        return ExecutionStatus.FAILED
    
    agent.current_plan = [Action(name="failing", cost=1.0, preconditions={}, effects={}, executor=failing_action)]
    agent._execute_current_action()
    assert agent.current_plan is None
    print('✓ FAILED actions clear entire plan')
    
    # Test EXECUTING status
    def continuing_action(agent):
        return ExecutionStatus.EXECUTING
    
    agent.current_plan = [Action(name="continuing", cost=1.0, preconditions={}, effects={}, executor=continuing_action)]
    original_plan_length = len(agent.current_plan)
    agent._execute_current_action()
    assert len(agent.current_plan) == original_plan_length  # Should remain same
    print('✓ EXECUTING actions remain in plan')
    
    # Test unknown status (should be treated as failure)
    def unknown_status_action(agent):
        return "unknown_status"
    
    agent.current_plan = [Action(name="unknown", cost=1.0, preconditions={}, effects={}, executor=unknown_status_action)]
    agent._execute_current_action()
    assert agent.current_plan is None
    print('✓ Unknown status treated as failure')
    
    print('All execution status tests passed!')


def test_edge_cases():
    """Test edge cases and error conditions."""
    print('Testing edge cases...')
    
    def dummy_executor(agent):
        return ExecutionStatus.SUCCEEDED
    
    def dummy_sensor(state):
        pass
    
    # Test agent with empty component lists
    agent = Agent(
        name="empty_agent",
        initial_state={"key": "value"},
        actions=[],
        goals=[],
        sensors=[]
    )
    
    # Should not crash when stepping with no components
    agent.step()
    assert agent.state == {"key": "value"}
    print('✓ Agent handles empty component lists')
    
    # Test execution with no plan
    agent.current_plan = None
    agent._execute_current_action()  # Should not crash
    
    agent.current_plan = []
    agent._execute_current_action()  # Should not crash
    print('✓ Agent handles empty/None plans')
    
    # Test sensor state updates
    def state_updating_sensor(state):
        state['updated'] = True
        state['counter'] = state.get('counter', 0) + 1
    
    agent = Agent(
        name="sensor_test",
        initial_state={"counter": 0},
        actions=[Action(name="test", cost=1.0, preconditions={}, effects={}, executor=dummy_executor)],
        goals=[Goal(name="test", desired_state={})],
        sensors=[Sensor(name="state_updating_sensor", callback=state_updating_sensor)]
    )
    
    agent._run_sensors()
    assert agent.state['updated'] == True
    assert agent.state['counter'] == 1
    
    agent._run_sensors()
    assert agent.state['counter'] == 2
    print('✓ Sensors properly update agent state')
    
    # Test defensive copying
    original_actions = [Action(name="original", cost=1.0, preconditions={}, effects={}, executor=dummy_executor)]
    original_goals = [Goal(name="original", desired_state={})]
    original_sensors = [Sensor(name="original_sensor", callback=dummy_sensor)]
    original_state = {"original": "value"}
    
    agent = Agent(
        name="copy_test",
        initial_state=original_state,
        actions=original_actions,
        goals=original_goals,
        sensors=original_sensors
    )
    
    # Modify original lists - agent should be unaffected
    original_actions.clear()
    original_goals.clear()
    original_sensors.clear()
    original_state["modified"] = True
    
    assert len(agent.actions) == 1
    assert len(agent.goals) == 1
    assert len(agent.sensors) == 1
    assert "modified" not in agent.state
    print('✓ Agent creates defensive copies of inputs')
    
    print('All edge case tests passed!')


def test_planning_integration():
    """Test integration with planner module."""
    print('Testing planner integration...')
    
    # Track planner calls
    planner_calls = []
    
    def mock_orchestrate_planning(agent):
        planner_calls.append({
            'agent_name': agent.name,
            'state_keys': list(agent.state.keys()),
            'num_actions': len(agent.actions),
            'num_goals': len(agent.goals)
        })
        return [Action(name="planned", cost=1.0, preconditions={}, effects={}, executor=lambda a: ExecutionStatus.SUCCEEDED)]
    
    # Mock planner temporarily
    import sys
    from types import ModuleType
    
    mock_planner = ModuleType('planner')
    mock_planner.orchestrate_planning = mock_orchestrate_planning
    
    original_planner = sys.modules.get('goap.planner')
    sys.modules['goap.planner'] = mock_planner
    
    # Also replace the imported planner module in this module
    global planner
    original_local_planner = planner
    planner = mock_planner
    
    try:
        agent = Agent(
            name="planner_test",
            initial_state={"test": "state"},
            actions=[Action(name="available", cost=1.0, preconditions={}, effects={}, executor=lambda a: ExecutionStatus.SUCCEEDED)],
            goals=[Goal(name="target", desired_state={"achieved": True})],
            sensors=[Sensor(name="null_sensor", callback=lambda s: None)]
        )
        
        # Test planning call
        planner_calls.clear()
        agent._find_new_plan()
        
        assert len(planner_calls) == 1
        call = planner_calls[0]
        assert call['agent_name'] == "planner_test"
        assert 'test' in call['state_keys']
        assert call['num_actions'] == 1
        assert call['num_goals'] == 1
        assert agent.current_plan is not None
        assert len(agent.current_plan) == 1
        print('✓ Planner integration works correctly')
        
    finally:
        # Restore original planner
        if original_planner:
            sys.modules['goap.planner'] = original_planner
        else:
            sys.modules.pop('goap.planner', None)
        
        # Restore local planner import
        planner = original_local_planner
    
    print('All planner integration tests passed!')


if __name__ == "__main__":
    test_basic_functionality()
    test_step_method()
    test_execution_states()
    test_edge_cases()
    test_planning_integration()