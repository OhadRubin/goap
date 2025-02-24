from src.regressive_planner import (
    RegressivePlanner,
    RegAction,
    reference,
    State,
    RegSensor,
    RegGoal,
)

from loguru import logger

from typing import Callable, List
import subprocess
from dataclasses import dataclass
from pathlib import Path
from abc import ABC, abstractmethod
from time import sleep
from automat import MethodicalMachine
from typing import Tuple, Dict

Sensors = List[RegSensor]

class WorldState(dict):
    """
    ws = WorldState({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(WorldState, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(WorldState, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(WorldState, self).__delitem__(key)
        del self.__dict__[key]

    def __le__(self, other):
        for k, v in other.__dict__():
            if other.__dict__()[k] != v:
                return False
        return True
    def condition_met(self, condition_dict: Dict[str, Any]) -> bool:
        return all(self.get(k, None) == v for k, v in condition_dict.items())

    def __eq__(self, other):
        if other.items() != self.items():
            return False
        else:
            return True

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

from typing import Any


# #
# # Executes plan. This function is called on every game loop.
# # "plan" is the current list of actions, and delta is the time since last loop.
# #
# # Every action exposes a function called perform, which will return true when
# # the job is complete, so the agent can jump to the next action in the list.
# #
# func _follow_plan(plan, delta):
# 	if plan.size() == 0:
# 		return

# 	var is_step_complete = plan[_current_plan_step].perform(_actor, delta)
# 	if is_step_complete and _current_plan_step < plan.size() - 1:
# 		_current_plan_step += 1

# On every loop this script checks if the current goal is still
# the highest priority. if it's not, it requests the action planner a new plan
# for the new high priority goal.
#
# func _process(delta):
# 	var goal = _update_best_goal()
# 	if _current_goal == null or goal != _current_goal:
# 	# You can set in the blackboard any relevant information you want to use
# 	# when calculating action costs and status. I'm not sure here is the best
# 	# place to leave it, but I kept here to keep things simple.
# 		var blackboard = {
# 			"position": _actor.position,
# 			}

# 		for s in WorldState._state:
# 			blackboard[s] = WorldState._state[s]

# 		_current_goal = goal
# 		_current_plan = Goap.get_action_planner().get_plan(_current_goal, blackboard)
# 		_current_plan_step = 0
# 	else:
# 		_follow_plan(_current_plan, delta)

class Automaton:
    """A 3 State Machine Automaton: observing (aka monitor or patrol), planning and acting"""

    machine = MethodicalMachine()

    def __init__(
        self,
        name: str,
        sensors: Sensors,
        actions: List[RegAction],
        world_state_facts: dict,
    ):
        # setup
        self.world_state = WorldState(world_state_facts)
        self.working_memory = []
        self.name = name
        self.sensors = sensors
        self.actions = actions
        self.planner = RegressivePlanner(self.world_state, self.actions)
        self.action_plan = []
        self.action_plan_response = None
        self.sensors_responses = {}
        self._current_plan_step = 0
        self._changed_facts = {}
        self.plan_for_goal = None

    def __sense_environment(self):
        for sensor in self.sensors:
            if not self.world_state.condition_met(sensor.preconditions):
                continue
            self.working_memory.append(sensor())
        _changed_facts = {}
        for fact in self.working_memory:
            prev_value = self.world_state.get(fact.binding, None)
            if prev_value != fact.data:
                _changed_facts[fact.binding] = prev_value
            setattr(self.world_state, fact.binding, fact.data)
        self._changed_facts = _changed_facts

    def __set_action_plan(self):
        # if either the world state has changed or we changed goals.
        if self.plan_for_goal == self.goal:
            # and len(self._changed_facts)==0:
            logger.info(f"Len of the plan: {len(self.action_plan)}")
            return self.action_plan
        logger.info(f"world state and actions: {self.world_state} {self.actions}")
        planner = RegressivePlanner(self.world_state, self.actions)
        self.action_plan = planner.find_plan(self.goal)
        self.plan_for_goal = self.goal
        self._current_plan_step = 0
        logger.info(f"Len of the plan: {len(self.action_plan)}")
        return self.action_plan

    def __execute_action_plan(self):
        effects = {}
        if self._current_plan_step < len(self.action_plan):
            curr_step = self.action_plan[self._current_plan_step]
            logger.info(f"Executing action: {curr_step.action}")
            curr_step.action.exec()
            effects = curr_step.action.effects
            for key,value in effects.items():
                setattr(self.world_state, key, value)
            self._current_plan_step += 1
        return effects

    @machine.state(initial=True)
    def waiting_orders(self):
        """Waiting goal / orders"""

    @machine.state()
    def sensing(self):
        """Running sensors and assimilating sensor's responses"""

    @machine.state()
    def planning(self):
        """Generating action plan to change actual world state to achieve goal"""

    @machine.state()
    def acting(self):
        """Executing action plan"""

    @machine.input()
    def wait(self):
        """Input waiting_orders state"""

    @machine.input()
    def sense(self):
        """Input sense state"""

    @machine.output()
    def __sense(self):
        """Execute sensors"""
        self.__sense_environment()

    @machine.input()
    def plan(self):
        """Input for planning state"""

    @machine.output()
    def __plan(self):
        """Generate action plan"""
        self.__set_action_plan()

    @machine.input()
    def act(self):
        """Input for acting state"""

    @machine.output()
    def __act(self):
        """Execute action plan"""
        return self.__execute_action_plan()

    @machine.input()
    def input_goal(self, goal):
        """Change / Set AI goal"""

    @machine.output()
    def __input_goal(self, goal):
        """Actually sets goal"""
        self.goal = goal

    @machine.output()
    def __reset_working_memory(self):
        self.working_memory = []

    # cyclical main states
    waiting_orders.upon(sense, enter=sensing, outputs=[__sense])
    sensing.upon(plan, enter=planning, outputs=[__plan])
    planning.upon(act, enter=acting, outputs=[__act])
    acting.upon(sense, enter=sensing, outputs=[__reset_working_memory, __sense])
    # change orders
    waiting_orders.upon(input_goal, enter=waiting_orders, outputs=[__input_goal])
    planning.upon(input_goal, enter=waiting_orders, outputs=[__input_goal])
    acting.upon(input_goal, enter=waiting_orders, outputs=[__input_goal])
    # reset working memory from sensing
    sensing.upon(wait, enter=waiting_orders, outputs=[__reset_working_memory])


