#!/usr/bin/env python3
"""
GOAP Example 10: Emergency Response System with Priority Overrides

This example demonstrates Agent 5's emergency response innovation: a system
that can immediately override normal activities when critical situations arise,
with automatic recovery and return to normal operations.

Key Concepts:
- Emergency goals with ultra-high priorities
- Immediate interruption of normal activities
- Context-aware emergency detection
- Automatic recovery and cleanup procedures
- Graceful return to normal operations

Run: python src/reg_examples/example10.py
"""

import time
import random
from typing import Dict, Any, List
from src.regressive_planner import RegAction, RegGoal, RegSensor
from src.goap import AutomatonController

# =============================================================================
# EMERGENCY SITUATION SIMULATION
# =============================================================================

class EmergencyWorld:
    """Simulates a world where various emergencies can occur."""
    
    def __init__(self):
        # Current emergencies
        self.active_emergencies = set()
        
        # Agent status
        self.health = 100
        self.location = "safe_area"
        self.equipment_status = "functional"
        
        # Environment
        self.weather = "clear"
        self.structural_integrity = 100
        self.resource_status = "abundant"
        
        # Activity state
        self.current_activity = "routine_work"
        self.activity_progress = 0
        self.interrupted_activity = None
        
        # Emergency triggers
        self.emergency_types = [
            "health_critical",
            "fire_outbreak", 
            "structural_damage",
            "resource_depletion",
            "equipment_failure",
            "severe_weather"
        ]
        
        self.time_step = 0
        self.recovery_progress = {}
    
    def advance_time(self):
        """Advance simulation and possibly trigger emergencies."""
        self.time_step += 1
        
        # Random emergency generation
        if random.random() < 0.15:  # 15% chance per cycle
            self.trigger_random_emergency()
        
        # Random emergency resolution
        if random.random() < 0.1:  # 10% chance per cycle
            self.resolve_random_emergency()
        
        # Natural degradation
        if random.random() < 0.05:
            self.health = max(10, self.health - random.randint(5, 15))
        
        if random.random() < 0.03:
            self.structural_integrity = max(0, self.structural_integrity - random.randint(10, 20))
    
    def trigger_random_emergency(self):
        """Trigger a random emergency."""
        emergency = random.choice(self.emergency_types)
        
        if emergency == "health_critical":
            self.health = random.randint(5, 25)
            self.active_emergencies.add("health_critical")
        elif emergency == "fire_outbreak":
            self.active_emergencies.add("fire_outbreak")
            self.location = "danger_zone"
        elif emergency == "structural_damage":
            self.structural_integrity = random.randint(10, 40)
            self.active_emergencies.add("structural_damage")
        elif emergency == "resource_depletion":
            self.resource_status = "critical"
            self.active_emergencies.add("resource_depletion")
        elif emergency == "equipment_failure":
            self.equipment_status = "damaged"
            self.active_emergencies.add("equipment_failure")
        elif emergency == "severe_weather":
            self.weather = "storm"
            self.active_emergencies.add("severe_weather")
        
        print(f"🚨 EMERGENCY: {emergency}")
    
    def resolve_random_emergency(self):
        """Randomly resolve an active emergency."""
        if self.active_emergencies:
            emergency = random.choice(list(self.active_emergencies))
            self.active_emergencies.remove(emergency)
            print(f"✅ RESOLVED: {emergency}")
    
    def get_emergency_level(self) -> str:
        """Assess overall emergency level."""
        if len(self.active_emergencies) >= 3:
            return "critical"
        elif len(self.active_emergencies) >= 1:
            return "active"
        else:
            return "none"

# Global emergency world
emergency_world = EmergencyWorld()

# =============================================================================
# EMERGENCY RESPONSE ACTIONS
# =============================================================================

class SeekMedicalHelpAction(RegAction):
    """Emergency medical response."""
    preconditions = {"health_below_30": True}
    effects = {"health_below_30": False}
    cost = 1.0  # Low cost for emergency actions
    
    def exec(self):
        emergency_world.health = min(100, emergency_world.health + 40)  # More effective healing
        if "health_critical" in emergency_world.active_emergencies:
            emergency_world.active_emergencies.remove("health_critical")
        print("🏥 Seeking emergency medical help! Health restored.")

