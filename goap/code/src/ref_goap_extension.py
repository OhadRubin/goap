
# If you use 'automat' for state machines, you can do:
# from automat import MethodicalMachine
# This code uses a simple stand-in for demonstration to mirror methodicalmachine usage.
# For a real project, install 'automat' and replace with MethodicalMachine usage.

###############################################################################
# 1) EXCEPTIONS
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


class Automaton:
    """
    Automaton with 4 states:
      - waiting_orders (initial)
      - sensing
      - planning
      - acting
    Manages a sense → plan → act loop, storing sensors, working_memory, etc.
    """

    def __init__(self, world_state: WorldState, sensors: Sensors, actions: List[Action]):
        self.state_machine = SimpleMethodicalMachine()
        self.world_state = world_state
        self.working_memory: List[Fact] = []
        self.sensors = sensors
        self.actions = actions
        self.planner = RegressivePlanner(world_state, actions)
        self.action_plan: List[PlanStep] = []
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


###############################################################################
# 14) (OPTIONAL) EXAMPLE USAGE & DEMO
###############################################################################

if __name__ == "__main__":
    # A small demo showing how you might instantiate everything.

    # 1) Define a couple of custom Actions
    class FlipTable(Action):
        effects = {
            "table_id": Ellipsis  # dynamic
        }
        preconditions = {
            "has_table": True
        }
        cost = 2.0

    class TakeCoverBehindTable(Action):
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

# End of goap_system.py
# ------------------------------------------------------------------------------
