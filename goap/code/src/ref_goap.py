"""
GOAP


Plan & Goal
-----------

A _plan_ is simply a sequence of actions that satisfy a _goal_ wherein the actions take the agent from a starting state to whichever state satisfies the goal.

A _goal_ is any condition that an agent wants to satisfy. In GOAP, goals simply define what conditions need to be met to satisfy the goal, the steps required to reach these satisfactory conditions are determined in real time by the GOAP planner. A goal is able to determine its current relevance and when it is satisfied.



Every agent is assigned _actions_ which are a single, atomic step within a _plan_ that makes an agent do something. Examples of an action are playing an animation, playing a sound, altering the state, picking up flowers, etc.

**Every action is encapsulated and ignorant of the others.**

Each defined action is aware of when it is valid to be executed and what its effects will be on the game world. Each action has both a _preconditions_ and _effects_ attributes which are used to chain actions into a valid _plan_. A precondition is the state required for an action to run and effects are the changes to the state after an action has executed. For example if the agent wants to harvest wheat using a scythe, it must first acquire the tool and make sure the precondition is met. Otherwise the agent harvests using its hands.

GOAP determines which action to execute by evaluating each action’s cost. The GOAP planner evaluates which sequence of actions to use by adding up the cumulative cost and selecting the sequence with lowest cost. Actions determine when to transition into and out of a state as well as what occurs in the game world due to the transition.


Goal-Oriented Action Planning (GOAP) is a flexible AI planning system that allows agents to determine their own sequence of actions in order to fulfill a desired goal. Rather than relying on a manually authored rigid behavior tree or state machine, a GOAP-based AI simply needs:  
• A set of possible goals (conditions to fulfill)  
• A set of actions (each with preconditions and effects)  
• A world state (the environment and the agent’s own data)  



The GOAP Planner
----------------

An agent develops a plan in real time by supplying a goal to satisfy a _planner_. The GOAP planner looks at an actions preconditions and effects in order to determine a queue of actions to satisfy the goal. The target goal is supplied by the agent along with the world state and a list of valid actions; This process is referred to as “formulating a plan”

If the planner is successful it returns a plan for the agent to follow. The agent executes the plan until it is completed, invalidated, or a more relevant goal is found. If at any point the goal is completed or another goal is more relevant then the character aborts the current plan and the planner formulates a new one.


The planner finds the solution by building a tree. Every time an action is applied it is removed from the list of available actions.

Dependencies 

GotoNode(TableNode)
UseObject(Table)
GotoNode(NodeCover78)
AttackFromCover()

With these pieces, the GOAP planner automatically figures out an optimal path (a plan) of actions that achieves the desired goal at runtime. This dynamic approach truly shines when the environment changes unexpectedly—GOAP can replan as needed, avoiding hand-crafted transitions between complex behaviors.

In this blog post, we’ll walk through code that demonstrates a regressive GOAP approach in Python, focusing especially on the concept of references (i.e., passing dynamic data from an action’s effect into the preconditions of subsequent actions). We will also explore five distinct scenarios of how references can be used in actions, completely separate from the “chanting” example shown in the code (to honor the requirement not to reuse that scenario).

The planner chains actions with other actions to satisfy dependencies in the form of preconditions. Some of these dependencies may originate from objects in the game world. Invisible game objects placed by designers to specify tactical positions may optionally have dependencies on other objects. For instance, an NPC needs to flip the table over before taking cover behind it. The planner handles dependencies like this by chaining additional actions. The final plan will look like this

There is no limit to the number of dependencies that can be chained. Perhaps an NPC will need to activate a generator to turn on the power before operating a crane to
drop a cargo container that he can use for cover. 

The planner must instantiate new instances of Actions when it pushes them to the list. This is because Actions contain references to specific objects (e.g., navigation nodes), and any Action may exist multiple times in one plan (and must persist for at least the duration of the acted behavior, while the AI uses its data). A newly created Action inherits contextual properties from the action or goal which depends on it (e.g., navigation nodes again).
Context preconditions (action preconditions which depend on data that is not represented in the world state) are also evaluated at this time.

Dynamic replanning could be observed by removing an item after the AI had built a plan which depended on that object. When the character arrived at its location, it would check that the item still existed. If not, the plan would be invalidated and the AI would replan using the remaining objects to satisfy the same goal.

The primary point we are trying to get across here is that with a planning system, we can just toss in goals and actions. We never have to manually specify the transitions between these behaviors. The A.I. figure out the dependencies themselves at run-time based on the goal state and the preconditions and effects of actions.



Table of Contents  
1. Overview of the GOAP Implementation  
2. The Role of Actions, Preconditions, Effects, and Planner  
3. How References Work (EffectReference, reference(..))  
4. Five Distinct Scenarios That Use References  
   4.1 Scenario 1: Passing a Flipped Table ID for Cover  
   4.2 Scenario 2: Passing a Picked-Up Key ID to Unlock a Door  
   4.3 Scenario 3: Linking a Generated Power-On State to Operate Machinery  
   4.4 Scenario 4: Passing a Craft Result as an Ingredient for Cooking  
   4.5 Scenario 5: Linking a Repaired Bridge to Cross a River  
5. Usage Examples and Putting It All Together  
6. Conclusion  

─────────────────────────────────────────────────────────────────────────────────
1. Overview of the GOAP Implementation  
─────────────────────────────────────────────────────────────────────────────────

Below is the skeleton of our code (already in place in the example) providing a “RegressivePlanner.” Rather than searching forward from the initial world state, this planner searches backward from the goal, matching actions’ effects to the goal’s requirements. Once a valid path is found, it is reversed (so that we end up with forward actions to execute).

Key Classes and Functions in This Implementation:

• Action (metaclass=ActionValidator): Defines preconditions, effects, cost, and how references are validated.  
• EffectReference / reference(name: str): Represents dynamic “pass-through” data.  
• RegressiveGOAPAStarNode: Represents a node in the search space (current_state, goal_state, and the chosen action).  
• RegressiveGOAPAStarSearch (AStarAlgorithm): Performs an A* search backward from the goal to the initial state.  
• RegressivePlanner: Orchestrates the entire search, returning a plan once found.  

For a full deep dive into the code itself, please refer to the listing provided in this post’s code blocks.

─────────────────────────────────────────────────────────────────────────────────
2. The Role of Actions, Preconditions, Effects, and Planner  
─────────────────────────────────────────────────────────────────────────────────

• Actions:  
  Each action encapsulates a single step that the agent can perform. An action has:  
  – preconditions: The state that must be true before it can run.  
  – effects: Changes to the world state once the action completes.  
  – cost: A numerical value indicating how “expensive” the action is.  

• Preconditions & Effects:  
  – If an action “HarvestWheat” needs a scythe in hand, it might have a precondition: { "has_scythe": True }. Once performed, it affects the world: { "inventory_wheat": True }.  
  – By linking preconditions of one action to effects of another, GOAP automatically “chains” them into a plan.  

• The Planner:  
  – Receives a target goal, the current world state, and a list of valid actions.  
  – Finds a minimal-cost sequence of actions that transforms the current state to match the goal’s state.  
  – If during execution something changes (e.g., an object is removed), the plan can be invalidated, and the planner will recalculate.  

─────────────────────────────────────────────────────────────────────────────────
3. How References Work (EffectReference, reference(..))  
─────────────────────────────────────────────────────────────────────────────────

References allow you to “pass forward” an effect from one action into the preconditions of subsequent actions, even if the actual value is only determined at runtime. This is done via:

• class EffectReference: A small class that annotates a requested effect name.  
• def reference(name: str): A convenience function that returns an EffectReference referencing that name.  

For instance, if Action A has effects = { "tool_id": ... }, it means “I will provide a tool_id (but we’ll only know the real value at runtime).” Another action B can specify preconditions = { "required_tool_id": reference("tool_id") }, meaning “I depend on the tool_id that was created or identified by the earlier action.”

When the planner regresses from the goal to see how to fulfill “required_tool_id,” it links to the action that claims to produce “tool_id.” The runtime or the final plan will ensure these match up properly.

─────────────────────────────────────────────────────────────────────────────────
4. Five Distinct Scenarios That Use References
─────────────────────────────────────────────────────────────────────────────────

Below are five hypothetical or illustrative usage scenarios that demonstrate how you can harness references in actions. These scenarios do not include the chanting example from the code snippet—thus giving fresh, concrete insight into references.

─────────────────────────────────────────────────────────────────────────────────
4.1 Scenario 1: Passing a Flipped Table ID for Cover  

Imagine a scenario where an NPC wants to take cover behind a table. The table must be flipped first to provide adequate cover. You also need to pass the specific (runtime) table ID from flipping the table to the “take cover” action.

--------------------------------------------------------------------------------
// Scenario 1 Example
class FlipTable(Action):
    # The actual table ID is unknown until we flip it at runtime.
    effects = {
        "table_id": ...  # The ... indicates we provide a service: the actual table ID
    }
    preconditions = {
        "has_table": True  # We must have a table to flip
    }

class TakeCoverBehindTable(Action):
    effects = {
        "is_in_cover": True
    }
    # Dependent on the actual table ID from the FlipTable action
    preconditions = {
        "table_to_hide_behind": reference("table_id")
    }
--------------------------------------------------------------------------------

By using reference("table_id"), the second action obtains the ID from the effect of FlipTable automatically. During planning, if “table_id” is not already satisfied, it looks for an action that produces that effect—leading to the FlipTable step before taking cover.

─────────────────────────────────────────────────────────────────────────────────
4.2 Scenario 2: Passing a Picked-Up Key ID to Unlock a Door  

Now consider that you have locked doors in your game. The NPC needs to pick up the correct key, which sets a dynamic “key_id” for that door, and then use that key to unlock.

--------------------------------------------------------------------------------
// Scenario 2 Example
class PickUpKey(Action):
    effects = {
        "key_id": ...  # We dynamically obtain this ID at runtime
    }
    preconditions = {
        "has_inventory_space": True
    }

class UnlockDoor(Action):
    effects = {
        "door_unlocked": True
    }
    # The door can only be unlocked if we have the correct key ID
    preconditions = {
        "required_key_id": reference("key_id")
    }
--------------------------------------------------------------------------------

When the planner sees that the door is locked, it works backward, noticing the “required_key_id” precondition. It then finds “key_id” can be fulfilled by PickUpKey. This chain ensures the key is collected before unlocking the door.

─────────────────────────────────────────────────────────────────────────────────
4.3 Scenario 3: Linking a Generated Power-On State to Operate Machinery  

Sometimes you only need a boolean or small piece of state data from a previous action, but not necessarily a complex ID. For example, you flip a generator on (power_on = True), which is used in a later action to operate a crane or any powered system.

--------------------------------------------------------------------------------
// Scenario 3 Example
class SwitchPower(Action):
    effects = {
        "power_on": True
    }
    preconditions = {
        "has_generator_access": True
    }

class OperateCrane(Action):
    effects = {
        "crane_moved": True
    }
    # The crane only operates if power_on is True
    preconditions = {
        "power_on": True  
    }
--------------------------------------------------------------------------------

In more dynamic scenarios, you might store a reference for the “power_source_id” instead of a mere boolean. The pattern still remains—one action’s effect states “power_source_id: ...,” another uses reference("power_source_id") in preconditions.

─────────────────────────────────────────────────────────────────────────────────
4.4 Scenario 4: Passing a Craft Result as an Ingredient for Cooking  

GOAP can be used for more than just NPC combat or stealth—consider a crafting system. You might have an action that crafts a “flour_bag_id.” Another action then requires that same flour to cook bread.

--------------------------------------------------------------------------------
// Scenario 4 Example
class CraftFlour(Action):
    effects = {
        "flour_bag_id": ...
    }
    preconditions = {
        "has_wheat": True
    }

class BakeBread(Action):
    effects = {
        "bread_ready": True
    }
    preconditions = {
        "flour_ingredient_id": reference("flour_bag_id"),
        "has_water": True
    }
--------------------------------------------------------------------------------

When the goal is “bread_ready == True,” GOAP sees you need a flour ingredient to bake bread, leading it to see who can supply flour_bag_id. This automatically inserts the CraftFlour step before BakeBread.

─────────────────────────────────────────────────────────────────────────────────
4.5 Scenario 5: Linking a Repaired Bridge to Cross a River  

In an adventure scenario, crossing a river might require a repaired bridge. The action “RepairBridge” yields a reference to a “bridge_id” that was repaired, used next by the “CrossBridge” action.

--------------------------------------------------------------------------------
// Scenario 5 Example
class RepairBridge(Action):
    effects = {
        "bridge_id": ...
    }
    preconditions = {
        "has_wood_planks": True,
        "has_tools": True
    }

class CrossBridge(Action):
    effects = {
        "is_across_river": True
    }
    preconditions = {
        "bridge_to_cross": reference("bridge_id")
    }
--------------------------------------------------------------------------------

This ensures the agent can only cross the newly repaired structure. If multiple bridges exist, the specific “bridge_id” is resolved dynamically at runtime, letting the plan figure out the best route.

─────────────────────────────────────────────────────────────────────────────────
5. Usage Examples and Putting It All Together  
─────────────────────────────────────────────────────────────────────────────────

In the sample code (shown in the large code listing), we define a RegressivePlanner that uses A* to work backward from the goal. Here’s how you might use it with a world state and a goal:

--------------------------------------------------------------------------------
if __name__ == "__main__":
    world_state = {
        "has_table": True,
        "has_inventory_space": True,
        "has_generator_access": True,
        "has_wood_planks": False,
        "has_tools": False,
        # ... any additional states ...
    }
    goal_state = {"is_in_cover": True}  # For instance, we want to be in cover

    actions = [
        FlipTable(),
        TakeCoverBehindTable(),
        PickUpKey(),
        UnlockDoor(),
        SwitchPower(),
        OperateCrane(),
        # ... add any others from the scenarios ...
    ]
    planner = RegressivePlanner(world_state, actions)
    plan = planner.find_plan(goal_state)

    for step in plan:
        print(step)
--------------------------------------------------------------------------------

When the planner sees “is_in_cover=True,” it attempts to find which action can produce that effect—TakeCoverBehindTable. That action depends on the precondition “table_to_hide_behind = reference('table_id'),” so it identifies FlipTable must be done first, which supplies “table_id.” Similar logic unfolds for other pairs: picking up keys and unlocking doors, turning on power, and so on.

GOAP excels at letting AI agents dynamically select actions to achieve goals, rather than being locked into rigid paths. This regressive GOAP framework in Python highlights how preconditions, effects, and references compose into flexible plans at runtime. By defining simple, isolated actions—and letting the system figure out the chain of dependencies—you can rapidly prototype sophisticated behaviors that respond to emergent gameplay changes.

The reference mechanism is one of the crucial tools to manage dynamic data flow between actions without manually wiring transitions. As seen in the five scenarios (table flipping, door unlocking, powering a crane, cooking with crafted ingredients, and crossing a repaired bridge), references allow you to turn a single GOAP domain into a wide variety of gameplay possibilities with minimal extra code.





"""

