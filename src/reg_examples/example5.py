from src.goap import AutomatonController, RegAction, RegSensor, RegGoal
from dataclasses import dataclass
from math import sqrt
import fire


@dataclass
class Position:
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def direction_to(self, other: 'Position') -> 'Position':
        dx = other.x - self.x
        dy = other.y - self.y
        dist = self.distance_to(other)
        if dist == 0:
            return Position(0, 0)
        return Position(dx/dist, dy/dist)


class WorldState:
    """Manages the state of the world including positions and resources"""
    _positions = {
        "agent": Position(0, 0),
        "food": Position(10, 10),
        "shelter": Position(-10, 5),
        "water": Position(5, -10),
    }
    
    _resources = {
        "hunger": 75,  # 0-100 scale
        "thirst": 60,  # 0-100 scale
        "energy": 80,  # 0-100 scale
        "shelter_built": False
    }
    
    @classmethod
    def get_position(cls, entity: str) -> Position:
        return cls._positions.get(entity)
    
    @classmethod
    def set_position(cls, entity: str, pos: Position):
        cls._positions[entity] = pos
        
    @classmethod
    def get_resource(cls, resource: str) -> float:
        return cls._resources.get(resource, 0)
    
    @classmethod
    def set_resource(cls, resource: str, value: float):
        cls._resources[resource] = value
    
    @classmethod
    def get_state(cls, key: str, default=None):
        if key in cls._resources:
            return cls._resources[key]
        return default
    
    @classmethod
    def set_state(cls, key: str, value):
        cls._resources[key] = value
    
    @classmethod
    def get_elements(cls, element_type: str) -> list:
        if element_type == "food":
            return [cls._positions["food"]] if "food" in cls._positions else []
        elif element_type == "water":
            return [cls._positions["water"]] if "water" in cls._positions else []
        elif element_type == "shelter":
            return [cls._positions["shelter"]] if "shelter" in cls._positions else []
        return []


class MovableAction(RegAction):
    """Base class for actions that involve movement"""
    def move_to(self, current_pos: Position, target_pos: Position, speed: float = 1.0) -> Position:
        direction = current_pos.direction_to(target_pos)
        new_x = current_pos.x + direction.x * speed
        new_y = current_pos.y + direction.y * speed
        return Position(new_x, new_y)
    
    def get_clazz(self):
        return self.__class__.__name__


# Sensors
class HungerSensor(RegSensor):
    binding = "hunger"
    
    def exec(self):
        return WorldState.get_resource("hunger")


class ThirstSensor(RegSensor):
    binding = "thirst"
    
    def exec(self):
        return WorldState.get_resource("thirst")


class EnergySensor(RegSensor):
    binding = "energy"
    
    def exec(self):
        return WorldState.get_resource("energy")


class PositionSensor(RegSensor):
    binding = "position"
    
    def exec(self):
        return WorldState.get_position("agent")


# Actions
class FindFoodAction(MovableAction):
    def get_cost(self, _blackboard) -> int:
        return 1
    
    def get_preconditions(self) -> dict:
        return {"hunger": lambda x: x > 50}
    
    def get_effects(self) -> dict:
        return {"is_hungry": False}
    
    def perform(self, actor, delta) -> bool:
        agent_pos = WorldState.get_position("agent")
        food_pos = WorldState.get_position("food")
        
        if agent_pos.distance_to(food_pos) < 2:
            WorldState.set_resource("hunger", max(0, WorldState.get_resource("hunger") - 30))
            print("Found food and eating - hunger reduced")
            return True
            
        new_pos = self.move_to(agent_pos, food_pos)
        WorldState.set_position("agent", new_pos)
        print(f"Moving towards food at {food_pos}")
        return False


