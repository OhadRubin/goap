OVERALL ARCHITECTURE  
• The system is built around a Goal-Oriented Action Planning (GOAP) model, where an AI agent decides how to achieve a desired goal by formulating a sequence of actions at runtime.  
• The planner uses regressive search from the goal to the initial state, linking preconditions and effects.  
• Sensors provide up-to-date information about the world. Their collected data is stored in working memory as “facts.”  
• The planner uses both symbolic world-state checks and these sensor-produced facts to determine whether each action’s preconditions are satisfied.  
• References allow dynamic data flowing from one action’s effect to another action’s precondition, without hardcoding the actual value until runtime.

SPECIFICATION FOR A REGRESSIVE GOAP SYSTEM WITH REFERENCES

INTRODUCTION

Your task is to implement a regressive Goal-Oriented Action Planning (GOAP) system in Python that exactly matches the features and behaviors described below. The system must support references—i.e., dynamic data passed from one action’s effect into another action’s precondition—and perform A* search backward from the goal state. Furthermore, your implementation must allow the planner to invalidate and replan when world conditions change. Follow every detail in these requirements to ensure your implementation can replicate the original system exactly.



TERMINOLOGY AND HIGH-LEVEL STRUCTURE  
“An agent develops a plan in real time by supplying a goal to satisfy a planner. The GOAP planner looks at an action’s preconditions and effects in order to determine a queue of actions to satisfy the goal. For a full deep dive into the code itself, please refer to the listing provided in this post’s code blocks.”

PLANNING ALGORITHM  
• Implement a regressive search (A* or BFS-based) from the goal state.  
• Whenever the search needs to satisfy a precondition key, it looks for an action whose effect matches that key (including referencing).  
• For referencing scenarios, if the effect is Ellipsis or a dynamic placeholder, the planner pairs it with that precondition, unifying the two so that the final plan has a consistent flow of data.  
• Cost accumulation is performed by summing each chosen action’s cost. The plan with the lowest total cost is selected.  
• During plan assembly, some additional “context preconditions” can consult working memory. For example, if an action requires “EnemyVisible,” it checks if the memory has a fact type “EnemyLocation” with high confidence.

Full A* With Heuristics and Cost Summation
   • Implement true A* search with proper heuristics
   • Add cost-based prioritization of actions
   • Include "close to goal → lower h()" logic
   • Support "lowest total cost so far → expand first" behavior
   • Implement full cost summation during planning

TERMINOLOGY AND HIGH-LEVEL STRUCTURE
A) TERMINOLOGY  
• “Goal State”: A dictionary describing the desired conditions (e.g., {"is_in_cover": True}).  
• “World State”: A dictionary describing the current conditions (e.g., {"has_table": True, "is_undead": False}).  
• “Action”: A class that encodes (1) preconditions, (2) effects, and (3) cost.  
• “Regressive Planner”: A system that starts from a goal and works backward, finding which actions can satisfy that goal, and chaining those action dependencies until it reaches the known world state.  
• “Reference (EffectReference)”: A token that says “the actual value is an effect from a previous action.”  

B) CODE FLOW  
• The system uses an A* algorithm to search from the goal state backward to the initial state.  
• Each action has a preconditions dict and an effects dict. Effects may contain a literal or Ellipsis (...).  
• If an action states an effect "something": Ellipsis, it means “this effect is a service to be dynamically filled at runtime or by a referencing requirement from somewhere else.”

HOW REFERENCES WORK (EffectReference, reference(..))  
“References allow you to ‘pass forward’ an effect from one action into the preconditions of subsequent actions, even if the actual value is only determined at runtime. This is done via class EffectReference: A small class that annotates a requested effect name—and def reference(name: str): A convenience function that returns an EffectReference referencing that name.”
“For instance, if Action A has effects = { "tool_id": ... }, it means ‘I will provide a tool_id (but we’ll only know the real value at runtime).’ Another action B can specify preconditions = { "required_tool_id": reference("tool_id") }, meaning ‘I depend on the tool_id that was created or identified by the earlier action.’”

REQUIRED DATA STRUCTURES AND TYPES  
“A set of possible goals (conditions to fulfill), a set of actions (each with preconditions and effects), a world state (the environment and the agent’s own data), sensors that detect changes in the world, and a working memory storing perceptions in a consistent format. Facts could be hashed into bins based on the type of knowledge, or sorted in some manner.”