from abc import ABC, abstractmethod
from collections import deque
from sys import float_info

from collections import defaultdict
from dataclasses import dataclass
from operator import attrgetter
from typing import Any, Optional, List, Dict
from enum import auto, Enum
from typing import ClassVar, Dict, Any, Tuple, List
from dataclasses import dataclass

from matplotlib import pyplot as plt
from networkx import DiGraph, draw_networkx
from dataclasses import dataclass
from typing import Callable, Optional, List, Dict, Any

State = Dict[str, Any]


from heapq import heappush, heappop


class PriorityElement:
    def __init__(self, element, score):
        self.value = element
        self.score = score
        self.removed = False

    def __lt__(self, other):
        return self.score < other.score


def _pass_through_key(x):
    return x


class PriorityQueue:
    def __init__(self, items=None, key=None):
        self._dict = {}
        self._heap = []

        if key is None:
            key = _pass_through_key

        self._key = key

        if items:
            for item in items:
                self.add(item)

    def __bool__(self):
        return bool(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def add(self, item):
        if item in self._dict:
            raise ValueError(f"{item} already in queue")

        element = PriorityElement(item, self._key(item))
        self._dict[item] = element
        heappush(self._heap, element)

    def pop(self):
        while True:
            element = heappop(self._heap)

            if not element.removed:
                element.removed = True
                value = element.value
                del self._dict[value]
                return value

    def remove(self, item):
        element = self._dict.pop(item)
        element.removed = True


class PathNotFoundException(Exception):
    pass


class AStarAlgorithm(ABC):
    @abstractmethod
    def get_neighbours(self, node):
        raise NotImplementedError

    @abstractmethod
    def get_g_score(self, current, node):
        raise NotImplementedError

    @abstractmethod
    def get_h_score(self, node):
        raise NotImplementedError

    def find_path(self, start, end):
        g_scores = {start: 0}
        f_scores = {start: self.get_h_score(start)}
        parents = {}

        candidates = PriorityQueue([start], key=f_scores.__getitem__)
        rejects = set()

        i = 0
        while candidates:
            current = candidates.pop()
            i += 1

            if self.is_finished(current, end, parents):
                return self.reconstruct_path(current, end, parents)

            rejects.add(current)

            for neighbour in self.get_neighbours(current):
                if neighbour in rejects:
                    continue

                tentative_g_score = g_scores[current] + self.get_g_score(
                    current, neighbour
                )
                tentative_is_better = tentative_g_score < g_scores.get(
                    neighbour, float_info.max
                )

                if neighbour in candidates and not tentative_is_better:
                    continue

                parents[neighbour] = current
                g_scores[neighbour] = tentative_g_score
                f_scores[neighbour] = tentative_g_score + self.get_h_score(neighbour)

                candidates.add(neighbour)

        raise PathNotFoundException("Couldn't find path for given nodes")

    @abstractmethod
    def is_finished(self, node, goal, parents):
        raise NotImplementedError

    def reconstruct_path(self, node, goal, parents):
        result = deque((node,))

        while True:
            try:
                node = parents[node]
            except KeyError:
                break
            result.appendleft(node)

        return result


class EffectReference:
    """Dynamic precondition that references an effect."""

    def __init__(self, name):
        self.goap_effect_reference = name


def reference(name: str) -> EffectReference:
    """Convenience function to return Forwarder object."""
    return EffectReference(name)


class RegActionValidator(type):
    """Metaclass to validate action classes at define time."""

    def __new__(mcs, cls_name: str, bases: Tuple[type], attrs: Dict[str, Any]):
        if bases:
            # Validate precondition plugins
            preconditions = attrs.get("preconditions", {})
            # Overwrite effect plugins to ellipsis
            effects = attrs.get("effects", {})
            # Compute names of service-like effects
            attrs["service_names"] = [k for k, v in effects.items() if v is Ellipsis]
            # Catch common errors with preconditions
            mcs._validate_preconditions(effects, preconditions)

        return super().__new__(mcs, cls_name, bases, attrs)

    @staticmethod
    def _validate_preconditions(all_effects: State, preconditions: State):
        for name, value in preconditions.items():
            if value is Ellipsis:
                raise ValueError(f"Preconditions cannot be services (...): '{name}'")

            elif (
                hasattr(value, "goap_effect_reference")
                and value.goap_effect_reference not in all_effects
            ):
                raise ValueError(
                    f"Invalid reference name for precondition '{name}': {value.name!r}"
                )


class RegAction(metaclass=RegActionValidator):
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


@dataclass(frozen=True)
class RegPlanStep:
    action: RegAction
    services: State


class _NotDefined:
    def __repr__(self):
        return "NOT_DEFINED"


NOT_DEFINED = _NotDefined()


@dataclass(frozen=True)
class RegressiveGOAPAStarNode:
    current_state: State
    goal_state: State
    action: Optional[RegAction] = None

    def __hash__(self):
        return id(self)

    @property
    def services(self):
        return {k: self.current_state[k] for k in self.action.service_names}

    def compute_cost(self, other: "RegressiveGOAPAStarNode") -> float:
        # The action determines the cost, and is stored on the "destination" node
        # i.e. x -- action --> y is encoded as (x, None), (y, action)
        return other.action.get_cost(other.services)

    def apply_action(
        self, world_state: State, action: RegAction
    ) -> "RegressiveGOAPAStarNode":
        # New node is a consequence of transitioning from
        # node to neighbour via action (which is the edge)
        current_state = self.current_state.copy()
        for key, value in action.effects.items():
            # After applying this action, as far as the regressive planner is concerned
            # we want to our new goal to be to satisfy the actions preconditions.
            # (see the next for block)
            if value is Ellipsis:
                # This action is "fulfilling" some of our goal state, hence
                # when using services (...), we take from the goal state!
                value = self.goal_state[key]

            # Normally we work backwards from the goal by building up a current state
            # that ultimately matches our goal state.
            # However, when an action shares a precondition and effect, we effectively
            # "update" our goal locally, so just as when we encounter a new unseen goal,
            # we need to take the current state from the world state
            elif key in action.preconditions:
                value = world_state.get(key, NOT_DEFINED)

            current_state[key] = value

        # Now update our goals!
        goal_state = self.goal_state.copy()
        for key, value in action.preconditions.items():
            # Allow references to effects (for pass-through services)
            if hasattr(value, "goap_effect_reference"):
                value = current_state[value.goap_effect_reference]

            goal_state[key] = value

            # Add fields to current state, overwriting if already defined
            # This ensure that we produce valid plans
            current_state[key] = world_state.get(key, NOT_DEFINED)

        return self.__class__(current_state, goal_state, action)

    @property
    def is_satisfied(self):
        return not self.unsatisfied_keys

    @property
    def unsatisfied_keys(self) -> List[str]:
        return [
            k
            for k, v in self.goal_state.items()
            # Allow keys not to be defined (e.g. for internal fields)
            if self.current_state[k] != v
        ]


_key_action_precedence = attrgetter("action.precedence")


class RegressiveGOAPAStarSearch(AStarAlgorithm):
    def __init__(self, world_state: State, actions: List[RegAction]):
        self._actions = actions
        self._effect_to_action = self._create_effect_table(actions)
        self._world_state = world_state

    def _create_effect_table(self, actions: List[RegAction]):
        effect_to_actions = defaultdict(list)

        for action in actions:
            for effect in action.effects:
                effect_to_actions[effect].append(action)

        effect_to_actions.default_factory = None
        return effect_to_actions

    def reconstruct_path(self, node, goal, parents):
        path = super().reconstruct_path(node, goal, parents)
        return reversed(path)

    def is_finished(self, node: RegressiveGOAPAStarNode, goal, parents):
        return node.is_satisfied

    def get_neighbours(self, node: RegressiveGOAPAStarNode):
        neighbours = []

        for key in node.unsatisfied_keys:
            goal_value = node.goal_state[key]

            for action in self._effect_to_action[key]:
                effect_value = action.effects[key]
                # If this effect does not satisfy the goal
                if effect_value != goal_value and effect_value is not Ellipsis:
                    continue

                # Compute neighbour after following action edge.
                neighbour = node.apply_action(self._world_state, action)

                # Ensure we can visit this node
                if not action.check_procedural_precondition(
                    neighbour.services, is_planning=True
                ):
                    continue

                neighbours.append(neighbour)
        neighbours.sort(key=_key_action_precedence, reverse=True)
        return neighbours

    def get_h_score(self, node: RegressiveGOAPAStarNode):
        return len(node.unsatisfied_keys)

    def get_g_score(
        self, node: RegressiveGOAPAStarNode, neighbour: RegressiveGOAPAStarNode
    ):
        return node.compute_cost(neighbour)


class RegressivePlanner:
    def __init__(self, world_state, actions):
        self._actions = actions
        self._world_state = world_state
        self._search = RegressiveGOAPAStarSearch(world_state, actions)

    @property
    def actions(self):
        return self._actions

    @property
    def world_state(self):
        return self._world_state

    def _create_plan_steps(self, path: List[RegressiveGOAPAStarNode]) -> List[RegPlanStep]:
        plan = []
        for node in path:
            if node.action is None:
                break
            plan.append(RegPlanStep(node.action, node.services))
        return plan

    def find_plan(self, goal_state: State) -> List[RegPlanStep]:
        # Initially populate the current state with keys from the goal, using
        # current values
        initial_state = {k: self._world_state[k] for k in goal_state}
        start = RegressiveGOAPAStarNode(initial_state, goal_state, None)

        path = self._search.find_path(start, goal_state)
        return self._create_plan_steps(path)


def repr_step(step):
    return step.action.__class__.__name__


def look_ahead(iterable):
    sequence = list(iterable)
    shifted_sequence = iter(sequence)
    next(shifted_sequence)
    return zip(sequence, shifted_sequence)


def visualise_plan(plan, filename):
    graph = DiGraph()

    for i, step in enumerate(plan):
        name = repr_step(step)
        graph.add_node(name)

    if len(plan) > 1:
        for i, (step, next_step) in enumerate(look_ahead(plan)):
            name = repr_step(step)
            next_name = repr_step(next_step)
            graph.add_edge(name, next_name)

    plt.axis("off")
    draw_networkx(graph)
    plt.savefig(filename)
    plt.close()


"""
Sometimes we want to define an action that provides a _service_ rather than
satisfies one particular state value. We can do this by providing ellipsis as the
effect.

When the procedural precondition is called, the action will be given the resolved
services dictionary, where it can succeed or fail on the values.

In this example, the `ChantIncantationEllipsis` action will chant _anything_ it is asked to.
Here, the `HauntWithIncantation` action is requesting `chant_incantation` service.
"""


class HauntWithIncantation(RegAction):
    effects = {"is_spooky": True}
    preconditions = {"is_undead": True, "chant_incantation": "WOOO I'm a ghost"}


class BecomeUndead(RegAction):
    effects = {"is_undead": True}
    preconditions = {"is_undead": False}


class ChantIncantationEllipsis(RegAction):
    effects = {"chant_incantation": ...}
    preconditions = {}


def example_1():
    world_state = {"is_spooky": False, "is_undead": False}
    goal_state = {"is_spooky": True}
    print("Initial State:", world_state)
    print("Goal State:   ", goal_state)

    actions = [BecomeUndead(), HauntWithIncantation(), ChantIncantationEllipsis()]
    planner = RegressivePlanner(world_state, actions)

    plan = planner.find_plan(goal_state)
    for action in plan:
        print(action)


"""
prints:
Initial State: {'is_spooky': False, 'is_undead': False}
Goal State:    {'is_spooky': True}
PlanStep(action=<__main__.ChantIncantationEllipsis object at 0x7bde744c8350>, services={'chant_incantation': "WOOO I'm a ghost"})
PlanStep(action=<__main__.BecomeUndead object at 0x7bde844c6e10>, services={})
PlanStep(action=<__main__.HauntWithIncantation object at 0x7bde744c8310>, services={})
"""


"""
Sometimes we also want to pass the service value to another dependent action.
In this example, the `PerformMagic` action requires two service (actions),
`chant_incantation` and `cast_spell`, and passes the `performs_magic` effect value
to both of them using `reference`.
"""


class HauntWithMagic(RegAction):
    effects = dict(is_spooky=True)
    preconditions = dict(is_undead=True, performs_magic="abracadabra")


class BecomeUndead(RegAction):
    effects = dict(is_undead=True)
    preconditions = dict(is_undead=False)


class PerformMagic(RegAction):
    effects = dict(performs_magic=...)
    preconditions = dict(
        chant_incantation=reference("performs_magic"),
        cast_spell=reference("performs_magic"),
    )


class ChantIncantation(RegAction):
    effects = dict(chant_incantation=...)
    preconditions = {}


class CastSpell(RegAction):
    effects = dict(cast_spell=...)
    preconditions = {}


def example_2():
    world_state = {"is_spooky": False, "is_undead": False}
    goal_state = {"is_spooky": True}
    print("Initial State:", world_state)
    print("Goal State:   ", goal_state)

    actions = [
        BecomeUndead(),
        HauntWithMagic(),
        CastSpell(),
        ChantIncantation(),
        PerformMagic(),
    ]
    planner = RegressivePlanner(world_state, actions)

    plan = planner.find_plan(goal_state)
    for action in plan:
        print(action)
"""prints:
Initial State: {'is_spooky': False, 'is_undead': False}
Goal State:    {'is_spooky': True}
PlanStep(action=<__main__.ChantIncantation object at 0x7d6090901c90>, services={'chant_incantation': 'abracadabra'})
PlanStep(action=<__main__.CastSpell object at 0x7d6090901d90>, services={'cast_spell': 'abracadabra'})
PlanStep(action=<__main__.PerformMagic object at 0x7d6090901c10>, services={'performs_magic': 'abracadabra'})
PlanStep(action=<__main__.BecomeUndead object at 0x7d6077f69d90>, services={})
PlanStep(action=<__main__.HauntWithMagic object at 0x7d6090901250>, services={})"""





###############################################################################
# BEGIN EXTENSION OF ORIGINAL CODE
###############################################################################


class OperationFailedError(Exception):
    """Indicates a high-level failure in an operation."""

    def __init__(self, reason: str):
        super().__init__(reason)


class SensorError(Exception):
    """Base class for sensor-related issues."""

    pass


class SensorMultipleTypeError(SensorError):
    """Raised when a sensor type conflict occurs."""

    pass


class SensorDoesNotExistError(SensorError):
    """Raised when attempting to access a sensor that doesn't exist in a collection."""

    pass


class SensorAlreadyInCollectionError(SensorError):
    """Raised when adding a sensor that already exists in a collection."""

    pass


class PlanError(Exception):
    """Base class for planning issues."""

    pass


class PlanFailed(PlanError):
    """Raised when planning fails to find a valid plan."""

    pass


class ActionError(Exception):
    """Base class for action-related issues."""

    pass


class ActionMultipleTypeError(ActionError):
    """Raised when multiple actions of the same name or type conflict."""

    pass


class ActionAlreadyInCollectionError(ActionError):
    """Raised when adding an action that already exists in a collection."""

    pass



###############################################################################
# 11) SENSOR, SENSORRESPONSE, SENSORS, FACT, WORKING MEMORY
###############################################################################

@dataclass
class SensorResponse:
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0

    @property
    def response(self) -> str:
        """Return stdout if present, else stderr."""
        return self.stdout if self.stdout else self.stderr


class Sensor:
    def __init__(self, name: str, binding: str, func: Callable[[], SensorResponse]):
        self.name = name
        self.binding = binding
        self.func = func
        self._response: Optional[SensorResponse] = None

    def exec(self) -> SensorResponse:
        resp = self.func()
        self._response = resp
        return resp

    @property
    def response(self) -> Optional[SensorResponse]:
        return self._response


class Sensors:
    def __init__(self):
        self._sensors: Dict[str, Sensor] = {}

    def add(self, name: str, binding: str, func: Callable[[], SensorResponse]):
        if name in self._sensors:
            raise SensorAlreadyInCollectionError(f"Sensor '{name}' already in collection.")
        self._sensors[name] = Sensor(name, binding, func)

    def remove(self, name: str):
        if name not in self._sensors:
            raise SensorDoesNotExistError(f"Sensor '{name}' not found.")
        del self._sensors[name]

    def get(self, name: str) -> Optional[Sensor]:
        return self._sensors.get(name, None)

    def run_all(self) -> List[Sensor]:
        results = []
        for s in self._sensors.values():
            s.exec()
            results.append(s)
        return results


@dataclass
class Fact:
    """
    Represents a sensor reading or piece of knowledge stored in working memory.
    sensor: which sensor created it
    data: the SensorResponse
    binding: which key in world_state or local usage 
    """
    sensor: str
    data: SensorResponse
    binding: str


###############################################################################
# 12) WORLDSTATE (BLACKBOARD-LIKE)
###############################################################################

class WorldState(dict):
    """
    A dictionary that also allows attribute-style access, e.g. ws.foo -> ws["foo"].
    """

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"No such attribute: {item}")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError:
            raise AttributeError(f"No such attribute: {item}")

    def __eq__(self, other):
        if not isinstance(other, dict):
            return False
        return dict.__eq__(self, other)


