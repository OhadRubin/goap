flowchart TD
    WS[World State] --> |Perceived by| CP[Cognitive Processor]
    CP --> |Updates| MM[Mental Models]
    MM --> |Informs| G[Goals]
    CP --> |Manages| CL[Cognitive Load]
    CP --> |Influences| RM[Resource Manager]
    CP --> |Regulates| SR[Self-Regulation Module]
    
    %% New Memory Components
    CP --> |Records experiences in| EM[Episodic Memory]
    EM --> |Contextualizes| MM
    EM <--> |References| SM[Semantic Memory]
    EM --> |Provides history for| IL[Intention Layer]
    SM --> |Provides knowledge for| IL
    
    %% New Communication Components
    MM <--> |Informs| CS[Communication System]
    IL --> |Provides intentions to| CS
    CS <--> |Exchanges with| OA[Other Agents]
    
    RM --> |Constrains| AP[Action Planner]
    G --> |Prioritized by| PP[Priority Processor] 
    PP --> |Feeds| AP
    SR --> |Monitors| AP
    MM --> |Provides context to| AP
    CL --> |Limits complexity of| AP
    IL --> |Provides motivation to| AP
    
    AP --> |Generates| Plan[Action Plan]
    Plan --> |Executed by| Executor[Action Executor]
    Executor --> |Changes| WS
    Executor --> |Provides feedback to| SR
    Executor --> |Stores outcome in| EM
    

# Extending CAPS for Communication and Memory-Driven Actions

To enable agents to communicate meaningfully and perform contextually-aware actions like organizing a pantry with previously purchased containers, we need to extend the Cognitive-Affective Planning System with two key components:

## 1. Communication System Extension

```csharp
class CommunicationSystem {
    AgentID selfID;
    Dictionary<AgentID, RelationshipModel> relationships;
    Queue<Message> messageQueue;
    Dictionary<ConversationID, Conversation> activeConversations;
    
    // Core methods
    Message ComposeMessage(AgentID recipient, CommunicationIntent intent, Dictionary<string, object> content);
    void ReceiveMessage(Message message);
    void UpdateRelationship(AgentID other, InteractionOutcome outcome);
    
    // Conversation management
    Conversation InitiateConversation(AgentID target, ConversationGoal goal);
    void ContinueConversation(ConversationID id, Message response);
    void EndConversation(ConversationID id, ConversationOutcome outcome);
    
    // Integration with mental models
    Dictionary<WorldProperty, bool> ExtractInformationFromMessage(Message message, float trustLevel);
    List<SocialConstraint> DeriveConstraintsFromRelationships();
}

class Message {
    AgentID sender;
    AgentID recipient;
    ConversationID conversationID;
    CommunicationIntent intent;
    Dictionary<string, object> content;
    float emotionalValence;
    DateTime timestamp;
    
    // Methods
    string ToNaturalLanguage(LanguageStyle style);
    Dictionary<string, object> ExtractSemanticContent();
}

enum CommunicationIntent {
    Share_Information,
    Request_Information,
    Request_Action,
    Express_Emotion,
    Establish_Social_Bond,
    Coordinate_Activity,
    Report_Completion,
    Request_Clarification
}
```

## 2. Memory System Extension

```csharp
class EpisodicMemory {
    List<Episode> episodes;
    Dictionary<string, float> episodeImportance;
    SpatialTemporalIndex episodeIndex;
    
    // Core methods
    void RecordEpisode(WorldState before, ActionSequence actions, WorldState after, EmotionalResponse response);
    List<Episode> RetrieveRelevantEpisodes(Situation currentSituation, int maxResults);
    void ConsolidateMemories(float timeAllocation);
    void DecayOldMemories(TimeSpan elapsedTime);
    
    // Specialized memory functions
    List<Episode> RetrievePastPurchases(ItemCategory category, TimeSpan lookbackPeriod);
    Dictionary<Location, List<StoredItem>> BuildInventoryKnowledge();
    void TagEpisodeWithNarrative(EpisodeID id, string narrativeDescription);
}

class SemanticMemory {
    Dictionary<Concept, ConceptNode> knowledgeNetwork;
    List<Procedure> knownProcedures;
    Dictionary<ObjectType, List<Properties>> objectKnowledge;
    
    // Methods
    Procedure RetrieveProcedure(ActionType action, List<Constraint> constraints);
    List<Relationship> GetRelationshipsBetween(Concept c1, Concept c2);
    void LearnNewConcept(Concept concept, List<Example> examples);
    void UpdateObjectKnowledge(ObjectType type, Properties newProperties);
}

class Episode {
    Guid id;
    DateTime timestamp;
    Location location;
    List<AgentID> participants;
    ActionSequence actions;
    WorldStateDelta changes;
    EmotionalResponse response;
    List<string> tags;
    
    // Narrative generation
    string GenerateNarrativeSummary(NarrativeDetail detail);
}
```

