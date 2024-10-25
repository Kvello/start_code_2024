from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from enum import Enum
from building import BuildingType

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

def get_building_appliances(building_type: BuildingType) -> List[Appliance]:
    """Return list of typical appliances for building type"""
    
    if building_type == BuildingType.RESIDENTIAL:
        return [
            Appliance("Fridge", ApplianceType.CONSTANT, 0.1, duty_cycle=0.3),
            Appliance("Lights", ApplianceType.OCCUPANCY, 0.2),
            Appliance("TV", ApplianceType.RANDOM, 0.15),
            Appliance("Heating", ApplianceType.TEMPERATURE, 2.0, temperature_dependent=True),
            Appliance("Dishwasher", ApplianceType.SCHEDULED, 1.2, 
                     schedule=[0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0]),
            # Add more residential appliances...
        ]
    
    elif building_type == BuildingType.COMMERCIAL:
        return [
            Appliance("HVAC", ApplianceType.TEMPERATURE, 5.0, temperature_dependent=True),
            Appliance("Lighting", ApplianceType.OCCUPANCY, 1.0),
            Appliance("Computers", ApplianceType.SCHEDULED, 2.0,
                     schedule=[0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0]),
            Appliance("Servers", ApplianceType.CONSTANT, 3.0, duty_cycle=0.8),
            # Add more commercial appliances...
        ]
    
    else:  # INDUSTRIAL
        return [
            Appliance("Process Heat", ApplianceType.SCHEDULED, 10.0),
            Appliance("Ventilation", ApplianceType.CONSTANT, 5.0),
            Appliance("Machinery", ApplianceType.SCHEDULED, 15.0,
                     schedule=[0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0]),
            # Add more industrial appliances...
        ]

def simulate_consumption(
    building_type: BuildingType,
    num_occupants: int,
    floor_area: float,
    weather_data: Dict[str, List],
    is_weekend: bool
) -> List[float]:
    """
    Enhanced CREST model simulation
    
    Parameters:
        building_type: Type of building (residential/commercial/industrial)
        num_occupants: Number of occupants
        floor_area: Building floor area in m²
        weather_data: Dictionary with weather parameters
        is_weekend: Whether it's a weekend day
    """
    
    appliances = get_building_appliances(building_type)
    consumption = []
    
    # Occupancy profiles
    weekday_profile = [
        0.9, 0.9, 0.9, 0.9, 0.9, 0.8, 0.7, 0.5,  # 00-07
        0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.3,  # 08-15
        0.5, 0.7, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9   # 16-23
    ]
    
    weekend_profile = [
        0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.8, 0.8,  # 00-07
        0.7, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5,  # 08-15
        0.6, 0.7, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9   # 16-23
    ]
    
    occupancy_profile = weekend_profile if is_weekend else weekday_profile
    
    # Simulate each hour
    for i in range(len(weather_data['timestamp'])):
        hour = weather_data['timestamp'][i].hour
        temperature = weather_data['temperature'][i]
        
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
                power *= occupancy_profile[hour]
            
            # Apply schedule
            power *= appliance.schedule[hour]
            
            # Apply duty cycle
            power *= appliance.duty_cycle
            
            # Add to total load
            hour_load += power
        
        # Scale by floor area and occupants
        if building_type == BuildingType.RESIDENTIAL:
            hour_load *= (floor_area / 100) * (num_occupants / 2)  # Normalized to 100m² and 2 occupants
        else:
            hour_load *= (floor_area / 1000)  # Normalized to 1000m² for commercial/industrial
        
        # Add random variation
        hour_load *= (1 + np.random.normal(0, 0.05))
        
        consumption.append(max(0, hour_load))
    
    return consumption