###############################################################################
# 13) STATE MACHINE (AUTOMATON) AND CONTROLLER
###############################################################################

class SimpleMethodicalMachine:
    """
    Stand-in for demonstration. In a real system, you’d use
    from automat import MethodicalMachine or an equivalent library.
    """

    def __init__(self):
        self.state = "waiting_orders"

    def input_goal(self):
        # No matter the current state, set state to waiting_orders
        self.state = "waiting_orders"

    def wait(self):
        # Return to waiting_orders
        self.state = "waiting_orders"

    def sense(self):
        # Transition from waiting_orders/acting to sensing
        if self.state in ("waiting_orders", "acting"):
            self.state = "sensing"
        # If in planning, or sensing, ignore or handle differently

    def plan(self):
        # Transition from sensing to planning
        if self.state == "sensing":
            self.state = "planning"

    def act(self):
        # Transition from planning to acting
        if self.state == "planning":
            self.state = "acting"

    def next_cycle(self):
        # Move from acting -> sensing
        if self.state == "acting":
            self.state = "sensing"


# If you use 'automat' for state machines, you can do:
# from automat import MethodicalMachine
# This code uses a simple stand-in for demonstration to mirror methodicalmachine usage.
# For a real project, install 'automat' and replace with MethodicalMachine usage.

