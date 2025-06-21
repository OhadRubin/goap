from goap.sensor import Sensor


def test_basic_functionality():
    """Test basic functionality of Sensor class."""
    print("Testing Sensor initialization...")

    # Test basic initialization
    def test_callback(state):
        state["test_value"] = 42

    sensor = Sensor("test_sensor", test_callback)
    assert sensor.name == "test_sensor"
    assert sensor.callback == test_callback
    print("✓ Basic initialization works")

    # Test sensor run with state modification
    print("Testing sensor run...")
    state = {"initial": True}
    sensor.run(state)
    assert state["test_value"] == 42
    assert state["initial"] == True
    print("✓ Sensor run with state modification works")

    # Test with lambda callback
    print("Testing lambda callback...")
    lambda_sensor = Sensor(
        "lambda_test", lambda s: s.update({"lambda_key": "lambda_value"})
    )
    state = {}
    lambda_sensor.run(state)
    assert state["lambda_key"] == "lambda_value"
    print("✓ Lambda callback works")

    print("All basic functionality tests passed!")


def test_callback_variations():
    """Test different types of callback functions."""

    # Test callback that reads and modifies state
    print("Testing read-modify callback...")

    def health_monitor(state):
        current_health = state.get("health", 100)
        if current_health < 30:
            state["health_critical"] = True
        else:
            state["health_critical"] = False
        state["health_checked"] = True

    sensor = Sensor("health_monitor", health_monitor)

    # Test with high health
    state = {"health": 80}
    sensor.run(state)
    assert state["health_critical"] == False
    assert state["health_checked"] == True

    # Test with low health
    state = {"health": 20}
    sensor.run(state)
    assert state["health_critical"] == True
    assert state["health_checked"] == True
    print("✓ Read-modify callback works")

    # Test callback that only reads (monitoring)
    print("Testing read-only callback...")
    readings = []

    def temperature_logger(state):
        temp = state.get("temperature", 0)
        readings.append(temp)

    temp_sensor = Sensor("temp_logger", temperature_logger)
    state = {"temperature": 25}
    temp_sensor.run(state)
    assert len(readings) == 1
    assert readings[0] == 25
    print("✓ Read-only callback works")

    # Test callback with complex data structures
    print("Testing complex data callback...")

    def enemy_detector(state):
        enemies = state.get("enemies", [])
        state["enemy_count"] = len(enemies)
        state["enemies_nearby"] = len(enemies) > 0
        if enemies:
            state["closest_enemy"] = min(
                enemies, key=lambda e: e.get("distance", float("inf"))
            )

    enemy_sensor = Sensor("enemy_detector", enemy_detector)
    state = {
        "enemies": [
            {"name": "goblin", "distance": 10},
            {"name": "orc", "distance": 5},
            {"name": "troll", "distance": 15},
        ]
    }
    enemy_sensor.run(state)
    assert state["enemy_count"] == 3
    assert state["enemies_nearby"] == True
    assert state["closest_enemy"]["name"] == "orc"
    print("✓ Complex data callback works")

    print("All callback variation tests passed!")


def test_multiple_sensors():
    """Test coordination between multiple sensors."""
    print("Testing multiple sensor coordination...")

    def vision_sensor(state):
        # Simulate vision detection
        state["vision_range"] = 10
        state["objects_seen"] = ["tree", "rock", "enemy"]

    def audio_sensor(state):
        # Simulate audio detection
        state["audio_range"] = 15
        state["sounds_heard"] = ["footsteps", "wind"]

    def integration_sensor(state):
        # Integrate multiple sensor inputs
        objects = state.get("objects_seen", [])
        sounds = state.get("sounds_heard", [])

        # Cross-reference audio and visual
        if "enemy" in objects and "footsteps" in sounds:
            state["confirmed_enemy"] = True
        else:
            state["confirmed_enemy"] = False

    vision = Sensor("vision", vision_sensor)
    audio = Sensor("audio", audio_sensor)
    integration = Sensor("integration", integration_sensor)

    # Simulate sensor processing order
    state = {}
    vision.run(state)
    audio.run(state)
    integration.run(state)

    assert state["vision_range"] == 10
    assert state["audio_range"] == 15
    assert "enemy" in state["objects_seen"]
    assert "footsteps" in state["sounds_heard"]
    assert state["confirmed_enemy"] == True
    print("✓ Multiple sensor coordination works")

    print("All multiple sensor tests passed!")


def test_error_handling():
    """Test error handling scenarios."""
    print("Testing error handling...")

    # Test sensor with callback that raises exception
    def failing_callback(state):
        raise ValueError("Sensor malfunction")

    failing_sensor = Sensor("failing_sensor", failing_callback)
    state = {"safe": True}

    # The sensor should propagate the exception
    try:
        failing_sensor.run(state)
        assert False, "Expected exception not raised"
    except ValueError as e:
        assert str(e) == "Sensor malfunction"
        assert state["safe"] == True  # State should remain unchanged
    print("✓ Exception propagation works")

    # Test sensor with None callback
    print("Testing None callback...")
    try:
        none_sensor = Sensor("none_test", None)
        none_sensor.run({})
        assert False, "Expected TypeError not raised"
    except TypeError:
        pass  # Expected behavior
    print("✓ None callback properly rejected")

    # Test callback that modifies state incorrectly
    print("Testing state corruption handling...")

    def corrupting_callback(state):
        # Try to replace the entire state dict (this should work in Python)
        state.clear()
        state.update({"corrupted": True})

    corrupt_sensor = Sensor("corrupt_test", corrupting_callback)
    state = {"original": "data"}
    corrupt_sensor.run(state)
    assert "original" not in state
    assert state["corrupted"] == True
    print("✓ State replacement handled")

    print("All error handling tests passed!")


