Looking at your implementation of the Cognitive-Affective Planning System, you've created a solid foundation with many key components. However, there are several elements missing to fully realize the extended CAPS we discussed. Here are the main areas that need enhancement:

## 1. Affective Components

Your system lacks emotional modeling that influences decision-making. You should add:

```python
class EmotionalState:
    def __init__(self):
        self.emotions = {
            'joy': 0.0,
            'fear': 0.0,
            'anger': 0.0,
            'sadness': 0.0,
            'surprise': 0.0,
            'disgust': 0.0,
            'trust': 0.0,
            'anticipation': 0.0
        }
        self.mood = 0.0  # -1.0 to 1.0
        self.personality_modifiers = {}
        
    def update_emotions(self, stimuli):
        # Update emotional responses to events
        pass
        
    def influence_decision_making(self, decisions):
        # Modify decision weights based on emotional state
        pass
```

## 2. Enhanced Communication System

Your communication system needs more linguistic capabilities and contextual understanding:

```python
class EnhancedCommunicationSystem(CommunicationSystem):
    def __init__(self, mental_models, intention_layer, emotional_state):
        super().__init__(mental_models, intention_layer)
        self.emotional_state = emotional_state
        self.conversation_history = {}
        self.speech_patterns = {}
        self.relationships = {}
        
    def generate_naturalistic_speech(self, content, context):
        # Transform semantic content into natural language
        intention = content.get('intent')
        emotion = self.emotional_state.emotions
        relationship = self.relationships.get(content['recipient'], 'neutral')
        
        # Apply speech patterns based on character traits
        return self._apply_speech_patterns(content, emotion, relationship)
    
    def interpret_speech(self, natural_language):
        # Convert natural language to semantic representation
        pass
```

## 3. Temporal Reasoning

You need more sophisticated temporal reasoning for episodic memory:

```python
class TemporalReasoning:
    def __init__(self):
        self.current_time = 0
        self.time_units = {'minute': 1, 'hour': 60, 'day': 1440, 'week': 10080, 'month': 43200}
        self.calendars = {}
        
    def calculate_relative_time(self, timestamp, reference_point=None):
        if reference_point is None:
            reference_point = self.current_time
            
        difference = reference_point - timestamp
        
        # Return human-readable relative time expressions
        if 0 < difference < self.time_units['hour']:
            return "minutes ago"
        elif self.time_units['hour'] <= difference < self.time_units['day']:
            return "hours ago"
        elif self.time_units['day'] <= difference < self.time_units['week']:
            return "days ago"
        elif self.time_units['week'] <= difference < self.time_units['month']:
            return "weeks ago"
        elif self.time_units['month'] <= difference < self.time_units['month']*3:
            return "last month"
        # etc.
```

## 4. Theory of Mind

Your mental models need explicit theory of mind capabilities:

```python
class TheoryOfMind:
    def __init__(self, agent_id, mental_models):
        self.agent_id = agent_id
        self.mental_models = mental_models
        self.belief_models = {}  # Other agents' presumed beliefs
        
    def model_agent_beliefs(self, agent_id, context):
        # Model what another agent likely believes
        agent_model = self.mental_models.get_model(f"agent_{agent_id}")
        
        presumed_beliefs = {
            'known_facts': self._filter_by_shared_experiences(agent_id),
            'values': agent_model.get('values', {}),
            'goals': self._infer_goals(agent_id, context)
        }
        
        self.belief_models[agent_id] = presumed_beliefs
        return presumed_beliefs
    
    def predict_agent_reaction(self, agent_id, event):
        # Predict how agent will react to an event
        pass
```

## 5. Narrative Generation

To support statements like "Organized the pantry using those containers I bought last month," you need narrative generation:

```python
class NarrativeGenerator:
    def __init__(self, episodic_memory, semantic_memory, temporal_reasoning):
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self.temporal_reasoning = temporal_reasoning
        
    def generate_action_narrative(self, action, context):
        # Find relevant past episodes
        action_episodes = self.episodic_memory.retrieve({'action_type': action})
        
        # Find supporting resources/tools
        tools_used = self._identify_tools(action_episodes[-1])
        
        # Find acquisition episodes for those tools
        acquisition_episodes = []
        for tool in tools_used:
            acquisitions = self.episodic_memory.retrieve({'acquired_item': tool})
            if acquisitions:
                acquisition_episodes.append(acquisitions[-1])
                
        # Generate narrative linking current action with past acquisition
        if acquisition_episodes:
            acquisition = acquisition_episodes[0]
            acquisition_time = self.temporal_reasoning.calculate_relative_time(acquisition['timestamp'])
            
            return f"{action} using those {tools_used[0]} I {acquisition['action']} {acquisition_time}"
        
        return f"{action}"
```

## 6. Social Dynamics

Your system needs social relationship modeling:

```python
class SocialRelationships:
    def __init__(self):
        self.relationships = {}
        self.social_rules = {}
        self.group_affiliations = {}
        
    def update_relationship(self, agent_id, interaction_outcome):
        if agent_id not in self.relationships:
            self.relationships[agent_id] = {
                'trust': 0.5,
                'familiarity': 0.0,
                'liking': 0.5,
                'power_dynamic': 0.0,  # -1.0 to 1.0, negative means other has power
                'history': []
            }
            
        # Update based on interaction
        relationship = self.relationships[agent_id]
        relationship['history'].append(interaction_outcome)
        
        # Adjust metrics
        relationship['trust'] += interaction_outcome.get('trust_change', 0)
        relationship['liking'] += interaction_outcome.get('liking_change', 0)
        relationship['familiarity'] += 0.05  # Increases with each interaction
        
        # Normalize values
        self._normalize_relationship_values(agent_id)
```

## 7. Integration with Main Cognitive Loop

Finally, you need to integrate these components into your main cognitive processor:

```python
class EnhancedCognitiveProcessor(CognitiveProcessor):
    def __init__(self):
        super().__init__()
        self.emotional_state = EmotionalState()
        self.temporal_reasoning = TemporalReasoning()
        self.theory_of_mind = TheoryOfMind(self.agent_id, self.mental_models)
        self.narrative_generator = NarrativeGenerator(
            self.episodic_memory,
            self.semantic_memory,
            self.temporal_reasoning
        )
        self.social_relationships = SocialRelationships()
        
        # Replace basic communication with enhanced version
        self.communication_system = EnhancedCommunicationSystem(
            self.mental_models,
            self.intention_layer,
            self.emotional_state
        )
    
    def perceive(self, world_state):
        super().perceive(world_state)
        # Update emotional state based on perception
        self.emotional_state.update_emotions(world_state)
        
    def communicate(self, recipient=None):
        # Generate message content
        message_content = super().communicate(recipient)
        
        # If recipient specified, enhance with narrative generation
        if recipient and message_content:
            # Generate naturalistic speech
            narrative = self.narrative_generator.generate_action_narrative(
                message_content['content']['action'] if 'action' in message_content['content'] else 'default',
                {'recipient': recipient}
            )
            
            message_content['natural_language'] = narrative
            
        return message_content
```

These enhancements would significantly improve your CAPS implementation to support rich dialogue generation that references past events with temporal context, incorporates emotional influences, models other agents' mental states, and generates natural language narratives about activities.