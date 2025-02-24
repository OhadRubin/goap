"""
Sometimes we also want to pass the service value to another dependent action.
In this example, the `PerformMagic` action requires two service (actions),
`chant_incantation` and `cast_spell`, and passes the `performs_magic` effect value
to both of them using `reference`.
"""

from src.regressive_planner import RegressivePlanner, RegAction, reference

class CreateTmpDir(RegAction):
    effects = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}
    preconditions = {"tmp_dir_state": "not_exist", "tmp_dir_content": "token_not_found"}


class CreateToken(RegAction):
    effects = {"tmp_dir_state": "exist", "tmp_dir_content": "token_found"}
    preconditions = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}


def example_4():
    world_state = {
        "tmp_dir_state": "not_exist",
        "tmp_dir_content": "token_not_found",
        "is_relaxed": False,
    }
    goal_state = {"tmp_dir_content": "token_found"}
    print("Initial State:", world_state)
    print("Goal State:   ", goal_state)

    actions = [
        CreateTmpDir(),
        CreateToken(),
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
    example_4()