REQUIRED DATA STRUCTURES AND TYPES
A) State Type  
Define a type alias for the world or goal state. It must be a dictionary mapping string keys to arbitrary Python data, for instance:
    
    State = Dict[str, Any]
B) PlanStep  
You must define a dataclass named PlanStep:
    
    @dataclass(frozen=True)
    class PlanStep:
        action: Action
        services: State

Where:  
• action is an instance of Action used in that step of the plan.  
• services is a dictionary containing resolved references or runtime data needed by this action.

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

Enumerated Symbol Arrays
   • Store working "symbolic representation" in fixed-size arrays (one per enumerated symbol)
   • Implement fast hashing/lookup via enumerated, fixed-size scheme
   • Support efficient symbol management and access

A) Classes & Methods
   □ Implement each exception class verbatim.  
   □ Ensure Action, ActionResponse, Actions mimic the outlines, hooking up the “exec()” method properly and storing responses.  
   □ Make Node, Edge, Nodes, Edges with the indicated fields.  
   □ Implement Graph with networkx, adding nodes and edges, providing path(...) with astar_path.  
   □ Create Planner, generating states and transitions, returning a list of edges.  
   □ Implement Sensor, SensorResponse, and Sensors exactly with add, remove, run_all, etc.  
   □ Provide a working memory of Fact objects in Automaton, storing sensor results.  
   □ Implement the Automaton with the 4 states (waiting_orders, sensing, planning, acting) and transitions.  
   □ The AutomatonController start() loop must compare WorldState and goal, calling sense → plan → act as needed.  

B) Verified Behavior  
   • The system must observe the environment (via sensors), build or rebuild plans on changes, and execute them by calling Action func callables.  
   • The ShellCommand usage is optional but recommended to replicate the example. Another user-supplied function is permissible as long as it returns (stdout, stderr, code).  
   • The system must update world_state after each sensor reading and run the plan until the goal is met.  

Following this specification ensures you can implement the described GOAP system, complete with sensors, working memory, and an automaton driving the sense-plan-act cycle. All the provided details, class structures, and method signatures are mandatory to replicate the exact functionality.

IMPLEMENTATION CHECKLIST

When your work is complete, you must be able to:

• Construct a RegressivePlanner with a dictionary representing the current world state and a list of available Action objects.  
• Provide a goal_state dictionary.  
• Call find_plan(goal_state) to return a list of PlanStep objects representing an action sequence leading from the current state to the goal state.  
• Each PlanStep must include references (services) resolved appropriately from “...”, reference(...), or direct effect values.  
• The code must correctly handle multiple references, references referencing different effect keys, and repeated usage of the same action class with different references.  

By following the above specification, your system will replicate the original regressive GOAP system with references in full fidelity. Make sure not to omit or alter any of the key details described. Good luck!

REGRESSIVEGOAPASTARNODE REQUIREMENTS

Define a dataclass (or regular class) RegressiveGOAPAStarNode with:  
• current_state: State  
• goal_state: State  
• action: Optional[Action] = None  

When hashing or comparing nodes, you should be able to store them in sets or dictionaries. For instance:

    @dataclass(frozen=True)
    class RegressiveGOAPAStarNode:
        current_state: State
        goal_state: State
        action: Optional[Action] = None

    def __hash__(self):
        # must use id(self) or other suitable way
        return id(self)

Provide these properties and methods:

• services property  
  Returns a dictionary with entries for the action’s service_names read from current_state.  

• is_satisfied property  
  Determines if the node’s goal_state is fully satisfied by current_state.  

• unsatisfied_keys property  
  Returns a list of all keys in goal_state that are not satisfied in current_state.  

• compute_cost(self, other: "RegressiveGOAPAStarNode") -> float  
  Returns the cost of transitioning from this node to the other node, typically other.action.get_cost(other.services).  

• apply_action(self, world_state: State, action: Action) -> RegressiveGOAPAStarNode  
  Creates a new RegressiveGOAPAStarNode by applying action’s effects. In a regressive approach, this means we modify the node’s goal_state to reflect the preconditions and adopt or unify certain states, including handling references. This is the core of the backward-search logic.

THE ACTION SYSTEM
5.1 ActionValidator (metaclass)