class Automaton:
    """
    Automaton with 4 states:
      - waiting_orders (initial)
      - sensing
      - planning
      - acting
    Manages a sense → plan → act loop, storing sensors, working_memory, etc.
    """

    def __init__(self, world_state: WorldState, sensors: Sensors, actions: List[RegAction]):
        self.state_machine = SimpleMethodicalMachine()
        self.world_state = world_state
        self.working_memory: List[Fact] = []
        self.sensors = sensors
        self.actions = actions
        self.planner = RegressivePlanner(world_state, actions)
        self.action_plan: List[RegPlanStep] = []
        self.goal: Dict[str, Any] = {}

    def input_goal(self, goal: Dict[str, Any]):
        # State transition
        self.state_machine.input_goal()
        # Implementation
        self.goal = goal

    def wait(self):
        # State transition
        self.state_machine.wait()
        # Implementation: Do nothing extra

    def sense(self):
        # State transition
        self.state_machine.sense()
        if self.state_machine.state == "sensing":
            # Run sensors, store facts
            updated_sensors = self.sensors.run_all()
            for s in updated_sensors:
                if s.response is not None:
                    f = Fact(sensor=s.name, data=s.response, binding=s.binding)
                    self.working_memory.append(f)
                    # Write to world_state
                    self.world_state[s.binding] = f.data.response  # or parse out data
        # Possibly remove old or low-confidence facts, etc.

    def plan(self):
        # State transition
        self.state_machine.plan()
        if self.state_machine.state == "planning":
            # Attempt to build a plan from world_state to self.goal
            try:
                plan_steps = self.planner.find_plan(self.goal)
                self.action_plan = plan_steps
            except PlanFailed as e:
                self.action_plan = []
                raise e

    def act(self):
        # State transition
        self.state_machine.act()
        if self.state_machine.state == "acting":
            # Execute the actions in the plan if still valid
            for step in self.action_plan:
                # Check step.action preconditions again if needed, or consult working_memory
                # Then "execute" the action. In a real system, step.action might have a .run(...).
                # For demonstration, we do nothing except symbolically update the world_state
                # with the action’s effects if apply_effects_on_exit is True.
                if not step.action.apply_effects_on_exit:
                    continue
                # If the action has literal effect values (non-ellipsis) we can update
                for eff_key, eff_val in step.action.effects.items():
                    if eff_val is not Ellipsis:
                        self.world_state[eff_key] = eff_val
                # If the action has "service_names" for Ellipsis, they are resolved in step.services
                # but that might not be needed in a purely symbolic sense here.

            # After acting, move to next cycle
            self.state_machine.next_cycle()
            # Optionally, we can clear or reduce working_memory if we want
            # self.working_memory.clear()

    def reset_working_memory(self):
        self.working_memory.clear()