def test_performance_characteristics():
    """Test performance characteristics of sensors."""
    import time

    print("Testing performance characteristics...")

    # Test rapid sensor execution
    execution_count = 0

    def fast_sensor(state):
        nonlocal execution_count
        execution_count += 1
        state["execution_count"] = execution_count

    fast = Sensor("fast_sensor", fast_sensor)
    state = {}

    # Run sensor many times quickly
    start_time = time.time()
    for i in range(1000):
        fast.run(state)
    end_time = time.time()

    execution_time = end_time - start_time
    assert execution_count == 1000
    assert state["execution_count"] == 1000
    print(f"✓ Executed 1000 sensor runs in {execution_time:.4f} seconds")

    # Test sensor with computational load
    def heavy_sensor(state):
        # Simulate computational work
        result = sum(i * i for i in range(100))
        state["computation_result"] = result

    heavy = Sensor("heavy_sensor", heavy_sensor)
    state = {}

    start_time = time.time()
    heavy.run(state)
    end_time = time.time()

    computation_time = end_time - start_time
    assert state["computation_result"] == sum(i * i for i in range(100))
    print(f"✓ Heavy computation sensor completed in {computation_time:.4f} seconds")

    print("All performance tests passed!")


def test_integration_patterns():
    """Test common integration patterns with sensors."""
    print("Testing integration patterns...")

    # Test sensor factory pattern
    def create_threshold_sensor(name, key, threshold, alert_key):
        def threshold_callback(state):
            value = state.get(key, 0)
            state[alert_key] = value > threshold

        return Sensor(name, threshold_callback)

    health_sensor = create_threshold_sensor(
        "health_check", "health", 20, "health_critical"
    )
    mana_sensor = create_threshold_sensor("mana_check", "mana", 10, "mana_low")

    state = {"health": 15, "mana": 25}
    health_sensor.run(state)
    mana_sensor.run(state)

    assert state["health_critical"] == False  # 15 > 20 is False
    assert state["mana_low"] == True  # 25 > 10 is True
    print("✓ Sensor factory pattern works")

    # Test sensor chaining pattern
    sensor_chain = []

    def position_sensor(state):
        state["x"] = 10
        state["y"] = 20

    def distance_sensor(state):
        x = state.get("x", 0)
        y = state.get("y", 0)
        state["distance_from_origin"] = (x**2 + y**2) ** 0.5

    def zone_sensor(state):
        distance = state.get("distance_from_origin", 0)
        if distance < 15:
            state["zone"] = "safe"
        elif distance < 30:
            state["zone"] = "caution"
        else:
            state["zone"] = "danger"

    sensor_chain.extend(
        [
            Sensor("position", position_sensor),
            Sensor("distance", distance_sensor),
            Sensor("zone", zone_sensor),
        ]
    )

    state = {}
    for sensor in sensor_chain:
        sensor.run(state)

    assert state["x"] == 10
    assert state["y"] == 20
    assert abs(state["distance_from_origin"] - 22.36) < 0.01
    assert state["zone"] == "caution"
    print("✓ Sensor chaining pattern works")

    print("All integration pattern tests passed!")


def test_comparison_with_csharp():
    """Test areas where Python implementation differs from C# version."""
    print("Testing C# compatibility aspects...")

    # Test name handling (C# auto-generates names, Python doesn't)
    sensor_with_name = Sensor("explicit_name", lambda s: None)
    assert sensor_with_name.name == "explicit_name"
    print("✓ Explicit naming works")

    # Test callback signature difference
    # C# passes Agent object, Python passes state dict directly
    def state_dict_callback(agent_state):
        # Python version - direct state access
        agent_state["python_style"] = True
        assert isinstance(agent_state, dict)

    python_sensor = Sensor("python_style", state_dict_callback)
    state = {}
    python_sensor.run(state)
    assert state["python_style"] == True
    print("✓ Python-style state dict callback works")

    # Test that Python version is simpler (no events)
    # C# has OnSensorRun event, Python doesn't
    event_log = []

    def logging_callback(state):
        event_log.append(f"Sensor ran with state keys: {list(state.keys())}")
        state["logged"] = True

    logging_sensor = Sensor("logger", logging_callback)
    state = {"initial": "value"}
    logging_sensor.run(state)

    assert len(event_log) == 1
    assert "initial" in event_log[0]
    assert state["logged"] == True
    print("✓ Manual event logging works (no built-in events)")

    print("All C# compatibility tests passed!")


# if __name__ == "__main__":
#     test_basic_functionality()
#     test_callback_variations()
#     test_multiple_sensors()
#     test_error_handling()
#     test_performance_characteristics()
#     test_integration_patterns()
#     test_comparison_with_csharp()