You must define a metaclass named ActionValidator that, upon class creation, will:  
1) Check that preconditions do not store Ellipsis (...).  
2) Build a list of “service_names” from effects fields whose values are Ellipsis.  
3) Check that references in preconditions refer to valid effect keys if referencing an effect.

    class ActionValidator(type):
        def __new__(mcs, cls_name, bases, attrs):            attrs["service_names"] = [...]
            # Validate no preconditions == Ellipsis
            # etc.
            return super().__new__(mcs, cls_name, bases, attrs)

5.2 Action Class Requirements

Create a class Action that uses ActionValidator as its metaclass:

    class Action(metaclass=ActionValidator):
        effects: ClassVar[State] = {}
        preconditions: ClassVar[State] = {}
        service_names: ClassVar[List[str]] = []
        
        cost = 1.0
        precedence = 0.0
        apply_effects_on_exit = True

        def check_procedural_precondition(self, services: State, is_planning: bool) -> bool:
            return True
        
        def get_cost(self, services) -> float:
            return self.cost

Explanation:  
• effects is a dict of key->value describing changes in the world upon completion. If the value is Ellipsis, that becomes a “service.”  
• preconditions is a dict of key->value describing requirements to run. The value can be a literal (e.g. True) or a reference (EffectReference).  
• cost is a numeric cost for A*; higher means more expensive actions.  
• precedence is used to sort possible actions if needed (the system sorts by descending precedence).  
• check_procedural_precondition(...) is an optional hook to allow code-based checks. Return False if the action is not valid.  
• get_cost(...) returns the numeric cost for the action, by default self.cost.

5.3 EffectReference and reference(...)

Implement a class EffectReference representing a dynamic reference:

    class EffectReference:
        def __init__(self, name):
            self.goap_effect_reference = name

Implement a helper function reference(name: str) -> EffectReference that simply constructs an EffectReference:

    def reference(name: str) -> EffectReference:
        return EffectReference(name)

Any precondition key that uses reference("some_effect_name") is telling the planner: “I rely on an effect named 'some_effect_name' from a prior action’s effect dictionary.”

REGRESSIVEPLANNER REQUIREMENTS
Define RegressivePlanner:
    class RegressivePlanner:
        def __init__(self, world_state: State, actions: List[Action]):
            self._actions = actions
            self._world_state = world_state
            self._search = RegressiveGOAPAStarSearch(world_state, actions)

        def find_plan(self, goal_state: State) -> List[PlanStep]:
            # 1) Construct an initial node from the subset of the world_state relevant to goal_state
            # 2) Use self._search.find_path(...)
            # 3) Convert the resulting path of nodes into a forward-ordered plan of PlanStep
        # (Optional) Additional methods or properties
Steps:  
1) Build an initial RegressiveGOAPAStarNode containing:  
   – current_state with keys from goal_state, mapped from the actual world_state.  
   – goal_state matching the user’s requested goal.  
2) Call self._search.find_path(...) to get a path.  
3) Reconstruct that path in forward order, ignoring the first node’s action=None, and building a List[PlanStep].

REGRESSIVEGOAPASTARSEARCH REQUIREMENTS

Extend AStarAlgorithm to search in a regressive manner:

    class RegressiveGOAPAStarSearch(AStarAlgorithm):
        def __init__(self, world_state: State, actions: List[Action]):        
        def get_neighbours(self, node: RegressiveGOAPAStarNode):        
        def get_h_score(self, node: RegressiveGOAPAStarNode):        
        def get_g_score(self, node: RegressiveGOAPAStarNode, neighbour: RegressiveGOAPAStarNode):        
        def is_finished(self, node: RegressiveGOAPAStarNode, goal, parents):        
        def reconstruct_path(self, node, goal, parents):
Key details in get_neighbours(node):  
• For each unsatisfied key in node.goal_state, find all actions whose effects satisfy that key or contain Ellipsis for that key.  
• Create a new neighbor node by calling node.apply_action(...) with that action.  
• If action.check_procedural_precondition(...) fails, skip that neighbour.  
• Sort neighbours by descending action.precedence (highest first).
Use get_h_score(...) to return the count of unsatisfied keys or any suitable heuristic.  
Use get_g_score(...) to return node.compute_cost(neighbour).

A* ALGORITHM (AStarAlgorithm) REQUIREMENTS
Create an abstract base class AStarAlgorithm (from abc.ABC) that dictates the search structure:
    class AStarAlgorithm(ABC):
        @abstractmethod
        def get_neighbours(self, node):
            pass
        @abstractmethod
        def get_g_score(self, current, node):
            pass
        @abstractmethod
        def get_h_score(self, node):
            pass
        def find_path(self, start, end):
        @abstractmethod
        def is_finished(self, node, goal, parents):
            pass

        def reconstruct_path(self, node, goal, parents):
