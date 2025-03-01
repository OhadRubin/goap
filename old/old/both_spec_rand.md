Section 1
OVERALL ARCHITECTURE  
• The system is built around a Goal-Oriented Action Planning (GOAP) model, where an AI agent decides how to achieve a desired goal by formulating a sequence of actions at runtime.  
• The planner uses regressive search from the goal to the initial state, linking preconditions and effects.  
• Sensors provide up-to-date information about the world. Their collected data is stored in working memory as “facts.”  
• The planner uses both symbolic world-state checks and these sensor-produced facts to determine whether each action’s preconditions are satisfied.  
• References allow dynamic data flowing from one action’s effect to another action’s precondition, without hardcoding the actual value until runtime.

Section 2
DATA REPRESENTATION  
a) World State  
• A dictionary holds symbolic keys and values (e.g., {"hasKey": False, "isDoorUnlocked": False}).  
• The system may track booleans, IDs, or other small data.  
b) Working Memory  
• A collection (e.g., a list) of “fact” objects that store sensor readings, including a fact type (e.g., “VisibleEnemy”) and relevant attributes (e.g., the enemy’s position or ID).  
• Each fact may include a timestamp, confidence score, or other metadata.  
c) Actions  
• Each action has:  
  – A name (string identifier).  
  – A preconditions dictionary specifying symbolic requirements or references.  
  – An effects dictionary describing changes or references produced by that action.  
  – A cost (float) for planning.  
• References are placeholders in preconditions or effects that say, “this will be determined by the result of a prior action.”  
d) Sensors  
• Each sensor observes part of the environment, retrieving data (e.g., scanning for items, enemies, or positions).  
• When activated, it creates or updates facts in working memory.  
• May include a confidence threshold or logic for removing outdated facts.

Section 3
TERMINOLOGY AND HIGH-LEVEL STRUCTURE  
“An agent develops a plan in real time by supplying a goal to satisfy a planner. The GOAP planner looks at an action’s preconditions and effects in order to determine a queue of actions to satisfy the goal. For a full deep dive into the code itself, please refer to the listing provided in this post’s code blocks.”

Section 4
EXECUTION FLOW  
1) Sense Phase  
   – The agent calls each sensor to produce new facts and store them in working memory.  
   – Potentially remove outdated or low-confidence facts.  
2) Plan Phase  
   – The agent or manager calls the regressive GOAP planner, passing in the current world state and desired goal.  
   – The planner returns an ordered list of actions.  
3) Act Phase  
   – For each action in the plan, check again if the action’s context preconditions are valid (via working memory).  
   – If valid, run the action’s effect. The action might place a reference value into the world state, or handle external logic (like animating the character).  
   – If a precondition is not met anymore, replan using the updated state and facts.  
4) Loop  
   – The agent repeatedly cycles through sense → plan → act, maintaining up-to-date data in working memory.

Section 5
SENSORS, FACTS, AND WORKING MEMORY  
a) Sensor Interface  
• Each sensor has an update method: sense(memory, worldState).  
• On invocation, the sensor inspects the world (or worldState) and generates facts.  
b) Fact Objects  
• A fact contains, at minimum:  
  – factType (e.g., “EnemyLocation” or “DoorState”).  
  – data (could be a dictionary for more attributes).  
  – confidence (a float from 0 to 1).  
• The memory class stores and retrieves facts, possibly removing old ones as needed.  
c) Planner Integration  
• Before or during planning, the AI consults working memory to confirm context-based requirements for actions. For instance, an action might require that a “NodeAvailable” fact with confidence above 0.7 exists before it can be chosen.

Section 6
Some sensors are event-driven while others poll. Event-driven sensors are useful for recognizing instantaneous events like sounds and damage. Polling works better for sensors that need to extract information from the world.”

Section 7
Sensors deposit perceptions in working memory, providing a constant stream of up-to-date data. References allow you to ‘pass forward’ an effect from one action into the preconditions of subsequent actions, even if the actual value is only determined at runtime.”

Section 8
CONCLUSION  
“By defining both a planning system with references and a consistent sensor/working memory approach, we can dynamically pass data between actions and store relevant facts. The GOAP planner automatically figures out an optimal path (a plan) of actions that achieves the desired goal at runtime. This dynamic approach shines when the environment changes unexpectedly—GOAP can replan as needed, avoiding hand-crafted transitions between complex behaviors.”

