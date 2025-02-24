from src.regressive_planner import RegressivePlanner, RegAction, reference, State, RegSensor

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

    def __eq__(self, other):
        if other.items() != self.items():
            return False
        else:
            return True

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


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
        self.actions_response = []
        self.goal = {}

    def __sense_environment(self):
        for sensor in self.sensors:
            self.working_memory.append(sensor())
        logger.info(f"Working memory: {self.working_memory}")
        for fact in self.working_memory:
            setattr(self.world_state, fact.binding, fact.data)

    def __set_action_plan(self):

        self.action_plan = self.planner.find_plan(self.goal, self.world_state)
        return self.action_plan

    def __execute_action_plan(self):
        response = []
        for step in self.action_plan:
            result = step.action.exec()
            response.append(result)
        self.actions_response = response
        return "Action planning execution results: {}".format(self.action_plan_response)

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
        self.__execute_action_plan()

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
        self, actions: List[RegAction], sensors: Sensors, name: str, world_state: dict
    ):
        self.automaton = Automaton(
            actions=actions,
            sensors=sensors,
            name=name,
            world_state_facts=world_state,
        )

    @property
    def world_state(self):
        return self.automaton.world_state

    @world_state.setter
    def world_state(self, value):
        self.automaton.world_state = value

    @property
    def goal(self):
        return self.automaton.goal

    @goal.setter
    def goal(self, value):
        self.automaton.input_goal(value)

    def start(self):
        while True:
            self.automaton.sense()
            if self.automaton.world_state != self.goal:
                logger.info(f"World state differs from goal:\nState: {self.automaton.world_state}\nGoal: {self.goal}")
                logger.info("Need to find an action plan")
                self.automaton.plan()
                logger.info(f"Plan found. Will execute the action plan: {self.automaton.action_plan}")
                self.automaton.act()
            else:
                logger.info(f"World state equals to goal: {self.goal}")
                self.automaton.wait()
            sleep(5)


class DirectoryStateSensor(RegSensor):
    binding = "tmp_dir_state"
    def exec(self):
        tmp_path = Path("/tmp/goap_tmp")
        out =  "exist" if tmp_path.exists() else "not_exist"
        return out

class TokenStateSensor(RegSensor):
    binding = "tmp_dir_content"
    def exec(self):
        token_path = Path("/tmp/goap_tmp") / ".token"
        out = "token_found" if token_path.exists() else "token_not_found"
        return out


class CreateTmpDir(RegAction):
    effects = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}
    preconditions = {"tmp_dir_state": "not_exist", "tmp_dir_content": "token_not_found"}

    def exec(self):
        Path("/tmp/goap_tmp").mkdir(parents=True, exist_ok=True)

class CreateToken(RegAction):
    effects = {"tmp_dir_state": "exist", "tmp_dir_content": "token_found"}
    preconditions = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}

    def exec(self):
        (Path("/tmp/goap_tmp") / ".token").touch()


def setup_automaton():
    """
    Set up an automaton with the specified planner type

    :param planner_type: Type of planner to use ("regressive" or "nx"). Defaults to "regressive"
    :return: Configured AutomatonController instance
    """
    world_state_matrix = {
        "tmp_dir_state": "Unknown",
        "tmp_dir_content": "Unknown",
    }
    automaton = AutomatonController(
        name="directory_watcher",
        actions=[CreateTmpDir(), CreateToken()],
        sensors=[DirectoryStateSensor(), TokenStateSensor()],
        world_state=world_state_matrix,
    )
    return automaton


def main():
    goal = {
        "tmp_dir_state": "exist",
        "tmp_dir_content": "token_found",
    }
    dir_handler = setup_automaton()  # or setup_automaton("nx") to use NXPlanner
    dir_handler.goal = goal
    dir_handler.start()


if __name__ == "__main__":
    main()