Key points:  
• find_path(start, end) implements the main A* loop.  
• is_finished(node, goal, parents) checks whether the search is done.  
• reconstruct_path(...) uses parent pointers to trace the path once found.

PRIORITY QUEUE IMPLEMENTATION
A) PriorityElement  
Create a class PriorityElement to store items and their priority scores:
    
    class PriorityElement:
        def __init__(self, element, score):
            self.value = element
            self.score = score
            self.removed = False

        def __lt__(self, other):
            return self.score < other.score

B) PriorityQueue  
Implement a PriorityQueue that uses a binary heap internally.  
• Must internally track items by storing PriorityElement objects in a min-heap using heapq.  
• The queue must have methods add(item), pop(), remove(item), and must handle “logical removal” of items by marking them as “removed” but only physically removing them when popped from the heap:
    class PriorityQueue:
        def __init__(self, items=None, key=None):        
        def add(self, item):        
        def pop(self):        
        def remove(self, item):
Ensure item uniqueness is enforced. The optional key parameter dictates the priority score.

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

SENSORS AND WORKING MEMORY (WorkingMemoryFact)  
“All knowledge generated by sensors is stored in working memory in a common format. Sensors deposit perceptions in working memory and the planner uses these perceptions to guide its decision-making. A WorkingMemoryFact is a record containing a set of associated attributes. Different subsets of attributes are assigned depending on the type of knowledge the fact represents.”

Some sensors are event-driven while others poll. Event-driven sensors are useful for recognizing instantaneous events like sounds and damage. Polling works better for sensors that need to extract information from the world.”

Sensors deposit perceptions in working memory, providing a constant stream of up-to-date data. References allow you to ‘pass forward’ an effect from one action into the preconditions of subsequent actions, even if the actual value is only determined at runtime.”

Garbage Collection and Expiration of Facts
   • Implement garbage collection or expiration for WorkingMemoryFacts to prevent indefinite accumulation
   • Add ability for sensors to remove or mark facts as invalid once handled
   • Support time-based expiration of temporary facts
   • Include a robust expiration and GC system

Complex Sensor Update Policies  
   • Support sensors that update at different rates
   • Allow limiting to one high-cost sensor per frame
   • Include both event-driven sensors (e.g. hearing gunshots) and polling sensors
   • Add "did_significant_work" Boolean returns to throttle sensor usage
   • Support distributed processing of sensor updates

Sensors are computational units that perceive or compute data. They store results in Fact objects, which are appended to the Automaton’s working_memory. The Fact object is minimal containing:

    Fact(sensor: str, data: SensorResponse, binding: str)
      – sensor: which sensor produced it
      – data: the SensorResponse
      – binding: the key used to write into the WorldState

After each sensor update, the Automaton writes Fact.data.response into the corresponding key in WorldState. By distributing heavy computations across sensors (e.g., pathfinding or line-of-sight tests), the code ensures the planner’s overhead is minimized at plan time.

Fact Confidence Management
    • Use confidence values to remove stale facts
    • Implement confidence decay over time
    • Support actions with confidence thresholds (e.g. requiring > 0.7)
    • Include logic for discarding/ignoring low confidence facts
    • Track fact age and elapsed time

SENSORS AND WORKING MEMORYFACTS

STATE MACHINE (METHODICALMACHINE) AND THE AUTOMATON

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

A) The Automaton:  
   class Automaton:  
     – Has the following states using MethodicalMachine:  
       1) waiting_orders (initial)  
       2) sensing  
       3) planning  
       4) acting  
     – Input transitions (wait, sense, plan, act, input_goal).  
     – Output methods that do the actual sensor reading, plan building, and plan execution.  
     – Internal references:  
       • world_state (a WorldState)  
       • working_memory (list of Fact)  
       • sensors (Sensors)  
       • actions (Actions)  
       • planner (Planner)  
       • action_plan (list)  
       • goal (dict)  
       • actions_response (list of ActionResponse)  

