#!/usr/bin/env python3

"""

OVERALL ARCHITECTURE  
• The system is built around a Goal-Oriented Action Planning (GOAP) model, where an AI agent decides how to achieve a desired goal by formulating a sequence of actions at runtime.  
• The planner uses regressive search from the goal to the initial state, linking preconditions and effects.  
• Sensors provide up-to-date information about the world. Their collected data is stored in working memory as “facts.”  
• The planner uses both symbolic world-state checks and these sensor-produced facts to determine whether each action’s preconditions are satisfied.  
• References allow dynamic data flowing from one action’s effect to another action’s precondition, without hardcoding the actual value until runtime.

TERMINOLOGY AND HIGH-LEVEL STRUCTURE  
“An agent develops a plan in real time by supplying a goal to satisfy a planner. The GOAP planner looks at an action’s preconditions and effects in order to determine a queue of actions to satisfy the goal. For a full deep dive into the code itself, please refer to the listing provided in this post’s code blocks.”

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

REQUIRED DATA STRUCTURES AND TYPES  
“A set of possible goals (conditions to fulfill), a set of actions (each with preconditions and effects), a world state (the environment and the agent’s own data), sensors that detect changes in the world, and a working memory storing perceptions in a consistent format. Facts could be hashed into bins based on the type of knowledge, or sorted in some manner.”

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

HOW REFERENCES WORK (EffectReference, reference(..))  
“References allow you to ‘pass forward’ an effect from one action into the preconditions of subsequent actions, even if the actual value is only determined at runtime. This is done via class EffectReference: A small class that annotates a requested effect name—and def reference(name: str): A convenience function that returns an EffectReference referencing that name.”
“For instance, if Action A has effects = { "tool_id": ... }, it means ‘I will provide a tool_id (but we’ll only know the real value at runtime).’ Another action B can specify preconditions = { "required_tool_id": reference("tool_id") }, meaning ‘I depend on the tool_id that was created or identified by the earlier action.’”

REFERENCES  
• A reference object (EffectReference) is used in an action’s preconditions to denote that the real value is supplied by the respective effect from another action.  
• If an action’s effect is { "someID": ... }, it indicates “I will produce a ‘someID’ once executed, but its actual data field is determined dynamically.”  
• Another action’s precondition can specify { "neededID": reference("someID") }, linking that precondition to the specific runtime value provided by the prior action.  
• The planner unifies this link during regressive search, ensuring that any unsatisfied reference is matched by an appropriate effect from a preceding action in the plan.

The system must support referencing the effects of actions, meaning that an action’s preconditions can use dynamic data produced by another action’s effect.”

By linking the preconditions of one action to the effects of another, GOAP automatically ‘chains’ them into a valid plan, letting the system replan as needed, avoiding hand-crafted transitions between complex behaviors.”

The system must support references—i.e., dynamic data passed from one action’s effect into the preconditions of subsequent actions—even if the actual value is only determined at runtime. By defining simple, isolated actions—and letting the system figure out the chain of dependencies—you can rapidly prototype sophisticated behaviors that respond to emergent gameplay changes.”
“This specification describes a specialized Goal-Oriented Action Planning (GOAP) system that incorporates sensors and working memory, and a state machine to distribute computation and drive AI behavior in real time. Implement the entire code architecture described here to replicate the system exactly, meaning that if you omit any details, the implementation will not be able to replicate the original system.”

PLANNING ALGORITHM  
• Implement a regressive search (A* or BFS-based) from the goal state.  
• Whenever the search needs to satisfy a precondition key, it looks for an action whose effect matches that key (including referencing).  
• For referencing scenarios, if the effect is Ellipsis or a dynamic placeholder, the planner pairs it with that precondition, unifying the two so that the final plan has a consistent flow of data.  
• Cost accumulation is performed by summing each chosen action’s cost. The plan with the lowest total cost is selected.  
• During plan assembly, some additional “context preconditions” can consult working memory. For example, if an action requires “EnemyVisible,” it checks if the memory has a fact type “EnemyLocation” with high confidence.

FIVE DISTINCT SCENARIOS THAT USE REFERENCES (OPTIONAL)  
“Below are five hypothetical or illustrative usage scenarios that demonstrate how you can harness references in actions. These scenarios do not include the chanting example from the code snippet—thus giving fresh, concrete insight into references. For instance, passing a tool ID, flipping a table for cover, picking up a key to unlock a door, linking a generated power-on state, or using a repaired bridge to cross a river.”

IMPLEMENTATION CHECKLIST  
• Implement a memory structure that can add, remove, and query facts by type.  
• Create multiple sensors, each with a sense method that writes one or more facts (with confidence) into memory.  
• Define Action classes that store preconditions, effects, references, cost, plus a method for context-based checks of working memory.  
• Implement the planning algorithm (e.g., an A* regressive search) that links actions by matching preconditions to effects, resolving references.  
• Ensure each action can run an execute(...) method that updates the world state (or triggers real game logic).  
• Include a cycle (or loop) that (1) triggers sensors to update memory, (2) attempts to plan a route from current world state to a specified goal, and (3) executes that plan step by step.

CONCLUSION  
“By defining both a planning system with references and a consistent sensor/working memory approach, we can dynamically pass data between actions and store relevant facts. The GOAP planner automatically figures out an optimal path (a plan) of actions that achieves the desired goal at runtime. This dynamic approach shines when the environment changes unexpectedly—GOAP can replan as needed, avoiding hand-crafted transitions between complex behaviors.”

GOAP System with References, Sensors, and Working Memory

This single file combines:
• A regressive GOAP planner (with references in preconditions/effects)
• A sensor-driven working-memory mechanism
• An example scenario where an NPC sees a table, flips it, and takes cover.

To run:
  1) Place this file (goap_with_sensors.py) somewhere.
  2) Run "python goap_with_sensors.py".
  3) See console output illustrating the sense-plan-act cycle.

Here are several features that appear in the other sample GOAP+Sensors codebases or specifications but are missing or only partially present in your combined implementation. You’ll see these elements discussed in the references/examples you provided but not fully carried over:

1) “State Machine” or Automaton Cycle  
   • Some examples use a 3- or 4-state finite-state machine (e.g. waiting_orders → sensing → planning → acting) with transitions driven by sensors and goals. In your code, you do perform a “sense → plan → act” sequence, but you do not implement an explicit state machine (like MethodicalMachine) or transitions that handle mid-plan interruptions or new goals.

2) Garbage Collection and Expiration of Facts  
   • Other specs point out that WorkingMemoryFacts can accumulate indefinitely, creating a need for garbage collection or expiration. For instance, sensors that deposit “temporary disturbance facts” should remove or mark them invalid once they are handled, or after a time-out. In your code, you clear memory in sense_phase() just for the demo, but do not implement a robust expiration or GC system.

3) More Complex Sensor Update Policies  
   • The distributed processing architecture in the detailed text recommends sensors that update at different rates or only one high-cost sensor per frame. Some sensors are event-driven (like hearing a gunshot) and others poll every N frames. Your code calls each sensor every “sense_phase” equally, but omits the idea of limiting expensive sensors or returning a “did_significant_work” Boolean to throttle sensor usage.

4) Context Effect Functions  
   • In some specs, actions can also have “context effect” code that runs after the action completes. You do have check_context_precondition(...) but do not demonstrate any separate post-execution “context effect function” that might, for example, remove or modify facts in working memory once an action concludes.

5) Enumerated Symbol Arrays  
   • The working “symbolic representation” in some references is stored in a fixed-size array (one entry per enumerated symbol). That approach ignites fast hashing/lookup and is mentionned as a key optimization in certain references. Your code uses a dictionary-based approach. That is fine, but it differs from the enumerated, fixed-size scheme highlighted in the “symbolic states” portion.

6) Full A* With Heuristics and Cost Summation  
   • The specification often calls for “regressive GOAP with A*,” summing costs and using a heuristic. In your code, you call it RegressiveGOAPAStarSearch but effectively do a breadth-first expansion (no real heuristic or cost-based prioritization). It works, but is missing the usual “close to goal → lower h()” or “lowest total cost so far → expand first” logic that true A* would do.

7) Multiple Reference Linkage Examples (Beyond Two Steps)  
   • References can chain through multiple actions, e.g., “PickUpKey → UseKeyOnDoor,” “CraftMaterial → UseMaterialToCook → DeliverCookedItem,” or “FlipMultipleTables.” The specs (and the five example scenarios) show deeper reference chaining. Your example only demonstrates a single reference scenario (FlipTableAction → TakeCoverAction). It works for a simple chain but doesn’t show the more advanced multi-step references found in the original references.

8) Blackboard-Like Subsystems and Subsystem Instructions  
   • Some references describe “subsystems” (navigation, animation, aiming) that read orders from a blackboard. Your code modifies world_state but does not show any subsystem concurrency or how blackboard commands get turned into movement or animations. That subsystem-based approach is more about hooking GOAP actions into the rest of the AI; you have the skeleton, but not the subsystem logic.

9) Advanced Scenarios and Variation  
   • The earlier specs included advanced sensor tasks (like NodeCombatSensors that gather tactical positions, or handling Disturbance facts). Your example sensors are quite simple (TableSensor, EnemySensor). The “create multiple paths,” “crouch in place,” “search for a safe route” behaviors are absent.

10) Fact Confidence-Based Preconditions or Removal  
   • In your code, you populate a confidence float but do not use it to remove stale facts or reduce their confidence over time. Nor do you show an action that requires, say, confidence > 0.7 to proceed. The references highlight the possibility of discarding or ignoring facts if confidence is too low or if enough time has elapsed.

In short, you have done a good job demonstrating a basic combined approach—sensors deposit facts into working memory, and a regressive planner uses references in preconditions/effects. However, the aspects above (state-machine-driven cycles, garbage collection, cost-heuristic planning, multiple chaining references, blackboard subsystems, more nuanced sensor update rules) are present in the larger examples but not fully implemented in your version.


"""

