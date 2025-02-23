"""
Sometimes we want to define an action that provides a _service_ rather than
satisfies one particular state value. We can do this by providing ellipsis as the
effect.

When the procedural precondition is called, the action will be given the resolved
services dictionary, where it can succeed or fail on the values.

In this example, the `ChantIncantationEllipsis` action will chant _anything_ it is asked to.
Here, the `HauntWithIncantation` action is requesting `chant_incantation` service.
"""
from src.regressive_planner import RegressivePlanner, RegAction, reference

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

if __name__ == "__main__":
    example_1()
