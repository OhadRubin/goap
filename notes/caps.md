# Extended GOAP: Cognitive-Affective Planning System (CAPS)

I'll propose an extension to GOAP that incorporates these cognitive dimensions while maintaining GOAP's strength in action planning. Let's call it the **Cognitive-Affective Planning System (CAPS)**.

flowchart TD
    WS[World State] --> |Perceived by| CP[Cognitive Processor]
    CP --> |Updates| MM[Mental Models]
    MM --> |Informs| G[Goals]
    CP --> |Manages| CL[Cognitive Load]
    CP --> |Influences| RM[Resource Manager]
    CP --> |Regulates| SR[Self-Regulation Module]
    
    RM --> |Constrains| AP[Action Planner]
    G --> |Prioritized by| PP[Priority Processor] 
    PP --> |Feeds| AP
    SR --> |Monitors| AP
    MM --> |Provides context to| AP
    CL --> |Limits complexity of| AP
    
    AP --> |Generates| Plan[Action Plan]
    Plan --> |Executed by| Executor[Action Executor]
    Executor --> |Changes| WS
    Executor --> |Provides feedback to| SR

## Core Enhancements to GOAP

## Detailed Component Description

### 1. Mental Model System
```
class MentalModel {
    Dictionary<WorldProperty, ValueWithConfidence> beliefs;
    Dictionary<AgentID, MentalModel> agentModels;  // Theory of mind
    List<CausalLink> causalNetwork;  // Understanding of cause/effect
    float complexity;  // Indicates cognitive load of maintaining this model
    
    // Methods
    void UpdateBeliefs(Perception perception, float attentionAllocation);
    MentalModel CreatePredictiveModel(TimeSpan futurePoint);
    void MergePerception(Perception newData, float trustFactor);
}
```

### 2. Resource Management Layer
```
class ResourceManager {
    Dictionary<ResourceType, Resource> availableResources;
    List<ResourceAllocation> currentAllocations;
    
    // Methods
    bool CanAllocateResources(GOAPAction action);
    void AllocateResourcesForAction(GOAPAction action);
    void ReleaseResources(ResourceAllocation allocation);
    float CalculateOpportunityCost(GOAPAction action);
    Dictionary<GOAPAction, float> AdjustActionCosts(List<GOAPAction> possibleActions);
}
```

### 3. Priority Processor
```
class PriorityProcessor {
    List<NeedState> currentNeeds;
    Dictionary<GoalType, float> goalValueModifiers;
    
    // Methods
    List<GOAPGoal> PrioritizeGoals(List<GOAPGoal> candidateGoals, MentalModel currentModel);
    float CalculateUrgency(GOAPGoal goal, WorldState currentState);
    void UpdateNeeds(float deltaTime, List<Event> recentEvents);
}
```

### 4. Cognitive Load Manager
```
class CognitiveLoadManager {
    float currentLoad;
    float maxCapacity;
    Dictionary<CognitiveProcess, float> activeProcessLoads;
    
    // Methods
    bool CanProcessNewTask(float complexity);
    void AllocateAttention(List<CognitiveProcess> processes);
    void SimplifyPlanning(ref GOAPPlanner planner, float loadFactor);
    float GetAvailableProcessingCapacity();
}
```

### 5. Self-Regulation Module
```
class SelfRegulator {
    List<PlanMonitor> activeMonitors;
    Dictionary<GoalType, PerformanceMetric> performanceHistory;
    
    // Methods
    void MonitorPlanExecution(ActionPlan plan, float checkFrequency);
    bool ShouldAbandonPlan(ActionPlan plan, WorldState currentState);
    void AdjustStrategy(GoalType goalType, PerformanceMetric results);
    List<AdaptiveRule> LearnFromExperience(List<PlanOutcome> outcomes);
}
```

### 6. Enhanced GOAP Planner
```
class CAPSPlanner : GOAPPlanner {
    MentalModel currentModel;
    ResourceManager resources;
    CognitiveLoadManager cognition;
    SelfRegulator regulator;
    PriorityProcessor priorities;
    
    // Overridden methods
    override ActionPlan CreatePlan(WorldState current, GOAPGoal goal) {
        // 1. Check cognitive capacity
        float planComplexity = EstimatePlanningComplexity(current, goal);
        if (!cognition.CanProcessNewTask(planComplexity)) {
            return CreateSimplifiedPlan(current, goal);
        }
        
        // 2. Adjust action costs based on resources
        List<GOAPAction> availableActions = GetAvailableActions();
        availableActions = resources.AdjustActionCosts(availableActions);
        
        // 3. Consider information uncertainty in mental model
        WorldState adjustedState = currentModel.GetWorldStateWithConfidence();
        
        // 4. Create plan with monitoring points
        ActionPlan plan = base.CreatePlan(adjustedState, goal);
        regulator.AttachMonitors(ref plan);
        
        return plan;
    }
    
    // New methods
    ActionPlan CreateContingencyPlans(ActionPlan mainPlan, List<RiskPoint> potentialFailures);
    void IncorporateSocialConsiderations(ref ActionPlan plan, List<SocialConstraint> constraints);
}
```

## Implementation Strategy

To implement CAPS as an extension of GOAP:

1. **Start with standard GOAP** as the foundation
2. **Add the Mental Model System** to represent NPC's understanding of the world
3. **Implement the Resource Manager** to track and allocate limited resources
4. **Build the Priority Processor** to handle competing goals
5. **Add the Cognitive Load Manager** to simulate limited attention/processing
6. **Implement the Self-Regulation Module** for monitoring and adjustment
7. **Extend the Planner** to incorporate all these systems

## Behavior Examples

With CAPS, NPCs could exhibit behaviors like:

1. **Adaptive planning under stress** - As cognitive load increases, plans become simpler
2. **Resource-constrained decision making** - NPC considers tradeoffs between time, energy, and other resources
3. **Incomplete information handling** - Plans account for uncertainty in the mental model
4. **Learning from experience** - Self-regulation improves planning over time
5. **Theory of mind** - NPC can reason about other agents' knowledge and intentions
6. **Emotional influence** - Affective state modulates priorities and resource allocation

## Technical Considerations

1. **Performance optimization** - Mental models and resource tracking add computational overhead
2. **Debugging complexity** - More sophisticated systems require better debugging tools
3. **Tuning challenges** - Balancing cognitive limitations for believable but not frustrating NPCs
4. **Graceful degradation** - System should fail intelligently when overloaded

Would you like me to elaborate on any specific aspect of this CAPS extension? For example, I could provide more detail on implementation patterns, example scenarios, or integration strategies with existing game engines.