## 3. Intention Layer

```csharp
class IntentionLayer {
    List<Intention> currentIntentions;
    Dictionary<GoalType, float> motivationalStrengths;
    Dictionary<Intention, float> commitmentLevels;
    
    // Methods
    void FormIntention(GoalType goal, Reason reason, float strength);
    void AbandonIntention(Intention intention);
    List<Intention> GetActiveIntentions();
    void UpdateCommitmentLevels(List<Event> recentEvents);
    Intention SelectDominantIntention(Situation context);
}

class Intention {
    GoalType goal;
    Reason reason;
    DateTime formationTime;
    List<SubIntention> subcomponents;
    
    // Methods
    bool IsCompatibleWith(Intention other);
    float CalculateRelevanceToContext(Situation context);
    string GenerateExplanation();
}

class Reason {
    ReasonType type;  // Obligation, Desire, Necessity, etc.
    Episode sourceEpisode;  // When applicable
    List<Belief> supportingBeliefs;
    Dictionary<string, object> additionalContext;
}
```

## Connecting the Components

To enable the scenario "Organized the pantry using those containers I bought last month", the system needs to:

1. **Record the purchase in episodic memory**
   - Store details about container purchase (type, quantity, purpose)
   - Tag with temporal information ("last month")
   - Link to semantic knowledge about containers and organization

2. **Form intentions related to organization**
   - Create intention to organize pantry
   - Reference past purchase as enabling resource
   - Set commitment level based on various factors

3. **Generate and execute the organization plan**
   - Retrieve containers from remembered location
   - Apply organization procedure from semantic memory
   - Record completion in episodic memory

4. **Communicate about the completed action**
   - Reference both the organization action and the past purchase
   - Generate natural language expressing temporal relationship
   - Convey completion status

## Implementation Example: Pantry Organization Scenario

```csharp
// 1. Agent retrieves relevant past purchases
List<Episode> containerPurchases = episodicMemory.RetrievePastPurchases(
    ItemCategory.StorageContainers, 
    TimeSpan.FromDays(60)
);

// 2. Agent confirms containers are available resources
ResourceVerification containerCheck = resourceManager.VerifyResourceAvailability(
    new Resource { 
        Type = ResourceType.PhysicalObject,
        Properties = new Dictionary<string, object> {
            { "category", "container" },
            { "purpose", "storage" },
            { "location", "home" }
        }
    }
);

// 3. Agent forms intention to organize pantry
intentionLayer.FormIntention(
    GoalType.Organize,
    new Reason {
        type = ReasonType.DesireForOrder,
        supportingBeliefs = new List<Belief> {
            new Belief { property = "pantry_organization_level", value = "low" },
            new Belief { property = "has_appropriate_containers", value = true }
        },
        additionalContext = new Dictionary<string, object> {
            { "target_location", "pantry" },
            { "enabling_resource", containerPurchases[0].id }
        }
    },
    0.8f  // High motivation strength
);

// 4. After execution, agent reports completion
Message completionReport = communicationSystem.ComposeMessage(
    recipient: husband.agentID,
    intent: CommunicationIntent.Report_Completion,
    content: new Dictionary<string, object> {
        { "action", "organize" },
        { "target", "pantry" },
        { "tool", "containers" },
        { "tool_acquisition_time", "last month" },
        { "completion_status", "complete" }
    }
);

// 5. Message is converted to natural language
string naturalLanguageReport = completionReport.ToNaturalLanguage(LanguageStyle.Casual);
// Result: "Organized the pantry using those containers I bought last month"
```

## Technical Implications

1. **Memory Complexity**: Storing and indexing episodic memories requires significant data structures
2. **Temporal Reasoning**: System needs robust time management to relate "last month" to specific episodes
3. **Communication Protocols**: Agents need shared communication protocols and language models
4. **Narrative Generation**: Converting actions and memories to natural language requires sophisticated NLG
5. **Belief Consistency**: System must maintain consistent beliefs across episodic, semantic memory and mental models

With these extensions, CAPS agents can now:
1. Communicate meaningfully about past, present and planned activities
2. Remember, reference, and utilize previously acquired resources
3. Form intentions that span longer time periods
4. Generate believable narratives about their activities
5. Coordinate complex activities requiring multiple resources acquired at different times

Would you like me to elaborate on any specific aspect of these extensions, such as the technical implementation details, memory indexing strategies, or communication protocols between agents?