B) State Machine Transitions:  
   1) waiting_orders → sense -> sensing  
      – calls __sense: runs sensors, appends Facts to working_memory, writes results to world_state.  
   2) sensing → plan -> planning  
      – calls __plan: uses self.planner.plan(...) to create edges representing a plan.  
   3) planning → act -> acting  
      – calls __act: iterates the plan edges, calling Action.exec on each.  
   4) acting → sense -> sensing  
      – calls __reset_working_memory and then __sense again.  
   5) waiting_orders, planning, and acting all also have input_goal, returning to waiting_orders after setting a new goal.  
   6) sensing can also go back to waiting_orders by the input “wait,” which resets working_memory.

PUTTING IT ALL TOGETHER (AUTOMATONCONTROLLER)

State Machine Cycle
   • Implement a finite-state machine (e.g. waiting_orders → sensing → planning → acting) with transitions driven by sensors and goals
   • Use an explicit state machine (like MethodicalMachine) with transitions that handle mid-plan interruptions and new goals
   • Support full "sense → plan → act" sequence with proper state management

class AutomatonController:  
• Holds an Automaton instance.  
• Provides high-level control with start(), which loops:  
  1) automaton.sense()  
  2) if world_state != goal:  
       – automaton.plan()  
       – automaton.act()  
     else:  
       – automaton.wait()  
  3) sleep(5)

VISUALIZING THE PLAN (OPTIONAL UTILITY)
Optionally, define a function visualise_plan(plan, filename) that uses networkx and matplotlib to draw the plan steps as nodes with edges in order:
    def visualise_plan(plan, filename):
        graph = DiGraph()
        ...
        plt.savefig(filename)
        plt.close()
necessary for the core planner, but if you do include it, replicate the approach of:  
1) Creating a DiGraph.  
2) Adding each plan step as a node.  
3) Adding edges from step to next step.  
4) Drawing with networkx, saving to an image file.

EXAMPLE MAIN FUNCTION AND EXECUTION FLOW

The example main() performs:

def main():  
  goal = {"tmp_dir_state": "exist", "tmp_dir_content": "token_found"}  
  dir_handler = setup_automaton()  
  dir_handler.goal = goal  
  dir_handler.start()

Where setup_automaton() builds an AutomatonController with initial world_state, sets up two sensors (SenseTmpDirState, SenseTmpDirContent) and two actions (CreateTmpDir, CreateToken).

Runtime Flow:  
1) The controller starts in an infinite loop.  
2) The Automaton’s “sense” transition is called. Both sensors run shell commands to see if /tmp/goap_tmp exists and if .token is there. The results are appended as Facts to working_memory, then written to the Automaton’s WorldState.  
3) If the current state does not match the goal, the controller triggers “plan.” The planner constructs a path from current state to goal by chaining the needed actions.  
4) Then “act” executes those actions in order (CreateTmpDir → CreateToken).  
5) After acting, the system goes back to sensing again. Next iteration, once the system sees that “tmp_dir_state=exist” and “tmp_dir_content=token_found,” it matches the goal, so the controller calls “wait” and repeats.

ShellCommand is a helper:

class ShellCommand:  
  – constructor: ShellCommand(command: str, timeout: int=30)  
  – callable: run this shell command, capturing stdout, stderr, and return_code.

In the example:  
• "mkdir -p /tmp/goap_tmp" (to create a directory)  
• "touch /tmp/goap_tmp/.token" (to place a file)  
• Some read commands to check if directory exists or if a file is present.  

These shell commands are used by sensors (to sense "tmp_dir_state" or "tmp_dir_content") and by actions (to create the directory or token).

EXAMPLE USAGE AND EXPECTED BEHAVIOR
Below is a minimal example demonstrating how your final system should be used:

Example 1: Flipping tables and taking cover (simple demonstration)
------------------------------------------------------------------

    # 1) Define your actions
    class FlipTable(Action):
        effects = {
            "table_id": ...  # Provides a table ID
        }
        preconditions = {
            "has_table": True
        }
    
    class TakeCoverBehindTable(Action):
        effects = {
            "is_in_cover": True
        }
        preconditions = {
            "table_to_hide_behind": reference("table_id")
        }

    # 2) Define your initial world_state and goal_state
    world_state = {
        "has_table": True,
        ...
    }
    goal_state = {
        "is_in_cover": True
    }

    # 3) Run the planner
    actions = [FlipTable(), TakeCoverBehindTable()]
    planner = RegressivePlanner(world_state, actions)
    plan = planner.find_plan(goal_state)

    # 4) Evaluate the plan steps
    for step in plan:
        print(step)