class AutomatonController(object):

    def __init__(
        self,
        actions: List[RegAction],
        sensors: Sensors,
        name: str,
        world_state: dict,
        possible_goals: Dict[str, RegGoal],
    ):
        self.actions = actions
        self.sensors = sensors
        self.name = name
        self.initial_world_state = world_state
        self.goal = None
        self.possible_goals = possible_goals
        self._world_state = world_state
        self.automaton = Automaton(
            actions=self.actions,
            sensors=self.sensors,
            name=self.name,
            world_state_facts=world_state,
        )

    def update_goal(self):
        self.automaton.input_goal(self.goal.desired_state)

    def update_best_goal(self):
        max_priority_goal = self.goal if self.goal else None
        for goal in self.possible_goals:
            if max_priority_goal is None or (
                goal.priority > max_priority_goal.priority
                and self.world_state.condition_met(goal.preconditions)
            ):
                max_priority_goal = goal
        if max_priority_goal is not self.goal:
            self.goal = max_priority_goal
            return True
        return False

    @property
    def world_state(self):
        if self.automaton is not None:
            return self.automaton.world_state
        return self._world_state

    def start(self):
        while True:
            if self.update_best_goal():
                logger.info(f"Switching to higher priority goal: {self.goal.name}")
                self.update_goal()
            self.automaton.sense()

            if not self.world_state.condition_met(self.goal.desired_state):
                logger.info(f"World state differs from goal:\nState: {self.world_state}\nGoal: {self.goal}")
                self.automaton.plan()
                logger.info(f"Plan found. Will execute the action plan: {self.automaton.action_plan}")
                self.automaton.act()
            else:
                logger.info(f"World state equals to goal: {self.goal}")
                self.automaton.wait()
            sleep(5)