class EvacuateAreaAction(RegAction):
    """Evacuate from dangerous area."""
    preconditions = {"location_dangerous": True}
    effects = {"location_dangerous": False}
    cost = 1.0
    
    def exec(self):
        emergency_world.location = "safe_area"
        if "fire_outbreak" in emergency_world.active_emergencies:
            emergency_world.active_emergencies.remove("fire_outbreak")
        print("🏃 Evacuating to safe area!")

class EmergencyRepairAction(RegAction):
    """Emergency structural repairs."""
    preconditions = {"structure_below_50": True}
    effects = {"structure_below_50": False}
    cost = 2.0
    
    def exec(self):
        emergency_world.structural_integrity = min(100, emergency_world.structural_integrity + 60)
        if "structural_damage" in emergency_world.active_emergencies:
            emergency_world.active_emergencies.remove("structural_damage")
        print("🔧 Performing emergency structural repairs!")

class SecureResourcesAction(RegAction):
    """Secure critical resources during shortage."""
    preconditions = {"resources_low": True}
    effects = {"resources_low": False}
    cost = 3.0
    
    def exec(self):
        emergency_world.resource_status = "low"
        if "resource_depletion" in emergency_world.active_emergencies:
            emergency_world.active_emergencies.remove("resource_depletion")
        print("📦 Securing critical resources from emergency stores!")

class FixEquipmentAction(RegAction):
    """Emergency equipment repair."""
    preconditions = {"equipment_broken": True}
    effects = {"equipment_broken": False}
    cost = 2.0
    
    def exec(self):
        emergency_world.equipment_status = "functional"
        if "equipment_failure" in emergency_world.active_emergencies:
            emergency_world.active_emergencies.remove("equipment_failure")
        print("⚒️ Emergency equipment repair completed!")

class TakeStormShelterAction(RegAction):
    """Take shelter during severe weather."""
    preconditions = {"weather_dangerous": True}
    effects = {"weather_dangerous": False}
    cost = 1.0
    
    def exec(self):
        if "severe_weather" in emergency_world.active_emergencies:
            emergency_world.active_emergencies.remove("severe_weather")
        print("🏠 Taking shelter from severe weather!")

# =============================================================================
# NORMAL ACTIVITY ACTIONS
# =============================================================================

class ContinueRoutineWorkAction(RegAction):
    """Continue normal work activities."""
    preconditions = {}
    effects = {"work_progress": True}
    cost = 2.0
    
    def exec(self):
        emergency_world.activity_progress += 10
        emergency_world.current_activity = "routine_work"
        print("💼 Continuing routine work activities...")

class PerformMaintenanceAction(RegAction):
    """Perform regular maintenance."""
    preconditions = {}
    effects = {"maintenance_complete": True}
    cost = 3.0
    
    def exec(self):
        emergency_world.current_activity = "maintenance"
        print("🔧 Performing regular maintenance...")

class RestAndRecoverAction(RegAction):
    """Rest and recover after emergencies."""
    preconditions = {}
    effects = {"recovered": True}
    cost = 1.0
    
    def exec(self):
        emergency_world.health = min(100, emergency_world.health + 10)
        emergency_world.current_activity = "recovery"
        print("😌 Resting and recovering from recent emergencies...")

class ResumeInterruptedActivityAction(RegAction):
    """Resume activity that was interrupted by emergency."""
    preconditions = {}
    effects = {"activity_resumed": True}
    cost = 1.5
    
    def exec(self):
        if emergency_world.interrupted_activity:
            emergency_world.current_activity = emergency_world.interrupted_activity
            emergency_world.interrupted_activity = None
            print(f"🔄 Resuming interrupted activity: {emergency_world.current_activity}")

