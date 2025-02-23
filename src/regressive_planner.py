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


from src.utils.astar import AStarAlgorithm


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

    def _create_plan_steps(
        self, path: List[RegressiveGOAPAStarNode]
    ) -> List[RegPlanStep]:
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