import time
from collections import defaultdict, deque
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple

###############################################################################
# 1) COMMON DATA TYPES AND UTILITY
###############################################################################

State = Dict[str, Any]

class EffectReference:
    """
    A reference placeholder for data provided by an action's effect,
    passed dynamically into a subsequent action's precondition.
    """
    def __init__(self, name: str):
        self.goap_effect_reference = name

def reference(name: str) -> EffectReference:
    """Returns an EffectReference for chaining data between actions."""
    return EffectReference(name)

###############################################################################
# 2) WORKING MEMORY AND FACTS
###############################################################################

class WorkingMemoryFact:
    """
    Holds arbitrary knowledge attributes plus confidence values.
    For demonstration, we'll track a 'data' field and a float 'confidence'.
    """
    def __init__(self, fact_type: str, data: Any, confidence: float):
        self.fact_type = fact_type
        self.data = data
        self.confidence = confidence

    def __repr__(self):
        return f"<Fact type={self.fact_type}, data={self.data}, conf={self.confidence}>"

class WorkingMemory:
    """
    A collection of WorkingMemoryFact.
    Sensors deposit facts here, planner or AI may remove or query them.
    """
    def __init__(self):
        self.facts: List[WorkingMemoryFact] = []

    def add_fact(self, fact: WorkingMemoryFact):
        self.facts.append(fact)

    def remove_fact(self, fact: WorkingMemoryFact):
        if fact in self.facts:
            self.facts.remove(fact)

    def query_facts(self, fact_type: str) -> List[WorkingMemoryFact]:
        return [f for f in self.facts if f.fact_type == fact_type]

