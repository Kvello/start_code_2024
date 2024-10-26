from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
from building import Building, BuildingType

class ApplianceType(Enum):
    CONSTANT = "constant"        # e.g., fridge
    OCCUPANCY = "occupancy"      # e.g., lights
    SCHEDULED = "scheduled"      # e.g., dishwasher
    TEMPERATURE = "temperature"  # e.g., heating/cooling
    RANDOM = "random"           # e.g., kettle, TV

class Appliance:
    def __init__(
        self,
        name: str,
        type: ApplianceType,
        rated_power: float,
        duty_cycle: float = 1.0,
        temperature_dependent: bool = False,
        occupancy_dependent: bool = False,
        schedule: Optional[List[float]] = None
    ):
        self.name = name
        self.type = type
        self.rated_power = rated_power
        self.duty_cycle = duty_cycle
        self.temperature_dependent = temperature_dependent
        self.occupancy_dependent = occupancy_dependent
        self.schedule = schedule if schedule is not None else [1.0] * 24

class TimeOfDay(Enum):
    NIGHT = "night"      # 00:00-06:00
    MORNING = "morning"  # 06:00-09:00
    DAY = "day"         # 09:00-17:00
    EVENING = "evening"  # 17:00-00:00

# Occupancy profiles for each building type and time period
OCCUPANCY_PROFILES = {
    BuildingType.RESIDENTIAL: {
        'weekday': {
            TimeOfDay.NIGHT: 0.9,    # Most people sleeping
            TimeOfDay.MORNING: 0.7,   # People getting ready
            TimeOfDay.DAY: 0.2,      # People at work
            TimeOfDay.EVENING: 0.8,   # People at home
        },
        'weekend': {
            TimeOfDay.NIGHT: 0.9,
            TimeOfDay.MORNING: 0.8,
            TimeOfDay.DAY: 0.6,
            TimeOfDay.EVENING: 0.7,
        }
    },
    BuildingType.COMMERCIAL: {
        'weekday': {
            TimeOfDay.NIGHT: 0.1,    # Security/cleaning
            TimeOfDay.MORNING: 0.6,   # Starting work
            TimeOfDay.DAY: 0.9,      # Full operation
            TimeOfDay.EVENING: 0.3,   # Some overtime
        },
        'weekend': {
            TimeOfDay.NIGHT: 0.1,
            TimeOfDay.MORNING: 0.1,
            TimeOfDay.DAY: 0.2,
            TimeOfDay.EVENING: 0.1,
        }
    },
    BuildingType.INDUSTRIAL: {
        'weekday': {
            TimeOfDay.NIGHT: 0.5,    # Night shift
            TimeOfDay.MORNING: 0.8,   # Morning shift
            TimeOfDay.DAY: 1.0,      # Peak operation
            TimeOfDay.EVENING: 0.7,   # Evening shift
        },
        'weekend': {
            TimeOfDay.NIGHT: 0.3,
            TimeOfDay.MORNING: 0.4,
            TimeOfDay.DAY: 0.5,
            TimeOfDay.EVENING: 0.3,
        }
    }
}

def get_building_appliances(building_type: BuildingType) -> List[Appliance]:
    """Return list of typical appliances for building type"""
    
    if building_type == BuildingType.RESIDENTIAL:
        return [
            Appliance("Fridge", ApplianceType.CONSTANT, rated_power=0.1, duty_cycle=0.3),
            Appliance("Lights", ApplianceType.OCCUPANCY, rated_power=0.2),
            Appliance("TV", ApplianceType.RANDOM, rated_power=0.15),
            Appliance("Heating", ApplianceType.TEMPERATURE, rated_power=2.0, temperature_dependent=True),
            Appliance("Dishwasher", ApplianceType.SCHEDULED, rated_power=1.2, 
                     schedule=[0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0]),
        ]
    
    elif building_type == BuildingType.COMMERCIAL:
        return [
            Appliance("HVAC", ApplianceType.TEMPERATURE, rated_power=5.0, temperature_dependent=True),
            Appliance("Lighting", ApplianceType.OCCUPANCY, rated_power=1.0),
            Appliance("Computers", ApplianceType.SCHEDULED, rated_power=2.0,
                     schedule=[0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0]),
            Appliance("Servers", ApplianceType.CONSTANT, rated_power=3.0, duty_cycle=0.8),
        ]
    
    else:  # INDUSTRIAL
        return [
            Appliance("Process Heat", ApplianceType.SCHEDULED, rated_power=10.0),
            Appliance("Ventilation", ApplianceType.CONSTANT, rated_power=5.0),
            Appliance("Machinery", ApplianceType.SCHEDULED, rated_power=15.0,
                     schedule=[0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0]),
        ]

def get_time_period(hour: int) -> TimeOfDay:
    """Convert hour to time period"""
    if 0 <= hour < 6:
        return TimeOfDay.NIGHT
    elif 6 <= hour < 9:
        return TimeOfDay.MORNING
    elif 9 <= hour < 17:
        return TimeOfDay.DAY
    else:
        return TimeOfDay.EVENING

def is_weekend(timestamp: datetime) -> bool:
    """Check if timestamp is on weekend"""
    return timestamp.weekday() >= 5

def simulate_consumption(
    building: Building,
    weather_forecast: Dict[str, List]
) -> List[float]:
    """
    Simulate building consumption for tomorrow using CREST model
    
    Parameters:
        building: Building configuration
        weather_forecast: Weather forecast for tomorrow
        
    Returns:
        List of hourly consumption values in kW for tomorrow (00:00-23:00)
    """
    appliances = get_building_appliances(building.building_type)
    consumption = []
    
    # Weather forecast should contain 24 hours for tomorrow
    timestamps = weather_forecast['timestamp']
    
    for i, timestamp in enumerate(timestamps):
        hour = timestamp.hour
        temperature = weather_forecast['temperature'][i]
        weekend = is_weekend(timestamp)
        
        # Get occupancy factor for this period
        time_period = get_time_period(hour)
        day_type = 'weekend' if weekend else 'weekday'
        occupancy = OCCUPANCY_PROFILES[building.building_type][day_type][time_period]
        
        # Base load for this hour
        hour_load = 0.0
        
        for appliance in appliances:
            power = appliance.rated_power
            
            # Apply temperature dependency
            if appliance.temperature_dependent:
                if temperature < 16:
                    # Heating needed
                    power *= 1 + 0.1 * (16 - temperature)
                elif temperature > 22:
                    # Cooling needed
                    power *= 1 + 0.1 * (temperature - 22)
            
            # Apply occupancy dependency
            if appliance.occupancy_dependent:
                power *= occupancy
            
            # Apply schedule
            power *= appliance.schedule[hour]
            
            # Apply duty cycle
            power *= appliance.duty_cycle
            
            # Add to total load
            hour_load += power
        
        # Scale by floor area and occupants
        if building.building_type == BuildingType.RESIDENTIAL:
            hour_load *= (building.floor_area / 100) * (building.num_occupants / 2)
        else:
            hour_load *= (building.floor_area / 1000)
        
        # Add random variation
        hour_load *= (1 + np.random.normal(0, 0.05))
        
        consumption.append(max(0, hour_load))
    
    return consumption
