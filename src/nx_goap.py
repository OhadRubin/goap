from src.utils.nx_utils import *
from src.regressive_planner import RegressivePlanner, RegAction, reference, State


class RegActionAdapter(RegAction):
    """Adapter class to make NXAction compatible with RegAction"""

    def __init__(self, nx_action):
        self.nx_action = nx_action
        self.effects = nx_action.effects
        self.preconditions = nx_action.conditions
        # Extract service names from effects that use Ellipsis
        self.service_names = [k for k, v in nx_action.effects.items() if v is Ellipsis]
        self.cost = nx_action.cost

    def check_procedural_precondition(self, services: State, is_planning: bool) -> bool:
        return True

    def get_cost(self, services) -> float:
        return self.cost

    def exec(self):
        return self.nx_action.exec()


class RegPlanner:
    def __init__(self, actions: NXActions):
        """
        :param actions: list of actions
        """
        # Convert NXActions to RegActions
        reg_actions = [RegActionAdapter(action) for action in actions]
        self.world_state = None  # Will be set in plan()
        self.planner = None  # Will be initialized in plan() with proper world state
        self.reg_actions = reg_actions
        self.actions = actions
        self.goal = None

    def plan(self, world_state: dict, goal: dict) -> list:
        """Find a plan to reach the goal state from the world state"""
        self.world_state = world_state
        self.goal = goal

        # Initialize planner with current world state
        self.planner = RegressivePlanner(world_state, self.reg_actions)

        # Get plan
        plan = self.planner.find_plan(goal)

        # Convert plan to format expected by NXPlanner consumers
        converted_plan = []
        for step in plan:
            # Get original NXAction
            nx_action = step.action.nx_action
            converted_plan.append(
                [None, None, {
                    "name": nx_action.name,
                    "pre": nx_action.conditions,
                    "eff": nx_action.effects,
                    "object": nx_action,
                    "services": step.services  # Include services from the plan step
                }]
            )

        return converted_plan


class NXPlanner(object):

    def __init__(self, actions: NXActions):
        """
        :param actions: list of actions
        """
        # init vars
        self.goal = None
        self.world_state = None
        self.actions = actions
        self.states = Nodes()
        self.transitions = Edges()
        self.action_plan = []
        self.graph = Graph(nodes=self.states, edges=self.transitions)

    def __generate_states(self, actions: NXActions, world_state: dict, goal: dict):
        self.states.add(Node(world_state))
        self.states.add(Node(goal))
        for action in actions:
            pre = {**world_state, **action.conditions}
            eff = {**pre, **action.effects}
            self.states.add(Node(attributes=pre))
            self.states.add(Node(attributes=eff))

    def __generate_transitions(self, actions, states):
        for action in actions:
            for state in states:
                if action.conditions.items() <= state.attributes.items():
                    attr = {**state.attributes, **action.effects}
                    suc = self.states.get(attr)
                    self.transitions.add(
                        Edge(
                            name=action.name,
                            predecessor=state,
                            successor=suc,
                            cost=action.cost,
                            obj=action,
                        )
                    )

    def plan(self, state: dict, goal: dict) -> list:
        self.world_state = state
        self.goal = goal
        self.__generate_states(self.actions, self.world_state, self.goal)
        self.__generate_transitions(self.actions, self.states)
        self.graph = Graph(self.states, self.transitions)
        world_state_node = self.states.get(state)
        goal_node = self.states.get(goal)
        plan = []
        if state != goal:
            try:
                path = self.graph.path(world_state_node, goal_node)
            except EnvironmentError as e:
                print(f"No possible path: {e}")

            try:
                plan = self.graph.edge_between_nodes(path)
            except EnvironmentError as e:
                print(f"No plan available: {e}")

        return plan


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


class Sensors:

    def __init__(self, sensors: List[Sensor] = None):
        """Collection of sensors, adds only unique sensors

        :param sensors: List containing the sensor objects
        """
        self.sensors = sensors if sensors else []

    def __str__(self):
        names = [sensor.name for sensor in self.sensors]
        return "{}".format(names)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        if self.sensors:
            return len(self.sensors)
        else:
            return 0

    def __iter__(self):
        return iter(self.sensors)

    def __delete__(self, sensor):
        if sensor in self.sensors:
            self.sensors.remove(sensor)
        else:
            raise SensorDoesNotExistError

    def __call__(self, name: str):
        """Search for sensor, return None if does not match

        :param name: sensor's name
        :return: Sensor
        """
        sens = None
        for s in self.sensors:
            if s.name == name:
                sens = s
        return sens

    def get(self, name):
        result = None
        if not self.sensors:
            return result

        for sensor in self.sensors:
            if sensor.name == name:
                result = sensor

        return result

    def add(self, name: str, binding: str, func: Callable):
        if not self.get(name=name):
            self.sensors.append(Sensor(name=name, binding=binding, func=func))
        else:
            raise SensorAlreadyInCollectionError(
                f"Another sensor is using the same name: {name}"
            )

    def remove(self, name: str):
        result = False
        if not self.sensors:
            return result
        sensor = self.get(name)
        if sensor:
            self.sensors.remove(sensor)
            result = True
        return result

    def run_all(self) -> list:
        responses = [sensor.exec() for sensor in self.sensors]
        return responses


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