###############################################################################
# 3) SENSORS
###############################################################################

class Sensor(ABC):
    """
    A sensor that, when updated, produces working memory facts.
    Subclass or implement 'sense()' for real logic.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def sense(self, memory: WorkingMemory, world_state: State) -> None:
        """
        Called each 'sense' cycle. Implementation should add or update
        relevant facts in 'memory'. Any real environment checks or computations
        should happen here.
        """
        pass

class TableSensor(Sensor):
    """
    Example sensor that checks if there is a table in the environment.
    If so, creates a fact "table_available" with some confidence.
    """
    def sense(self, memory: WorkingMemory, world_state: State) -> None:
        # For demonstration, we'll say if world_state["see_table"] is True,
        # we place a "table_available" fact in memory with confidence=1.0
        if world_state.get("see_table") is True:
            fact = WorkingMemoryFact(
                fact_type="table_available",
                data={"table_id": 123},
                confidence=1.0
            )
            memory.add_fact(fact)

class EnemySensor(Sensor):
    """
    Sensor that checks if an enemy is present.
    If yes, store an "enemy_visible" fact with confidence.
    """
    def sense(self, memory: WorkingMemory, world_state: State) -> None:
        # If world_state says there's an enemy, we create a fact.
        enemy_seen = world_state.get("enemy_detected", False)
        if enemy_seen:
            memory.add_fact(WorkingMemoryFact(
                fact_type="enemy_visible",
                data={"enemy_id": 777},
                confidence=0.9
            ))

###############################################################################
# 4) ACTIONS AND REFERENCES
###############################################################################

class Action(ABC):
    """
    A GOAP action with:
      - preconditions: a dictionary or references that must match the world state
      - effects: changes the action applies
      - cost: numeric cost for the planner
    """
    cost = 1.0

    def __init__(self, name: str, preconditions: Dict[str, Any], effects: Dict[str, Any], cost: float = 1.0):
        self.name = name
        self.preconditions = preconditions   # e.g. { "has_table": True, "table_id": reference("table_id") }
        self.effects = effects               # e.g. { "is_in_cover": True }
        self.cost = cost

    def __repr__(self):
        return f"<Action {self.name}>"

    @abstractmethod
    def check_context_precondition(self, memory: WorkingMemory, world_state: State) -> bool:
        """
        Optional code-based check to see if the action is valid given working memory.
        E.g. we might check if there's a 'table_available' fact with confidence > 0.5
        """
        pass

    @abstractmethod
    def execute(self, world_state: State, memory: WorkingMemory) -> None:
        """
        Called during plan execution. Implementation sets or modifies
        items in world_state. Possibly interacts with subsystems, etc.
        """
        pass

class FlipTableAction(Action):
    """
    Flip a table to create cover. 
    Produces an effect of providing "flipped_table_id".
    """
    def __init__(self):
        super().__init__(
            name="FlipTable",
            preconditions={"table_detected": True},  # requires table_detected == True
            effects={"flipped_table_id": ...},       # references a dynamic ID
            cost=2.0
        )

    def check_context_precondition(self, memory: WorkingMemory, world_state: State) -> bool:
        # We want to confirm there's a table_available fact in memory with > 0.5 confidence
        facts = memory.query_facts("table_available")
        has_table_fact = any(fact.confidence > 0.5 for fact in facts)
        return has_table_fact

    def execute(self, world_state: State, memory: WorkingMemory) -> None:
        # We'll get the actual table ID from memory (just pick the first fact)
        facts = memory.query_facts("table_available")
        if facts:
            table_id = facts[0].data["table_id"]
            # We'll store it in world_state as if we have "flipped_table_id"
            # The effect was "flipped_table_id": ...
            # The planner sees that we produce "flipped_table_id"
            # so we store that actual ID:
            world_state["flipped_table_id"] = table_id
            print(f"[FlipTableAction] Table {table_id} flipped!")

class TakeCoverAction(Action):
    """
    Requires a flipped_table_id reference. 
    Achieves "is_in_cover" == True.
    """
    def __init__(self):
        super().__init__(
            name="TakeCover",
            preconditions={
                "table_detected": True,
                "table_to_hide_behind": reference("flipped_table_id")
            },
            effects={"is_in_cover": True},
            cost=1.0
        )

    def check_context_precondition(self, memory: WorkingMemory, world_state: State) -> bool:
        # We'll also require that there's an "enemy_visible" fact if we want to bother taking cover
        facts = memory.query_facts("enemy_visible")
        return len(facts) > 0

    def execute(self, world_state: State, memory: WorkingMemory) -> None:
        tbl_id = world_state.get("flipped_table_id", None)
        if tbl_id is not None:
            world_state["is_in_cover"] = True
            print(f"[TakeCoverAction] Taking cover behind flipped table {tbl_id}.")

###############################################################################
# 5) REGRESSIVE GOAP PLANNER (A* SEARCH)
###############################################################################

class RegressiveGOAPAStarNode:
    """
    Node in the search - storing current 'state' + how we got it (the action).
    In a regressive approach, 'goal_state' is what's needed at this node,
    and 'current_state' is partial or intermediate states.
    """
    def __init__(self, current_state: State, goal_state: State, action: Optional[Action] = None):
        self.current_state = dict(current_state)
        self.goal_state = dict(goal_state)
        self.action = action

    def __hash__(self):
        # hashed by memory ID for demonstration. 
        # For serious usage, define a stable hash if states are repeated often.
        return id(self)

    @property
    def unsatisfied_keys(self) -> List[str]:
        # All keys in the goal_state that are not matching in current_state
        result = []
        for k, v in self.goal_state.items():
            if k not in self.current_state or self.current_state[k] != v:
                result.append(k)
        return result

    @property
    def is_satisfied(self) -> bool:
        return len(self.unsatisfied_keys) == 0

class RegressiveGOAPAStarSearch:
    """
    A simplified regressive A* for demonstration: 
    We'll expand from the goal, matching actions that can produce that state,
    then unify with current state to see if we have a solution.
    """

    def __init__(self, actions: List[Action], memory: WorkingMemory):
        self.actions = actions
        self.memory = memory

        # Pre-build an effect->actions mapping for quick lookup
        # to see which actions can fulfill each effect key
        self.effect_table = defaultdict(list)
        for action in actions:
            for ekey in action.effects.keys():
                self.effect_table[ekey].append(action)

    def find_plan(self, start_state: State, goal_state: State) -> List[Action]:
        """
        Return a list of actions from start->goal with minimal cost (not strictly
        guaranteed in this simple example).
        """
        # We'll do a BFS or D' BFS in regressive manner for simplicity,
        # ignoring advanced heuristics. 
        start_node = RegressiveGOAPAStarNode(start_state, goal_state, None)
        frontier = deque([start_node])
        came_from = {}

        while frontier:
            node = frontier.popleft()

            # If node is satisfied, we found a path. Reconstruct
            if node.is_satisfied:
                return self._reconstruct_plan(node, came_from)

            # Expand: for each unsatisfied key, see which actions produce it
            for key in node.unsatisfied_keys:
                # The goal_value we want is node.goal_state[key]
                wanted_val = node.goal_state[key]

                # Find an action that yields that effect
                for candidate in self.effect_table[key]:
                    effect_val = candidate.effects[key]

                    # If effect_val == wanted_val or is Ellipsis (reference):
                    if effect_val == wanted_val or effect_val is Ellipsis:
                        # Also check context preconditions
                        if not candidate.check_context_precondition(self.memory, node.current_state):
                            continue

                        # Construct a new node
                        new_goal_state = dict(node.goal_state)
                        new_current = dict(node.current_state)

                        # Because we do regressive, we unify the preconditions into the new goal
                        # Also unify references if needed
                        for prec_key, prec_val in candidate.preconditions.items():
                            if isinstance(prec_val, EffectReference):
                                # Means we reference e.g. "flipped_table_id"
                                # We'll unify it with node.current_state or something
                                ref_name = prec_val.goap_effect_reference
                                # If the action also produces that effect, we unify from that
                                # For demonstration, we do a simple approach
                                if ref_name in candidate.effects:
                                    # The effect is Ellipsis but we can unify with the wanted_val
                                    if ref_name in node.goal_state:
                                        new_goal_state[prec_key] = node.goal_state[ref_name]
                                    else:
                                        # fallback
                                        new_goal_state[prec_key] = "REFERENCE"
                                else:
                                    # fallback
                                    new_goal_state[prec_key] = "REFERENCE"
                            else:
                                new_goal_state[prec_key] = prec_val

                        # Then define the new node
                        new_node = RegressiveGOAPAStarNode(new_current, new_goal_state, candidate)
                        came_from[new_node] = node
                        frontier.append(new_node)

        return []

    def _reconstruct_plan(self, node: RegressiveGOAPAStarNode, came_from: Dict[RegressiveGOAPAStarNode, RegressiveGOAPAStarNode]) -> List[Action]:
        plan = []
        current = node
        while current in came_from:
            parent = came_from[current]
            action = current.action
            if action:
                plan.append(action)
            current = parent
        plan.reverse()
        return plan

###############################################################################
# 6) MAIN WRAPPER: SENSE -> PLAN -> ACT
###############################################################################

class GOAPAgent:
    """
    A simple agent that:
    1) Has a world_state
    2) Has working_memory + sensors
    3) Re-plans using RegressiveGOAPAStarSearch
    4) Executes the plan
    """

    def __init__(self):
        self.world_state: State = {
            "see_table": False,
            "enemy_detected": False,
            "table_detected": False,   # High-level boolean if we've recognized a table
            "is_in_cover": False
        }
        self.memory = WorkingMemory()

        # Setup some sensors:
        self.sensors = [
            TableSensor("TableSensor"),
            EnemySensor("EnemySensor")
        ]

        # Setup some actions with references
        self.actions = [
            FlipTableAction(),
            TakeCoverAction()
        ]
        self.planner = RegressiveGOAPAStarSearch(self.actions, self.memory)

        # We'll define a "goal" we want to achieve
        self.goal_state = {"is_in_cover": True}

    def sense_phase(self):
        """
        Gather data from each sensor, store as facts in working memory,
        then unify some booleans in world_state as needed
        """
        # Clear out old facts for demonstration
        self.memory.facts.clear()

        for sensor in self.sensors:
            sensor.sense(self.memory, self.world_state)

        # Example logic: if we see table_available in memory,
        # set "table_detected" in world_state to True
        table_facts = self.memory.query_facts("table_available")
        self.world_state["table_detected"] = len(table_facts) > 0

    def plan_phase(self) -> List[Action]:
        # Build a plan from current world_state to self.goal_state
        plan = self.planner.find_plan(self.world_state, self.goal_state)
        return plan

    def act_phase(self, plan: List[Action]):
        # Execute the plan in order
        for action in plan:
            # Check again if preconditions are met and context is valid
            if not action.check_context_precondition(self.memory, self.world_state):
                print(f"[act_phase] Action {action.name} no longer valid, aborting.")
                return
            # "Apply" the action
            action.execute(self.world_state, self.memory)

            # Then apply the action's (symbolic) effects to the world_state
            for k, v in action.effects.items():
                if v is Ellipsis:
                    # For reference-based effects, we assume the action
                    # has already stored the actual data (like "flipped_table_id")
                    continue
                self.world_state[k] = v

###############################################################################
# 7) DEMONSTRATION
###############################################################################

def main():
    agent = GOAPAgent()

    print("\n--- SCENARIO 1: The agent does not see a table or enemy yet ---")
    agent.sense_phase()
    plan1 = agent.plan_phase()
    print(f"Plan: {plan1}")
    agent.act_phase(plan1)
    print(f"World State after attempt: {agent.world_state}\n")

    print("--- SCENARIO 2: The agent sees a table and an enemy appears ---")
    agent.world_state["see_table"] = True
    agent.world_state["enemy_detected"] = True
    agent.sense_phase()
    plan2 = agent.plan_phase()
    print(f"Plan: {plan2}")
    agent.act_phase(plan2)
    print(f"World State after actions: {agent.world_state}\n")

    print("--- Done ---")

if __name__ == "__main__":
    main()
