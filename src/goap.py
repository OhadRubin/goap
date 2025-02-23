from src.utils.nx_utils import *
from src.regressive_planner import RegressivePlanner, RegAction, reference, State


from typing import Callable, List


class Sensor:
    """Sensor object factory"""

    def __init__(self, name: str, binding: str, func: Callable):
        """Sensor object model

        :param binding: string containing the key name
                        which the sensor will right to
        :param name: string containing the name of the sensor
        """
        self.binding = binding
        self.name = name
        self.func = func
        self.response = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__repr__()

    def __call__(self):
        return self.exec()

    def exec(self):
        try:
            stdout, stderr, return_code = self.func()
        except RuntimeError as e:
            raise RuntimeError(f"Error executing function {self.func}. Exception: {e}")
        self.response = SensorResponse(
            stdout=stdout, stderr=stderr, return_code=return_code
        )
        return self.response


class SensorResponse:

    def __init__(
        self,
        stdout: str = "",
        stderr: str = "",
        return_code: int = 0,
    ):
        """

        :param name:
        :param sensor_type:
        """
        self._stdout = stdout
        self._stderr = stderr
        self.return_code = return_code

    def __str__(self):
        response = self.stdout
        if self.stderr:
            response = self.stderr
        return "Response: {}, ReturnCode: {}".format(response, self.return_code)

    def __repr__(self):
        return self.__str__()

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, value: str):
        self._stdout = value.rstrip("\r\n")

    @property
    def stderr(self):
        return self._stderr

    @stderr.setter
    def stderr(self, value: str):
        self._stderr = value.rstrip("\r\n")

    @property
    def response(self):
        if self.stdout:
            return self.stdout
        else:
            return self.stderr

    @response.setter
    def response(self, value):
        self.response = value


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


from time import sleep
from datetime import datetime
from automat import MethodicalMachine
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Fact:

    binding: str
    data: Any
    parent_sensor: str
    time_stamp: datetime = field(init=False)

    def __post_init__(self):
        self.time_stamp = datetime.now()

    def __str__(self):
        return f"{self.binding}: {self.data}"

    def __repr__(self):
        return self.__str__()


class Automaton:
    """A 3 State Machine Automaton: observing (aka monitor or patrol), planning and acting"""

    machine = MethodicalMachine()

    def __init__(
        self,
        name: str,
        sensors: List[Sensor],
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
            self.working_memory.append(
                Fact(
                    parent_sensor=sensor.name,
                    data=sensor.exec(),
                    binding=sensor.binding,
                )
            )
        for fact in self.working_memory:
            setattr(self.world_state, fact.binding, fact.data.response)

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
        self, actions: NXActions, sensors: List[Sensor], name: str, world_state: dict
    ):
        """
        :param actions: List of actions
        :param sensors: List of sensors
        :param name: Name of the automaton
        :param world_state: Initial world state
        """
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
                print(
                    "World state differs from goal: \nState: {}\nGoal: {}".format(
                        self.automaton.world_state, self.goal
                    )
                )
                print("Need to find an action plan")
                self.automaton.plan()
                print(
                    "Plan found. Will execute the action plan: {}".format(
                        self.automaton.action_plan
                    )
                )
                self.automaton.act()
            else:
                print("World state equals to goal: {}".format(self.goal))
                self.automaton.wait()
            sleep(5)


from typing import Optional, Tuple
from subprocess import Popen, PIPE


class ShellCommand(object):
    """Creates an callable object which executes a shell command"""

    def __init__(self, command: str, timeout: int = 30):
        self.command = command
        self.timeout = timeout
        self.response = None

    def __call__(self):
        return self.run(self.command)

    def run(self, command=Optional[str]) -> Tuple[str, str, int]:
        process = Popen(
            ["/bin/sh", "-c", command],
            shell=False,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
            return_code = process.returncode
            self.response = (stdout.strip().split(" ")[-1], stderr, return_code)
        except RuntimeError as e:
            raise Exception(f"Error opening process {self.command}: {e}")
        finally:
            process.kill()

        return self.response


def setup_sensors():
    sense_dir_state = ShellCommand(
        command='if [ -d "/tmp/goap_tmp" ]; then echo -n "exist"; else echo -n "not_exist"; fi'
    )
    sense_dir_content = ShellCommand(
        command='[ -f /tmp/goap_tmp/.token ] && echo -n "token_found" || echo -n "token_not_found"'
    )
    sensors = [
        Sensor(name="SenseTmpDirState", func=sense_dir_state, binding="tmp_dir_state"),
        Sensor(
            name="SenseTmpDirContent", func=sense_dir_content, binding="tmp_dir_content"
        ),
    ]
    return sensors


class CreateTmpDir(RegAction):
    effects = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}
    preconditions = {"tmp_dir_state": "not_exist", "tmp_dir_content": "token_not_found"}

    def func(self):
        return ShellCommand(command="mkdir -p /tmp/goap_tmp")()


class CreateToken(RegAction):
    effects = {"tmp_dir_state": "exist", "tmp_dir_content": "token_found"}
    preconditions = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}

    def func(self):
        return ShellCommand(command="touch /tmp/goap_tmp/.token")()


def setup_actions():
    actions = [
        CreateTmpDir(),
        CreateToken(),
    ]
    print(f"actions: {actions}")
    return actions


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
        actions=setup_actions(),
        sensors=setup_sensors(),
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
