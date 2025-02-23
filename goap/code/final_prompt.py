
```
class NXActions:

    def __init__(self, actions: List[NXAction] = None):
        self.actions = actions if actions else []

    def __str__(self):
        names = [action.name for action in self.actions]
        return "{}".format(names)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.actions)

    def __len__(self):
        if self.actions:
            return len(self.actions)
        else:
            return 0

    def __getitem__(self, key: str) -> Optional[NXAction]:
        for action in self.actions:
            if action.name == key:
                return action
            else:
                return None

    def get(self, name: str) -> Optional[NXAction]:
        result = None
        if not self.actions:
            return result

        for action in self.actions:
            if action.name == name:
                result = action

        return result

    def get_by_conditions(self, conditions: dict) -> Optional[List[NXAction]]:
        result = []
        for action in self.actions:
            if action.conditions == conditions:
                result.append(action)
        return result

    def get_by_effects(self, effects: dict) -> Optional[List[NXAction]]:
        result = []
        for action in self.actions:
            if action.effects == effects:
                result.append(action)
        return result

    def add(
        self,
        name: str,
        conditions: dict,
        effects: dict,
        func: Callable,
        cost: float = 0.1,
    ):
        if self.get(name):
            raise ActionAlreadyInCollectionError(
                f"The action name {name} is already in use"
            )
        self.actions.append(NXAction(func, name, conditions, effects, cost))

    def remove(self, name: str):
        result = False
        if not self.actions:
            return result
        action = self.get(name)
        if action:
            self.actions.remove(action)
            result = True
        return result

    def run_all(self) -> list:
        responses = [action.exec() for action in self.actions]
        return responses

    @staticmethod
    def compare_actions(action1: NXAction, action2: NXAction) -> bool:
        result = False
        if (
            action1.conditions == action2.conditions
            and action1.effects == action2.effects
        ):
            result = True

        return result


class NXPlanner(object):

    def __init__(self, actions: Actions):
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

    def __generate_states(self, actions: Actions, world_state: dict, goal: dict):
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
        self, name: str, sensors: Sensors, actions: NXActions, world_state_facts: dict
    ):
        # setup
        self.world_state = WorldState(world_state_facts)
        self.working_memory = []
        self.name = name
        self.sensors = sensors
        self.actions = actions
        self.planner = NXPlanner(actions=actions)
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
        self, actions: NXActions, sensors: Sensors, name: str, world_state: dict
    ):
        self.automaton = Automaton(
            actions=actions, sensors=sensors, name=name, world_state_facts=world_state
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
            self.response = (stdout, stderr, return_code)
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


def setup_automaton():
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

```


This is how RegressivePlanner is used:
    
```

"""
Sometimes we also want to pass the service value to another dependent action.
In this example, the `PerformMagic` action requires two service (actions),
`chant_incantation` and `cast_spell`, and passes the `performs_magic` effect value
to both of them using `reference`.
"""

Action = RegressiveAction
class HauntWithMagic(Action):
    effects = dict(is_spooky=True)
    preconditions = dict(is_undead=True, performs_magic="abracadabra")


class BecomeUndead(Action):
    effects = dict(is_undead=True)
    preconditions = dict(is_undead=False)


class PerformMagic(Action):
    effects = dict(performs_magic=...)
    preconditions = dict(
        chant_incantation=reference("performs_magic"),
        cast_spell=reference("performs_magic"),
    )


class ChantIncantation(Action):
    effects = dict(chant_incantation=...)
    preconditions = {}


class CastSpell(Action):
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


```

I would like to replace NXPlanner with RegressionPlanner and RegressiveAction. 
I want to reuse as much code as possible.
Please advise.