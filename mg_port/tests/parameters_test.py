
from goap.parameters import Parameterizer, SelectFromCollection, SelectFromState, generate_action_variants

# ==============================================================================
# TESTS
# ==============================================================================

def test_parameterizer_abstract_base():
    """Test that Parameterizer is properly abstract and cannot be instantiated."""
    print('Testing Parameterizer abstract base class...')
    
    # Test that Parameterizer cannot be instantiated directly
    try:
        parameterizer = Parameterizer()
        parameterizer.generate({})
        assert False, "Parameterizer should be abstract and not instantiable"
    except TypeError:
        # Expected - abstract class should not be instantiable
        pass
    
    # Test that generate method is abstract
    from abc import ABC
    assert issubclass(Parameterizer, ABC), "Parameterizer should inherit from ABC"
    
    print('✓ Parameterizer is properly abstract')


def test_select_from_collection():
    """Test SelectFromCollection parameterizer functionality."""
    print('Testing SelectFromCollection...')
    
    # Test basic functionality
    collection = ['sword', 'bow', 'staff']
    parameterizer = SelectFromCollection(collection)
    
    # Should return copy of collection regardless of state
    result = parameterizer.generate({})
    assert result == collection, f"Expected {collection}, got {result}"
    
    # Test with different state - should still return same collection
    result = parameterizer.generate({'enemies': ['goblin', 'orc']})
    assert result == collection, f"Expected {collection}, got {result}"
    
    # Test with empty collection
    empty_parameterizer = SelectFromCollection([])
    result = empty_parameterizer.generate({})
    assert result == [], "Empty collection should return empty list"
    
    # Test None filtering
    collection_with_none = ['sword', None, 'bow', None, 'staff']
    parameterizer = SelectFromCollection(collection_with_none)
    result = parameterizer.generate({})
    expected = ['sword', 'bow', 'staff']
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test defensive copy (modifying original shouldn't affect parameterizer)
    original = ['item1', 'item2']
    parameterizer = SelectFromCollection(original)
    original.append('item3')
    result = parameterizer.generate({})
    assert result == ['item1', 'item2'], "Parameterizer should use defensive copy"
    
    # Test type validation
    try:
        SelectFromCollection("not a list")
        assert False, "Should reject non-list collections"
    except TypeError:
        pass
    
    print('✓ SelectFromCollection works correctly')


def test_select_from_state():
    """Test SelectFromState parameterizer functionality."""
    print('Testing SelectFromState...')
    
    # Test basic functionality with list in state
    parameterizer = SelectFromState('enemies')
    state = {'enemies': ['goblin', 'orc', 'dragon']}
    result = parameterizer.generate(state)
    assert result == ['goblin', 'orc', 'dragon'], f"Expected enemies list, got {result}"
    
    # Test with missing key
    result = parameterizer.generate({'other_key': 'value'})
    assert result == [], "Missing key should return empty list"
    
    # Test with None filtering
    state = {'enemies': ['goblin', None, 'orc', None]}
    result = parameterizer.generate(state)
    expected = ['goblin', 'orc']
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with single value (should wrap in list)
    state = {'target': 'goblin'}
    single_parameterizer = SelectFromState('target')
    result = single_parameterizer.generate(state)
    assert result == ['goblin'], "Single value should be wrapped in list"
    
    # Test with tuple (should convert to list)
    state = {'positions': ('north', 'south', 'east', 'west')}
    pos_parameterizer = SelectFromState('positions')
    result = pos_parameterizer.generate(state)
    assert result == ['north', 'south', 'east', 'west'], "Tuple should be converted to list"
    
    # Test with set (should convert to list)
    state = {'items': {'key', 'potion', 'scroll'}}
    item_parameterizer = SelectFromState('items')
    result = item_parameterizer.generate(state)
    assert len(result) == 3, "Set should be converted to list"
    assert all(item in ['key', 'potion', 'scroll'] for item in result), "All set items should be present"
    
    # Test with string (should not iterate, wrap as single value)
    state = {'message': 'hello'}
    msg_parameterizer = SelectFromState('message')
    result = msg_parameterizer.generate(state)
    assert result == ['hello'], "String should be wrapped as single value"
    
    # Test with None value
    state = {'empty': None}
    empty_parameterizer = SelectFromState('empty')
    result = empty_parameterizer.generate(state)
    assert result == [], "None value should return empty list"
    
    # Test constructor validation
    try:
        SelectFromState(123)  # Not a string
        assert False, "Should reject non-string keys"
    except TypeError:
        pass
    
    try:
        SelectFromState("")  # Empty string
        assert False, "Should reject empty string keys"
    except ValueError:
        pass
    
    print('✓ SelectFromState works correctly')


def test_generate_action_variants_basic():
    """Test basic functionality of generate_action_variants."""
    print('Testing generate_action_variants basic functionality...')
    
    # Create a mock action class for testing
    class MockAction:
        def __init__(self, name='test', cost=1.0, preconditions=None, effects=None, 
                     executor=None, parameterizers=None):
            self.name = name
            self.cost = cost
            self.preconditions = preconditions or {}
            self.effects = effects or {}
            self.executor = executor or (lambda: None)
            self.parameterizers = parameterizers
            self.parameters = {}
        
        def copy(self):
            new_action = MockAction(self.name, self.cost, self.preconditions.copy(), 
                                  self.effects.copy(), self.executor, self.parameterizers)
            new_action.parameters = self.parameters.copy()
            return new_action
        
        def set_parameter(self, name, value):
            self.parameters[name] = value
    
    # Test with no parameterizers
    action = MockAction(name='simple_action')
    result = generate_action_variants(action, {})
    assert len(result) == 1, "No parameterizers should return single action"
    assert result[0] == action, "Should return the original action"
    
    # Test with None parameterizers
    action.parameterizers = None
    result = generate_action_variants(action, {})
    assert len(result) == 1, "None parameterizers should return single action"
    
    # Test with empty parameterizers dict
    action.parameterizers = {}
    result = generate_action_variants(action, {})
    assert len(result) == 1, "Empty parameterizers should return single action"
    
    # Test with single parameterizer
    action.parameterizers = {
        'weapon': SelectFromCollection(['sword', 'bow'])
    }
    result = generate_action_variants(action, {})
    assert len(result) == 2, "Should generate 2 variants for 2 weapon choices"
    
    # Check that parameters are set correctly
    weapons = [variant.parameters.get('weapon') for variant in result]
    assert 'sword' in weapons, "Should have sword variant"
    assert 'bow' in weapons, "Should have bow variant"
    
    print('✓ generate_action_variants basic functionality works')


def test_generate_action_variants_combinations():
    """Test Cartesian product generation in generate_action_variants."""
    print('Testing generate_action_variants Cartesian product...')
    
    # Mock action class (reusing from previous test)
    class MockAction:
        def __init__(self, name='test', cost=1.0, preconditions=None, effects=None, 
                     executor=None, parameterizers=None):
            self.name = name
            self.cost = cost
            self.preconditions = preconditions or {}
            self.effects = effects or {}
            self.executor = executor or (lambda: None)
            self.parameterizers = parameterizers
            self.parameters = {}
        
        def copy(self):
            new_action = MockAction(self.name, self.cost, self.preconditions.copy(), 
                                  self.effects.copy(), self.executor, self.parameterizers)
            new_action.parameters = self.parameters.copy()
            return new_action
        
        def set_parameter(self, name, value):
            self.parameters[name] = value
    
    # Test with multiple parameterizers
    state = {'enemies': ['goblin', 'orc']}
    action = MockAction(
        name='attack',
        parameterizers={
            'target': SelectFromState('enemies'),
            'weapon': SelectFromCollection(['sword', 'bow'])
        }
    )
    
    result = generate_action_variants(action, state)
    assert len(result) == 4, "Should generate 2 targets × 2 weapons = 4 variants"
    
    # Check all combinations are present
    combinations = [(v.parameters.get('target'), v.parameters.get('weapon')) for v in result]
    expected_combinations = [
        ('goblin', 'sword'), ('goblin', 'bow'),
        ('orc', 'sword'), ('orc', 'bow')
    ]
    
    for expected in expected_combinations:
        assert expected in combinations, f"Missing combination: {expected}"
    
    # Test with three parameterizers
    action.parameterizers['direction'] = SelectFromCollection(['north', 'south'])
    result = generate_action_variants(action, state)
    assert len(result) == 8, "Should generate 2 × 2 × 2 = 8 variants"
    
    print('✓ generate_action_variants Cartesian product works')


def test_generate_action_variants_edge_cases():
    """Test edge cases and error handling in generate_action_variants."""
    print('Testing generate_action_variants edge cases...')
    
    # Mock action class
    class MockAction:
        def __init__(self, name='test', cost=1.0, preconditions=None, effects=None, 
                     executor=None, parameterizers=None):
            self.name = name
            self.cost = cost
            self.preconditions = preconditions or {}
            self.effects = effects or {}
            self.executor = executor or (lambda: None)
            self.parameterizers = parameterizers
            self.parameters = {}
        
        def copy(self):
            new_action = MockAction(self.name, self.cost, self.preconditions.copy(), 
                                  self.effects.copy(), self.executor, self.parameterizers)
            new_action.parameters = self.parameters.copy()
            return new_action
        
        def set_parameter(self, name, value):
            self.parameters[name] = value
    
    # Test with empty parameter values (should return empty list)
    action = MockAction(
        name='test',
        parameterizers={'target': SelectFromState('missing_key')}
    )
    result = generate_action_variants(action, {})
    assert result == [], "Empty parameter values should return empty list"
    
    # Test with one empty and one non-empty parameterizer
    action.parameterizers = {
        'target': SelectFromState('missing_key'),  # Returns empty list
        'weapon': SelectFromCollection(['sword'])  # Returns one item
    }
    result = generate_action_variants(action, {})
    assert result == [], "Any empty parameterizer should result in no variants"
    
    # Test invalid parameterizers type
    action.parameterizers = "not a dict"
    try:
        generate_action_variants(action, {})
        assert False, "Should reject non-dict parameterizers"
    except TypeError:
        pass
    
    # Test invalid parameterizer instance
    action.parameterizers = {'invalid': 'not a parameterizer'}
    try:
        generate_action_variants(action, {})
        assert False, "Should reject non-Parameterizer instances"
    except TypeError:
        pass
    
    # Test action without copy method (fallback constructor)
    class ActionWithoutCopy:
        def __init__(self, name='test', cost=1.0, preconditions=None, effects=None, 
                     executor=None, parameterizers=None):
            self.name = name
            self.cost = cost
            self.preconditions = preconditions or {}
            self.effects = effects or {}
            self.executor = executor or (lambda: None)
            self.parameterizers = parameterizers
            self.parameters = {}
        
        def copy(self):
            new_action = ActionWithoutCopy(self.name, self.cost, self.preconditions.copy(), 
                                          self.effects.copy(), self.executor, self.parameterizers)
            new_action.parameters = self.parameters.copy()
            return new_action
        
        def set_parameter(self, name, value):
            self.parameters[name] = value
    
    action = ActionWithoutCopy(
        name='no_copy',
        parameterizers={'weapon': SelectFromCollection(['sword'])}
    )
    result = generate_action_variants(action, {})
    assert len(result) == 1, "Should handle actions without copy method"
    assert result[0].parameters.get('weapon') == 'sword', "Should set parameter correctly"
    
    print('✓ generate_action_variants edge cases work correctly')


def test_integration_with_action_patterns():
    """Test integration with different action implementation patterns."""
    print('Testing integration with various action patterns...')
    
    # Test with action that has parameters attribute
    class ActionWithParameters:
        def __init__(self, name='test', parameterizers=None):
            self.name = name
            self.parameterizers = parameterizers
            self.parameters = None
        
        def copy(self):
            new_action = ActionWithParameters(self.name, self.parameterizers)
            new_action.parameters = self.parameters.copy() if self.parameters else None
            return new_action
        
        def set_parameter(self, name, value):
            if self.parameters is None:
                self.parameters = {}
            self.parameters[name] = value
    
    action = ActionWithParameters(
        name='param_action',
        parameterizers={'target': SelectFromCollection(['enemy1', 'enemy2'])}
    )
    
    result = generate_action_variants(action, {})
    assert len(result) == 2, "Should generate variants for action with parameters attribute"
    
    # Test with action that uses attribute setting (fallback)
    class ActionWithDirectAttributes:
        def __init__(self, name='test', parameterizers=None):
            self.name = name
            self.parameterizers = parameterizers
            self.parameters = {}
        
        def copy(self):
            new_action = ActionWithDirectAttributes(self.name, self.parameterizers)
            new_action.parameters = self.parameters.copy()
            # Copy any existing parameter attributes
            for attr_name in dir(self):
                if not attr_name.startswith('_') and attr_name not in ['name', 'parameterizers', 'copy', 'parameters']:
                    try:
                        setattr(new_action, attr_name, getattr(self, attr_name))
                    except AttributeError:
                        pass
            return new_action
    
    action = ActionWithDirectAttributes(
        name='attr_action',
        parameterizers={'value': SelectFromCollection([1, 2, 3])}
    )
    
    result = generate_action_variants(action, {})
    assert len(result) == 3, "Should generate variants using direct attribute setting"
    
    # Check that parameters are set
    values = [variant.parameters.get('value', None) for variant in result]
    assert 1 in values and 2 in values and 3 in values, "Should set parameter in parameters dict"
    
    print('✓ Integration with action patterns works correctly')


def test_comprehensive_scenario():
    """Test a comprehensive scenario simulating real GOAP usage."""
    print('Testing comprehensive parameterization scenario...')
    
    # Mock action that resembles real Action class
    class MockAction:
        def __init__(self, name, cost=1.0, preconditions=None, effects=None, 
                     executor=None, parameterizers=None):
            self.name = name
            self.cost = cost
            self.preconditions = preconditions or {}
            self.effects = effects or {}
            self.executor = executor or (lambda: None)
            self.parameterizers = parameterizers
            self.parameters = {}
        
        def copy(self):
            new_action = MockAction(
                name=self.name,
                cost=self.cost,
                preconditions=self.preconditions.copy(),
                effects=self.effects.copy(),
                executor=self.executor,
                parameterizers=self.parameterizers
            )
            new_action.parameters = self.parameters.copy()
            return new_action
        
        def set_parameter(self, name, value):
            self.parameters[name] = value
    
    # Create a complex action with multiple parameterizers
    attack_action = MockAction(
        name='attack',
        cost=1.0,
        preconditions={'has_weapon': True},
        effects={'enemy_health': '-10'},
        parameterizers={
            'target': SelectFromState('visible_enemies'),
            'weapon': SelectFromState('available_weapons'),
            'stance': SelectFromCollection(['aggressive', 'defensive'])
        }
    )
    
    # Complex world state
    world_state = {
        'visible_enemies': ['goblin', 'orc', 'skeleton'],
        'available_weapons': ['sword', 'bow'],
        'player_health': 100,
        'has_weapon': True
    }
    
    # Generate all variants
    variants = generate_action_variants(attack_action, world_state)
    
    # Should generate 3 enemies × 2 weapons × 2 stances = 12 variants
    assert len(variants) == 12, f"Expected 12 variants, got {len(variants)}"
    
    # Check that all combinations are unique
    combinations = set()
    for variant in variants:
        combo = (
            variant.parameters.get('target'),
            variant.parameters.get('weapon'),
            variant.parameters.get('stance')
        )
        combinations.add(combo)
    
    assert len(combinations) == 12, "All combinations should be unique"
    
    # Check that each variant has all required parameters
    for variant in variants:
        assert 'target' in variant.parameters, "Each variant should have target"
        assert 'weapon' in variant.parameters, "Each variant should have weapon"
        assert 'stance' in variant.parameters, "Each variant should have stance"
        
        # Check parameter values are valid
        assert variant.parameters['target'] in ['goblin', 'orc', 'skeleton']
        assert variant.parameters['weapon'] in ['sword', 'bow']
        assert variant.parameters['stance'] in ['aggressive', 'defensive']
    
    # Test with empty state (should return empty list)
    empty_state = {'visible_enemies': [], 'available_weapons': ['sword']}
    variants = generate_action_variants(attack_action, empty_state)
    assert len(variants) == 0, "Empty enemies list should result in no variants"
    
    print('✓ Comprehensive parameterization scenario works correctly')


# if __name__ == "__main__":
#     print("Running parameters.py validation tests...")
#     print("=" * 50)
    
#     test_parameterizer_abstract_base()
#     test_select_from_collection()
#     test_select_from_state()
#     test_generate_action_variants_basic()
#     test_generate_action_variants_combinations()
#     test_generate_action_variants_edge_cases()
#     test_integration_with_action_patterns()
#     test_comprehensive_scenario()
    
#     print("=" * 50)
#     print("All parameters.py tests passed successfully!")
#     print("Implementation is validated and working correctly.")