class DeclareAllClearAction(RegAction):
    """Declare area safe when all emergencies resolved."""
    preconditions = {}
    effects = {"safe": True}
    cost = 0.5
    
    def exec(self):
        print("✅ All emergencies resolved - Area declared safe!")


# =============================================================================
# EMERGENCY RESPONSE GOALS
# =============================================================================

class HealthEmergencyGoal(RegGoal):
    """Ultra-high priority health emergency response."""
    preconditions = {}
    desired_state = {"health_below_30": False}
    priority = 200  # Ultra-high emergency priority
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when health is critically low."""
        return world_state.get("health_below_30", False)
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Maximum priority for health emergencies."""
        if world_state.get("health_below_30", False):
            return 200  # Always highest priority
        return 0

class SafetyEmergencyGoal(RegGoal):
    """High priority safety emergency response."""
    preconditions = {}
    desired_state = {"location_dangerous": False, "weather_dangerous": False}
    priority = 180
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when in dangerous location or situation."""
        return (world_state.get("location_dangerous", False) or 
                world_state.get("weather_dangerous", False))
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """High priority for safety emergencies."""
        if world_state.get("location_dangerous", False):
            return 180
        elif world_state.get("weather_dangerous", False):
            return 150
        return 0

class StructuralEmergencyGoal(RegGoal):
    """High priority structural emergency response."""
    preconditions = {}
    desired_state = {"structure_below_50": False}
    priority = 160
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when structural damage is detected."""
        return world_state.get("structure_below_50", False)
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Priority based on damage severity."""
        if world_state.get("structure_below_50", False):
            return 160
        return 0

class ResourceEmergencyGoal(RegGoal):
    """Medium-high priority resource emergency response."""
    preconditions = {}
    desired_state = {"resources_low": False}
    priority = 140
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when resources are critically low."""
        return world_state.get("resources_low", False)
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Priority for resource emergencies."""
        if world_state.get("resources_low", False):
            return 140
        return 0

class EquipmentEmergencyGoal(RegGoal):
    """Medium priority equipment emergency response."""
    preconditions = {}
    desired_state = {"equipment_broken": False}
    priority = 120
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when equipment has failed."""
        return world_state.get("equipment_broken", False)
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Priority for equipment failures."""
        if world_state.get("equipment_broken", False):
            return 120
        return 0

class NormalOperationsGoal(RegGoal):
    """Low priority normal operations - always valid as fallback."""
    preconditions = {}
    desired_state = {"work_progress": True}
    priority = 10
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Always valid - serves as fallback when no emergencies need attention."""
        return True
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Higher priority when no emergencies, lower when emergencies exist."""
        if world_state.get("no_emergencies", False):
            return 15  # Normal priority when safe
        else:
            return 5   # Low priority during emergencies (but still valid)

class OverallSafetyGoal(RegGoal):
    """Achieve overall safety when all emergencies resolved."""
    preconditions = {}
    desired_state = {"safe": True}
    priority = 50
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when there are unresolved emergency conditions but no active emergencies."""
        return (world_state.get("no_emergencies", False) and
                not world_state.get("safe", False))
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Medium priority for achieving overall safety."""
        if world_state.get("no_emergencies", False) and not world_state.get("safe", False):
            return 50
        return 0

class RecoveryGoal(RegGoal):
    """Recovery goal after emergencies are resolved."""
    preconditions = {}
    desired_state = {"recovered": True}
    priority = 25
    
    def is_valid(self, world_state: Dict[str, Any]) -> bool:
        """Valid when emergencies have been resolved but recovery needed."""
        return (world_state.get("emergencies_resolved", False) and
                not world_state.get("recovered", True))
    
    def get_priority(self, world_state: Dict[str, Any]) -> int:
        """Medium priority for recovery."""
        if self.is_valid(world_state):
            return 25
        return 0

# =============================================================================
# EMERGENCY DETECTION SENSORS
# =============================================================================

class HealthCriticalSensor(RegSensor):
    """Monitors if health is critical."""
    binding = "health_critical"
    
    def exec(self):
        health_critical = emergency_world.health < 30
        if health_critical:
            print(f"⚠️ Health critical: {emergency_world.health}/100")
        return health_critical

class DangerSensor(RegSensor):
    """Monitors if in dangerous location."""
    binding = "in_danger"
    
    def exec(self):
        return emergency_world.location == "danger_zone"

class SevereWeatherSensor(RegSensor):
    """Monitors severe weather conditions."""
    binding = "severe_weather"
    
    def exec(self):
        return "severe_weather" in emergency_world.active_emergencies

class StructuralDamageSensor(RegSensor):
    """Monitors structural damage."""
    binding = "structural_damage"
    
    def exec(self):
        structural_damage = emergency_world.structural_integrity < 50
        if structural_damage:
            print(f"⚠️ Structural damage: {emergency_world.structural_integrity}/100")
        return structural_damage

class ResourceCriticalSensor(RegSensor):
    """Monitors critical resource levels."""
    binding = "resource_critical"
    
    def exec(self):
        resource_critical = emergency_world.resource_status == "critical"
        if resource_critical:
            print("⚠️ Resource levels critical!")
        return resource_critical

class EquipmentFailedSensor(RegSensor):
    """Monitors equipment failures."""
    binding = "equipment_failed"
    
    def exec(self):
        equipment_failed = emergency_world.equipment_status != "functional"
        if equipment_failed:
            print(f"⚠️ Equipment failure: {emergency_world.equipment_status}")
        return equipment_failed

class NoEmergenciesSensor(RegSensor):
    """Monitors if no emergencies are active."""
    binding = "no_emergencies"
    
    def exec(self):
        return len(emergency_world.active_emergencies) == 0

class SafeSensor(RegSensor):
    """Monitors overall safety status."""
    binding = "safe"
    
    def exec(self):
        return len(emergency_world.active_emergencies) == 0

class EmergenciesResolvedSensor(RegSensor):
    """Monitors if emergencies resolved but recovery needed."""
    binding = "emergencies_resolved"
    
    def exec(self):
        has_emergencies = len(emergency_world.active_emergencies) > 0
        return not has_emergencies and emergency_world.health < 90

class RecoveredSensor(RegSensor):
    """Monitors if fully recovered."""
    binding = "recovered"
    
    def exec(self):
        return emergency_world.health > 90

class ActivityInterruptedSensor(RegSensor):
    """Monitors if activity was interrupted."""
    binding = "activity_interrupted"
    
    def exec(self):
        return emergency_world.interrupted_activity is not None

class HealthBelow30Sensor(RegSensor):
    """Monitors if health is below 30."""
    binding = "health_below_30"
    
    def exec(self):
        return emergency_world.health < 30

class LocationDangerousSensor(RegSensor):
    """Monitors if location is dangerous."""
    binding = "location_dangerous"
    
    def exec(self):
        return emergency_world.location == "danger_zone"

class StructureBelow50Sensor(RegSensor):
    """Monitors if structure integrity is below 50."""
    binding = "structure_below_50"
    
    def exec(self):
        return emergency_world.structural_integrity < 50

class ResourcesLowSensor(RegSensor):
    """Monitors if resources are low."""
    binding = "resources_low"
    
    def exec(self):
        return emergency_world.resource_status == "critical"

class EquipmentBrokenSensor(RegSensor):
    """Monitors if equipment is broken."""
    binding = "equipment_broken"
    
    def exec(self):
        return emergency_world.equipment_status != "functional"

class WeatherDangerousSensor(RegSensor):
    """Monitors if weather is dangerous."""
    binding = "weather_dangerous"
    
    def exec(self):
        return "severe_weather" in emergency_world.active_emergencies

# =============================================================================
# EXAMPLE EXECUTION
# =============================================================================

def example_10():
    """Demonstrate emergency response system with priority overrides."""
    
    print("=== GOAP Example 10: Emergency Response System ===")
    print("This example shows how emergency goals can immediately override")
    print("normal activities, handle crises, and gracefully return to normal.\n")
    
    # Initial world state - normal conditions
    world_state = {
        "health_critical": False,
        "in_danger": False,
        "severe_weather": False,
        "structural_damage": False,
        "resource_critical": False,
        "equipment_failed": False,
        "no_emergencies": True,
        "emergency_level": "none",
        "safe": True,
        "activity_interrupted": False,
        "emergencies_resolved": False,
        "recovered": True,
        "health_level": 100,
        "location": "safe_area",
        # Goal state properties
        "health_treated": True,
        "in_safe_location": True,
        "structure_stabilized": True,
        "resources_secured": True,
        "equipment_functional": True,
        "work_progress": False,
        "maintenance_complete": False,
        "activity_resumed": False,
        "sheltered": True,
        # Action precondition properties
        "health_below_30": False,
        "location_dangerous": False,
        "structure_below_50": False,
        "resources_low": False,
        "equipment_broken": False,
        "weather_dangerous": False,
    }
    
    # Create actions
    actions = [
        # Emergency response actions
        SeekMedicalHelpAction(),
        EvacuateAreaAction(),
        EmergencyRepairAction(),
        SecureResourcesAction(),
        FixEquipmentAction(),
        TakeStormShelterAction(),
        # Normal activity actions
        ContinueRoutineWorkAction(),
        PerformMaintenanceAction(),
        RestAndRecoverAction(),
        ResumeInterruptedActivityAction(),
        DeclareAllClearAction(),
    ]
    
    # Create emergency response goals (with priority hierarchy)
    goals = [
        HealthEmergencyGoal(),      # Priority 200 - Critical
        SafetyEmergencyGoal(),      # Priority 180 - High  
        StructuralEmergencyGoal(),  # Priority 160 - High
        ResourceEmergencyGoal(),    # Priority 140 - Medium-High
        EquipmentEmergencyGoal(),   # Priority 120 - Medium
        OverallSafetyGoal(),        # Priority 50  - Medium
        RecoveryGoal(),             # Priority 25  - Low-Medium
        NormalOperationsGoal()      # Priority 5-15 - Fallback/Low
    ]
    
    # Create sensors
    sensors = [
        HealthCriticalSensor(),
        DangerSensor(),
        SevereWeatherSensor(),
        StructuralDamageSensor(),
        ResourceCriticalSensor(),
        EquipmentFailedSensor(),
        NoEmergenciesSensor(),
        SafeSensor(),
        EmergenciesResolvedSensor(),
        RecoveredSensor(),
        ActivityInterruptedSensor(),
        # Action precondition sensors
        HealthBelow30Sensor(),
        LocationDangerousSensor(),
        StructureBelow50Sensor(),
        ResourcesLowSensor(),
        EquipmentBrokenSensor(),
        WeatherDangerousSensor()
    ]
    
    print("Starting emergency response simulation...")
    print(f"Initial status: Health={emergency_world.health}, Location={emergency_world.location}")
    print(f"Active emergencies: {emergency_world.active_emergencies}")
    print()
    
    # Create controller
    controller = AutomatonController(
        name="emergency_response_system",
        actions=actions,
        sensors=sensors,
        world_state=world_state,
        possible_goals=goals
    )
    
    print("Running emergency response simulation...")
    print("Watch how emergency goals immediately override normal activities!")
    print("(Ctrl+C to stop)\n")
    
    # Start a background thread to advance the emergency world
    import threading
    def advance_world():
        while True:
            time.sleep(1.5)
            emergency_world.advance_time()
    
    world_thread = threading.Thread(target=advance_world, daemon=True)
    world_thread.start()
    
    # Use the intended API - let the controller handle everything
    controller.start()
    
    print("\n=== Key Insights ===")
    print("1. Emergency goals immediately override normal activities")
    print("2. Ultra-high priorities (200) ensure critical responses")
    print("3. Multiple emergency types are handled with appropriate priorities")
    print("4. System automatically returns to normal operations after emergencies")
    print("5. Recovery phases bridge emergency response and normal operations")
    print("6. Interrupted activities can be intelligently resumed")

if __name__ == "__main__":
    example_10()