class DrinkWaterAction(MovableAction):
    def get_cost(self, _blackboard) -> int:
        return 1
    
    def get_preconditions(self) -> dict:
        return {"thirst": lambda x: x > 50}
    
    def get_effects(self) -> dict:
        return {"is_thirsty": False}
    
    def perform(self, actor, delta) -> bool:
        agent_pos = WorldState.get_position("agent")
        water_pos = WorldState.get_position("water")
        
        if agent_pos.distance_to(water_pos) < 2:
            WorldState.set_resource("thirst", max(0, WorldState.get_resource("thirst") - 40))
            print("Found water and drinking - thirst reduced")
            return True
            
        new_pos = self.move_to(agent_pos, water_pos)
        WorldState.set_position("agent", new_pos)
        print(f"Moving towards water at {water_pos}")
        return False


class RestAction(MovableAction):
    def get_cost(self, _blackboard) -> int:
        return 1
    
    def get_preconditions(self) -> dict:
        return {"energy": lambda x: x < 40}
    
    def get_effects(self) -> dict:
        return {"is_tired": False}
    
    def perform(self, actor, delta) -> bool:
        agent_pos = WorldState.get_position("agent")
        shelter_pos = WorldState.get_position("shelter")
        
        if agent_pos.distance_to(shelter_pos) < 2:
            WorldState.set_resource("energy", min(100, WorldState.get_resource("energy") + 50))
            print("Resting at shelter - energy restored")
            return True
            
        new_pos = self.move_to(agent_pos, shelter_pos)
        WorldState.set_position("agent", new_pos)
        print(f"Moving towards shelter at {shelter_pos}")
        return False


# Goals
class SatisfyHungerGoal(RegGoal):
    def get_clazz(self):
        return "SatisfyHungerGoal"
    
    def is_valid(self) -> bool:
        return WorldState.get_state("hunger", 0) > 50 and len(WorldState.get_elements("food")) > 0
    
    def priority(self) -> int:
        return 3 if WorldState.get_state("hunger", 0) > 80 else 2
    
    def get_desired_state(self) -> dict:
        return {"is_hungry": False}


class SatisfyThirstGoal(RegGoal):
    def get_clazz(self):
        return "SatisfyThirstGoal"
    
    def is_valid(self) -> bool:
        return WorldState.get_state("thirst", 0) > 50 and len(WorldState.get_elements("water")) > 0
    
    def priority(self) -> int:
        return 3 if WorldState.get_state("thirst", 0) > 80 else 1
    
    def get_desired_state(self) -> dict:
        return {"is_thirsty": False}


class RestGoal(RegGoal):
    def get_clazz(self):
        return "RestGoal"
    
    def is_valid(self) -> bool:
        return WorldState.get_state("energy", 0) < 40 and len(WorldState.get_elements("shelter")) > 0
    
    def priority(self) -> int:
        return 2 if WorldState.get_state("energy", 0) < 20 else 1
    
    def get_desired_state(self) -> dict:
        return {"is_tired": False}


def start():
    """Run a survival scenario where an agent manages hunger, thirst, and rest"""
    world_state = {
        "is_hungry": True,
        "is_thirsty": True,
        "is_tired": False,
        "hunger": WorldState.get_resource("hunger"),
        "thirst": WorldState.get_resource("thirst"),
        "energy": WorldState.get_resource("energy")
    }

    agent = AutomatonController(
        name="survival_agent",
        actions=[FindFoodAction(), DrinkWaterAction(), RestAction()],
        sensors=[HungerSensor(), ThirstSensor(), EnergySensor(), PositionSensor()],
        world_state=world_state,
        possible_goals=[SatisfyHungerGoal(), SatisfyThirstGoal(), RestGoal()]
    )
    
    print("Starting survival scenario...")
    print(f"Initial state: Hunger={WorldState.get_resource('hunger')}, "
          f"Thirst={WorldState.get_resource('thirst')}, "
          f"Energy={WorldState.get_resource('energy')}")
    
    agent.start()


if __name__ == "__main__":
    fire.Fire({"start": start})