Section 9
HOW REFERENCES WORK (EffectReference, reference(..))  
“References allow you to ‘pass forward’ an effect from one action into the preconditions of subsequent actions, even if the actual value is only determined at runtime. This is done via class EffectReference: A small class that annotates a requested effect name—and def reference(name: str): A convenience function that returns an EffectReference referencing that name.”
“For instance, if Action A has effects = { "tool_id": ... }, it means ‘I will provide a tool_id (but we’ll only know the real value at runtime).’ Another action B can specify preconditions = { "required_tool_id": reference("tool_id") }, meaning ‘I depend on the tool_id that was created or identified by the earlier action.’”

Section 10
REFERENCES  
• A reference object (EffectReference) is used in an action’s preconditions to denote that the real value is supplied by the respective effect from another action.  
• If an action’s effect is { "someID": ... }, it indicates “I will produce a ‘someID’ once executed, but its actual data field is determined dynamically.”  
• Another action’s precondition can specify { "neededID": reference("someID") }, linking that precondition to the specific runtime value provided by the prior action.  
• The planner unifies this link during regressive search, ensuring that any unsatisfied reference is matched by an appropriate effect from a preceding action in the plan.

Section 11
The system must support referencing the effects of actions, meaning that an action’s preconditions can use dynamic data produced by another action’s effect.”

Section 12
By linking the preconditions of one action to the effects of another, GOAP automatically ‘chains’ them into a valid plan, letting the system replan as needed, avoiding hand-crafted transitions between complex behaviors.”

Section 13
PLANNING ALGORITHM  
• Implement a regressive search (A* or BFS-based) from the goal state.  
• Whenever the search needs to satisfy a precondition key, it looks for an action whose effect matches that key (including referencing).  
• For referencing scenarios, if the effect is Ellipsis or a dynamic placeholder, the planner pairs it with that precondition, unifying the two so that the final plan has a consistent flow of data.  
• Cost accumulation is performed by summing each chosen action’s cost. The plan with the lowest total cost is selected.  
• During plan assembly, some additional “context preconditions” can consult working memory. For example, if an action requires “EnemyVisible,” it checks if the memory has a fact type “EnemyLocation” with high confidence.

Section 14
SENSORS AND WORKING MEMORY (WorkingMemoryFact)  
“All knowledge generated by sensors is stored in working memory in a common format. Sensors deposit perceptions in working memory and the planner uses these perceptions to guide its decision-making. A WorkingMemoryFact is a record containing a set of associated attributes. Different subsets of attributes are assigned depending on the type of knowledge the fact represents.”

Section 15
The system must support references—i.e., dynamic data passed from one action’s effect into the preconditions of subsequent actions—even if the actual value is only determined at runtime. By defining simple, isolated actions—and letting the system figure out the chain of dependencies—you can rapidly prototype sophisticated behaviors that respond to emergent gameplay changes.”
“This specification describes a specialized Goal-Oriented Action Planning (GOAP) system that incorporates sensors and working memory, and a state machine to distribute computation and drive AI behavior in real time. Implement the entire code architecture described here to replicate the system exactly, meaning that if you omit any details, the implementation will not be able to replicate the original system.”

Section 16
REQUIRED DATA STRUCTURES AND TYPES  
“A set of possible goals (conditions to fulfill), a set of actions (each with preconditions and effects), a world state (the environment and the agent’s own data), sensors that detect changes in the world, and a working memory storing perceptions in a consistent format. Facts could be hashed into bins based on the type of knowledge, or sorted in some manner.”

Section 17
FIVE DISTINCT SCENARIOS THAT USE REFERENCES (OPTIONAL)  
“Below are five hypothetical or illustrative usage scenarios that demonstrate how you can harness references in actions. These scenarios do not include the chanting example from the code snippet—thus giving fresh, concrete insight into references. For instance, passing a tool ID, flipping a table for cover, picking up a key to unlock a door, linking a generated power-on state, or using a repaired bridge to cross a river.”

Section 18
IMPLEMENTATION CHECKLIST  
• Implement a memory structure that can add, remove, and query facts by type.  
• Create multiple sensors, each with a sense method that writes one or more facts (with confidence) into memory.  
• Define Action classes that store preconditions, effects, references, cost, plus a method for context-based checks of working memory.  
• Implement the planning algorithm (e.g., an A* regressive search) that links actions by matching preconditions to effects, resolving references.  
• Ensure each action can run an execute(...) method that updates the world state (or triggers real game logic).  
• Include a cycle (or loop) that (1) triggers sensors to update memory, (2) attempts to plan a route from current world state to a specified goal, and (3) executes that plan step by step.