class Fact(object):
    def __init__(self, sensor, data, binding):
        self.binding = binding
        self.data = data
        self.time_stamp = datetime.now()
        self.parent_sensor = sensor

    def __str__(self):
        return "{}: {}".format(self.binding, self.data)

    def __repr__(self):
        return self.__str__()


class AutomatonPriorities:
    def __init__(self, items: list):
        self._items = items

    def __iter__(self):
        return self._items

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return self.__repr__()


class Automaton:
    """A 3 State Machine Automaton: observing (aka monitor or patrol), planning and acting"""

    machine = MethodicalMachine()

    def __init__(
        self, name: str, sensors: Sensors, actions: NXActions, world_state_facts: dict, planner_type: str = "regressive"
    ):
        """
        :param name: Name of the automaton
        :param sensors: List of sensors
        :param actions: List of actions
        :param world_state_facts: Initial world state
        :param planner_type: Type of planner to use ("regressive" or "nx"). Defaults to "regressive"
        """
        # setup
        self.world_state = WorldState(world_state_facts)
        self.working_memory = []
        self.name = name
        self.sensors = sensors
        self.actions = actions
        
        # Initialize planner based on type
        if planner_type.lower() == "nx":
            self.planner = NXPlanner(actions=actions)
        elif planner_type.lower() == "regressive":
            self.planner = RegPlanner(actions=actions)
        else:
            raise ValueError(f"Unknown planner type: {planner_type}. Must be 'nx' or 'regressive'")
        
        #
        self.action_plan = []
        self.action_plan_response = None
        self.sensors_responses = {}
        self.actions_response = []
        self.goal = {}

    def __sense_environment(self):
        for sensor in self.sensors:
            self.working_memory.append(
                Fact(sensor=sensor.name, data=sensor.exec(), binding=sensor.binding)
            )
        for fact in self.working_memory:
            setattr(self.world_state, fact.binding, fact.data.response)

    def __set_action_plan(self):
        self.action_plan = self.planner.plan(self.world_state, self.goal)
        return self.action_plan

    def __execute_action_plan(self):
        self.actions_response = [
            action[2]["object"].exec() for action in self.action_plan
        ]
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
        self, actions: NXActions, sensors: Sensors, name: str, world_state: dict, planner_type: str = "regressive"
    ):
        """
        :param actions: List of actions
        :param sensors: List of sensors
        :param name: Name of the automaton
        :param world_state: Initial world state
        :param planner_type: Type of planner to use ("regressive" or "nx"). Defaults to "regressive"
        """
        self.automaton = Automaton(
            actions=actions, 
            sensors=sensors, 
            name=name, 
            world_state_facts=world_state,
            planner_type=planner_type
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
                    "Plain found. Will execute the action plan: {}".format(
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
    sensors = Sensors()
    sensors.add(name="SenseTmpDirState", func=sense_dir_state, binding="tmp_dir_state")
    sensors.add(
        name="SenseTmpDirContent", func=sense_dir_content, binding="tmp_dir_content"
    )
    return sensors


def setup_actions():
    mkdir = ShellCommand(command="mkdir -p /tmp/goap_tmp")
    mktoken = ShellCommand(command="touch /tmp/goap_tmp/.token")
    actions = NXActions()
    actions.add(
        name="CreateTmpDir",
        conditions={"tmp_dir_state": "not_exist", "tmp_dir_content": "token_not_found"},
        effects={"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"},
        func=mkdir,
    )
    actions.add(
        name="CreateToken",
        conditions={"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"},
        effects={"tmp_dir_state": "exist", "tmp_dir_content": "token_found"},
        func=mktoken,
    )
    return actions


def setup_automaton(planner_type: str = "regressive"):
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
        planner_type=planner_type
    )
    return automaton


def main():
    goal = {
        "tmp_dir_state": "exist",
        "tmp_dir_content": "token_found",
    }
    # Use regressive planner by default, but you can specify "nx" to use NXPlanner
    # dir_handler = setup_automaton("nx")  # or setup_automaton("nx") to use NXPlanner
    dir_handler = setup_automaton("regressive")  # or setup_automaton("nx") to use NXPlanner
    dir_handler.goal = goal
    dir_handler.start()


if __name__ == "__main__":
    main()
