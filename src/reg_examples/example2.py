"""
Sometimes we also want to pass the service value to another dependent action.
In this example, the `PerformMagic` action requires two service (actions),
`chant_incantation` and `cast_spell`, and passes the `performs_magic` effect value
to both of them using `reference`.
"""
from src.regressive_planner import RegressivePlanner, RegAction, reference


class HauntWithMagic(RegAction):
    # Requires being undead and having performed magic with "abracadabra" spell
    # Results in making something spooky
    effects = dict(is_spooky=True)
    preconditions = dict(is_undead=True, performs_magic="abracadabra")


class BecomeUndead(RegAction):
    # Requires not being undead yet
    # Results in becoming undead
    effects = dict(is_undead=True)
    preconditions = dict(is_undead=False)


class PerformMagic(RegAction):
    # The ... means this action provides a service value that will be passed to other actions
    # The value "abracadabra" will be passed to both chant_incantation and cast_spell
    # through the reference() function
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
    
    def func(self):
        print("Casting spell")


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
    for step in plan:
        print(step)
        step.action.exec()


"""prints:
Initial State: {'is_spooky': False, 'is_undead': False}
Goal State:    {'is_spooky': True}
PlanStep(action=<__main__.ChantIncantation object at 0x7d6090901c90>, services={'chant_incantation': 'abracadabra'})
PlanStep(action=<__main__.CastSpell object at 0x7d6090901d90>, services={'cast_spell': 'abracadabra'})
PlanStep(action=<__main__.PerformMagic object at 0x7d6090901c10>, services={'performs_magic': 'abracadabra'})
PlanStep(action=<__main__.BecomeUndead object at 0x7d6077f69d90>, services={})
PlanStep(action=<__main__.HauntWithMagic object at 0x7d6090901250>, services={})"""



if __name__ == "__main__":
    example_2()