You should see steps that indicate that the “FlipTable” must occur (yielding table_id) before “TakeCoverBehindTable” can be satisfied.

Example 2: Handoff of references  
--------------------------------
(Provided in the original code snippet, see “HauntWithMagic,” “PerformMagic,” etc.)

    class HauntWithMagic(Action):
        effects = {"is_spooky": True}
        preconditions = {"is_undead": True, "performs_magic": "abracadabra"}

    class BecomeUndead(Action):
        effects = {"is_undead": True}
        preconditions = {"is_undead": False}

    class PerformMagic(Action):
        effects = {"performs_magic": ...}
        preconditions = {
            "chant_incantation": reference("performs_magic"),
            "cast_spell": reference("performs_magic")
        }

    class ChantIncantation(Action):
        effects = {"chant_incantation": ...}
        preconditions = {}

    class CastSpell(Action):
        effects = {"cast_spell": ...}
        preconditions = {}

    world_state = {"is_spooky": False, "is_undead": False}
    goal_state = {"is_spooky": True}
    actions = [HauntWithMagic(), BecomeUndead(), PerformMagic(), ChantIncantation(), CastSpell()]
    planner = RegressivePlanner(world_state, actions)
    plan = planner.find_plan(goal_state)
    for step in plan:
        print(step)

EXPECTED OUTPUT:  
The system automatically inserts “ChantIncantation” and “CastSpell” to produce the required references for “PerformMagic,” which in turn satisfies “performs_magic” = “abracadabra” for “HauntWithMagic.” The plan must also satisfy “BecomeUndead” because “HauntWithMagic” requires “is_undead = True.”

FIVE DISTINCT SCENARIOS THAT USE REFERENCES (OPTIONAL)  
“Below are five hypothetical or illustrative usage scenarios that demonstrate how you can harness references in actions. These scenarios do not include the chanting example from the code snippet—thus giving fresh, concrete insight into references. For instance, passing a tool ID, flipping a table for cover, picking up a key to unlock a door, linking a generated power-on state, or using a repaired bridge to cross a river.”

Advanced Scenarios
   • Support complex sensor tasks like NodeCombatSensors for tactical positions
   • Handle Disturbance facts appropriately
   • Enable behaviors like "create multiple paths", "crouch in place", "search safe route"
   • Support rich variety of scenarios and actions

WORLDSTATE AND BLACKBOARD-LIKE INTEGRATION

REFERENCES  
• A reference object (EffectReference) is used in an action’s preconditions to denote that the real value is supplied by the respective effect from another action.  
• If an action’s effect is { "someID": ... }, it indicates “I will produce a ‘someID’ once executed, but its actual data field is determined dynamically.”  
• Another action’s precondition can specify { "neededID": reference("someID") }, linking that precondition to the specific runtime value provided by the prior action.  
• The planner unifies this link during regressive search, ensuring that any unsatisfied reference is matched by an appropriate effect from a preceding action in the plan.

The system must support referencing the effects of actions, meaning that an action’s preconditions can use dynamic data produced by another action’s effect.”

By linking the preconditions of one action to the effects of another, GOAP automatically ‘chains’ them into a valid plan, letting the system replan as needed, avoiding hand-crafted transitions between complex behaviors.”

The system must support references—i.e., dynamic data passed from one action’s effect into the preconditions of subsequent actions—even if the actual value is only determined at runtime. By defining simple, isolated actions—and letting the system figure out the chain of dependencies—you can rapidly prototype sophisticated behaviors that respond to emergent gameplay changes.”
“This specification describes a specialized Goal-Oriented Action Planning (GOAP) system that incorporates sensors and working memory, and a state machine to distribute computation and drive AI behavior in real time. Implement the entire code architecture described here to replicate the system exactly, meaning that if you omit any details, the implementation will not be able to replicate the original system.”

Blackboard-Like Subsystems
   • Implement subsystems (navigation, animation, aiming) that read from a blackboard
   • Support subsystem concurrency
   • Include logic for converting commands into movement/animations
   • Enable proper subsystem integration with GOAP actions

The agent architecture is similar to the MIT Media Lab’s C4 notion of using a blackboard, working memory, sensors, and multiple subsystems. In this system:

• Sensors detect changes in the environment (or internal states) and store perceptions in working memory.  
• The planner uses these perceptions to guide decision making, formulating a plan of actions to satisfy the current goal.  
• Actions, when executed, write instructions (e.g., new destinations) to a blackboard-like data storage (here represented by a WorldState plus the Automaton’s internal structures). Other subsystems (navigation, animation, combat, etc.) update accordingly.  

