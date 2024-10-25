from typing import List, Dict
from datetime import datetime
import numpy as np

def simulate_solar(
    solar_setup: 'SolarSetup',
    weather_data: Dict[str, List],
) -> List[float]:
    """
    Simulate solar panel power generation with detailed physics model
    
    Takes into account:
    - Panel orientation (azimuth and tilt)
    - Temperature effects
    - Cloud cover
    - Air mass effects
    - Diffuse radiation
    """
    generation = []
    
    for i in range(len(weather_data['timestamp'])):
        # Get weather parameters
        time = weather_data['timestamp'][i]
        temp = weather_data['temperature'][i]
        irr = weather_data['irradiance'][i]
        clouds = weather_data['cloud_cover'][i]
        
        # Calculate incident angle modifier
        iam = _calculate_iam(time, solar_setup.azimuth_angle, solar_setup.tilt_angle)
        
        # Calculate temperature effect
        temp_factor = 1 + solar_setup.temp_coefficient * (temp - 25) / 100
        
        # Calculate total irradiance (direct + diffuse)
        diffuse_ratio = min(1.0, clouds / 100 + 0.2)  # More clouds = more diffuse
        direct_irr = irr * (1 - diffuse_ratio) * iam
        diffuse_irr = irr * diffuse_ratio * ((1 + np.cos(np.radians(solar_setup.tilt_angle))) / 2)
        total_irr = direct_irr + diffuse_irr
        
        # Calculate power
        power = (solar_setup.peak_power_kw * (total_irr / 1000) * 
                temp_factor * solar_setup.efficiency)
        
        # Add small random variations for micro-effects
        power *= (1 + np.random.normal(0, 0.02))
        generation.append(max(0, power))
    
    return generation

def _calculate_iam(time: datetime, azimuth: float, tilt: float) -> float:
    """Calculate incident angle modifier based on solar position"""
    # This is a simplified model - could be enhanced with proper astronomical calculations
    hour = time.hour
    day_of_year = time.timetuple().tm_yday
    
    # Approximate solar position
    solar_noon = 12
    day_length = 12 + 4 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    sunrise = solar_noon - day_length/2
    sunset = solar_noon + day_length/2
    
    if hour < sunrise or hour > sunset:
        return 0
    
    # Simple cosine approximation
    time_angle = np.pi * (hour - sunrise) / (sunset - sunrise)
    panel_factor = np.cos(np.radians(tilt)) + np.cos(np.radians(azimuth - 180))
    
    return max(0, np.sin(time_angle) * panel_factor / 2)