class AutomatonController:
    """
    Provides a high-level loop around the Automaton.
    """

    def __init__(self, automaton: Automaton):
        self.automaton = automaton
        self._running = False

    def start(self):
        """
        Example loop that repeatedly tries sense -> plan -> act
        until goal is satisfied, or indefinite if no external break.
        """
        self._running = True
        while self._running:
            # 1) sense
            self.automaton.sense()

            # 2) check if goal is satisfied
            # if so, wait
            if self.goal_satisfied():
                self.automaton.wait()
            else:
                # 3) plan
                try:
                    self.automaton.plan()
                except PlanFailed:
                    # No plan found; might do random fallback or remain
                    pass

                # 4) act
                self.automaton.act()

            # In a real game or AI system, you might add a sleep or time-step here
            # For demonstration, we can break the loop once goal is satisfied
            if self.goal_satisfied():
                self._running = False

    def goal_satisfied(self) -> bool:
        """
        Simple check if the current world_state satisfies the automaton's goal.
        """
        for k, v in self.automaton.goal.items():
            if k not in self.automaton.world_state or self.automaton.world_state[k] != v:
                return False
        return True

    def stop(self):
        self._running = False




if __name__ == "__main__":
    # A small demo showing how you might instantiate everything.

    # 1) Define a couple of custom Actions
    class FlipTable(RegAction):
        effects = {
            "table_id": Ellipsis  # dynamic
        }
        preconditions = {
            "has_table": True
        }
        cost = 2.0

    class TakeCoverBehindTable(RegAction):
        effects = {
            "is_in_cover": True
        }
        preconditions = {
            # We require a specific table to hide behind, referencing "table_id"
            "table_to_hide_behind": reference("table_id")
        }
        cost = 1.0

    # 2) Set up the world_state, sensors, etc.
    world_state = WorldState()
    world_state["has_table"] = True
    world_state["is_in_cover"] = False

    sensors = Sensors()
    # Example dummy sensor that does nothing but set "enemy_visible" to "False" in world_state
    def sense_enemy():
        return SensorResponse(stdout="False", stderr="", return_code=0)

    sensors.add("EnemySensor", "enemy_visible", sense_enemy)

    # 3) Build an Automaton
    actions = [FlipTable(), TakeCoverBehindTable()]
    automaton = Automaton(world_state, sensors, actions)
    controller = AutomatonController(automaton)

    # 4) Supply a goal and run
    goal = {"is_in_cover": True}
    automaton.input_goal(goal)  # sets automaton.goal
    controller.start()

    # 5) Check the outcome
    print("Final World State:", dict(automaton.world_state))
    print("Working Memory Facts:", automaton.working_memory)

    # The plan will have:
    # Step 1: FlipTable -> provides "table_id"
    # Step 2: TakeCoverBehindTable -> references "table_id" and sets is_in_cover=True
    #
    # Because once we run the code, the regressive planner sees we need is_in_cover=True,
    # it sees that "TakeCoverBehindTable" requires "table_to_hide_behind"=reference("table_id"),
    # so we unify that with "FlipTable"'s effect "table_id"=Ellipsis. 
    # The plan leads to flipping the table first, then taking cover.
    #
    # This completes the demonstration.