One of the key points is to distribute potentially costly computations over many sensor updates, caching partial results in working memory. The planner references these cached values when validating preconditions.

The WorldState class acts as the blackboard storing the symbolic representation of the environment. The Automaton references it for the current state; sensors and actions update or read from it.  
• Accessing world_state.tmp_dir_state is syntactic sugar for world_state["tmp_dir_state"].  

Working memory is stored as a list of Fact objects in the Automaton. Once the Automaton calls sensors, each sensor result is turned into a Fact and appended to working_memory. The binding determines which key in world_state to set with fact.data.response.

Multiple Reference Linkage
   • Support reference chains through multiple actions
   • Enable complex scenarios like "PickUpKey → UseKeyOnDoor"
   • Allow deep reference chaining across many steps
   • Support branching reference paths

Additional requirements for a complete GOAP+Sensors implementation based on the specifications:

PLANNER AND ACTION MECHANICS

EXAMPLE SHELL COMMAND USAGE

SPECIFICATION FOR A GOAP SYSTEM WITH SENSORS AND WORKING MEMORY

INTRODUCTION  
This specification describes a specialized Goal-Oriented Action Planning (GOAP) system that incorporates sensors, working memory, and a state machine to distribute computation and drive AI behavior in real time. Implement the entire code architecture described here to replicate the system exactly.

CONTENTS  
1. Overview of the Agent Architecture  
2. Required Classes, Interfaces, and Data Structures  
3. Sensors and Workings of WorkingMemoryFacts  
4. Planner and Action Mechanics  
5. WorldState and Blackboard-like Integration  
6. State Machine (MethodicalMachine) and the Automaton  
7. Putting it All Together (AutomatonController)  
8. Example Shell Command Usage  
9. Example Main Function and Execution Flow  
10. Implementation Checklist

CONCLUSION  
“By defining both a planning system with references and a consistent sensor/working memory approach, we can dynamically pass data between actions and store relevant facts. The GOAP planner automatically figures out an optimal path (a plan) of actions that achieves the desired goal at runtime. This dynamic approach shines when the environment changes unexpectedly—GOAP can replan as needed, avoiding hand-crafted transitions between complex behaviors.”

Context Effect Functions
   • Implement "context effect" code that runs after actions complete
   • Support post-execution functions that can modify facts in working memory
   • Allow actions to have both precondition checks and post-execution effects

Your implementation must define exactly the following classes (with the described methods and constructor parameters), ensuring you replicate the functionality in full detail. The associated file-level imports, exception handling, and usage of Python standard library or side libraries (like networkx, methodicalmachine) should be included accordingly.

A) Exceptions  
Define these exceptions as is:

• OperationFailedError(reason: str)  
  Indicates a high-level failure in an operation.

• SensorError (base class for sensor-related issues). Under it:  
  – SensorMultipleTypeError  
  – SensorDoesNotExistError  
  – SensorAlreadyInCollectionError  

• PlanError (base class for planning issues). Under it:  
  – PlanFailed  

• ActionError (base class for action-related issues). Under it:  
  – ActionMultipleTypeError  
  – ActionAlreadyInCollectionError  

B) Action, ActionResponse, and Actions Collection

1) Action  
   class Action:  
       • constructor:  
         def __init__(self, func: Callable, name: str, conditions: dict, effects: dict, cost: float = 0.1)  
         – func: A callable containing the “execution logic” for the action.  
         – name: A unique string ID for the action.  
         – conditions: dict specifying symbolic conditions required to run (e.g., {"tmp_dir_state": "exist"}).  
         – effects: dict specifying which symbolic changes occur after completion.  
         – cost: numeric value representing cost in planning.  
       • exec(): runs self.func and returns an ActionResponse.  
       • response: property storing the last ActionResponse from exec().  

2) ActionResponse  
   class ActionResponse:  
       – holds stdout, stderr, return_code, plus a string property response returning stdout if available, else stderr.  

3) Actions (a collection of Action)  
   class Actions:  
       – holds a list of Action objects.  
       – add(name, conditions, effects, func, cost=0.1): adds a new Action. Raises ActionAlreadyInCollectionError if name duplicates.  
       – remove(name): removes an Action by name.  
       – get(name): returns the Action instance or None.  
       – run_all(): iterates all actions in the collection, calling exec.  

