from datetime import datetime
import numpy as np

def calculate_irradiance(time: datetime, lat: float, lon: float, cloud_cover: float) -> float:
    """
    Calculate solar irradiance based on position and cloud cover
    
    Parameters:
        time: Timestamp
        lat: Latitude in degrees
        lon: Longitude in degrees
        cloud_cover: Cloud coverage percentage (0-100)
    
    Returns:
        Calculated irradiance in W/m²
    """
    hour = time.hour
    day_of_year = time.timetuple().tm_yday
    
    # Basic solar position
    solar_noon = 12
    day_length = 12 + 4 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    sunrise = solar_noon - day_length/2
    sunset = solar_noon + day_length/2
    
    if hour < sunrise or hour > sunset:
        return 0
    
    # Maximum theoretical irradiance
    max_irradiance = 1000  # W/m²
    
    # Time factor (0-1)
    time_factor = np.sin(np.pi * (hour - sunrise) / (sunset - sunrise))
    
    # Cloud factor (0-1)
    cloud_factor = 1 - (cloud_cover / 100) * 0.75  # Clouds block up to 75% of radiation
    
    return max_irradiance * time_factor * cloud_factor