C) Graph Construction Data Structures (Node, Edge, Nodes, Edges, Graph)

1) Node(attributes: dict, weight: float=0.0)  
   – A node identified by a dict of attributes (the “symbolic world state” it represents).  

2) Edge(name, predecessor: Node, successor: Node, cost=0.0, obj: object=None)  
   – Connects two Nodes in a directed manner, labeled with “name,” holding a reference to an Action (obj).  

3) Nodes and Edges Collections  
   class Nodes: keeps a list of Node objects with helper methods (add, get, iteration).  
   class Edges: keeps a list of Edge objects with helper methods (add, iteration).  

4) Graph  
   – Must be built on networkx.DiGraph.  
   – add_nodes_from(nodes: Nodes) and add_edges_from(edges: Edges).  
   – path(src: Node, dst: Node): uses networkx’s astar_path to find a path.  
   – edge_between_nodes(path, data=True): returns the edges for a path.  

D) Planner  
   class Planner:  
       – constructor: Planner(actions: Actions)  
       – plan(state: dict, goal: dict) -> list of edges  
         1) Generate states from actions, the initial “world_state,” and the “goal.”  
         2) Generate transitions where each action’s conditions match a Node’s attributes.  
         3) Build a Graph and search from the initial Node to the goal Node with astar_path.  
         4) Return the path as a list of edges (the plan).  

E) Sensor, SensorResponse, and Sensors Collection

1) Sensor  
   class Sensor:  
       – constructor: Sensor(name: str, binding: str, func: Callable)  
         * name: unique ID  
         * binding: string key referencing where the sensor’s data is stored in working memory or the world state  
         * func: the callable that does the detection or computation  
       – exec(): calls func() and returns a SensorResponse  
       – The sensor sets self.response to the SensorResponse.  

2) SensorResponse  
   class SensorResponse:  
       – holds stdout, stderr, return_code, plus a property response that returns stdout if present, otherwise stderr.  

3) Sensors (a collection of Sensor)  
   class Sensors:  
       – add(name, binding, func): add a new unique sensor.  
       – remove(name)  
       – run_all(): calls exec on each sensor.  

F) WorldState  
   class WorldState(dict):  
       – A specialized dictionary with attribute-style access (ws.attr -> ws["attr"]).  
       – Must override __setitem__, __delitem__, __eq__, etc.  
       – The code holds usage akin to a blackboard or set of “symbols.”  

G) Fact  
   class Fact:  
       – constructor: Fact(sensor, data, binding) - holds a reference to the sensor name, the data, and the binding.  
       – each Fact is appended to the Automaton’s working_memory list.

The implementation must include all these components working together:
• A complete regressive GOAP planner with references
• A robust sensor-driven working-memory system
• Full state machine management
• Proper fact lifecycle handling
• Rich action and scenario support

REQUIRED CLASSES, INTERFACES, AND DATA STRUCTURES

IMPLEMENTATION CHECKLIST  
• Implement a memory structure that can add, remove, and query facts by type.  
• Create multiple sensors, each with a sense method that writes one or more facts (with confidence) into memory.  
• Define Action classes that store preconditions, effects, references, cost, plus a method for context-based checks of working memory.  
• Implement the planning algorithm (e.g., an A* regressive search) that links actions by matching preconditions to effects, resolving references.  
• Ensure each action can run an execute(...) method that updates the world state (or triggers real game logic).  
• Include a cycle (or loop) that (1) triggers sensors to update memory, (2) attempts to plan a route from current world state to a specified goal, and (3) executes that plan step by step.

IMPLEMENTATION CHECKLIST

The Planner implements a regressive search approach using a custom Graph:

• __generate_states: For each Action, create a Node for the pre-state based on (world_state + action.conditions) and a Node for the post-state based on (pre-state + action.effects).  
• __generate_transitions: For each Node that satisfies Action’s conditions, create an Edge to a Node that includes the Action’s effects.  
• plan(state, goal) => a list of edges:  
  – Build the states, transitions, construct a Graph.  
  – Use networkx.astar_path(...) to find a path from the Node matching “state” to the Node matching “goal.”  
  – Return the edges along that path.  

Each Action has conditions and effects, plus a cost. The search cost is the sum of Edge costs when building a solution path.

OVERVIEW OF THE AGENT ARCHITECTURE