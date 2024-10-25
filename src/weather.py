from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import requests
import numpy as np
from dataclasses import dataclass

@dataclass
class WeatherData:
    """Weather data handler with comprehensive meteorological parameters"""
    
    def __init__(self):
        self.base_url = "https://api.met.no/weatherapi/locationforecast/2.0/complete"
        self.headers = {
            'User-Agent': 'BuildingEnergySimulator/1.0'
        }

    def get_forecast(self, location: Tuple[float, float], hours: int = 24) -> Dict[str, List]:
        """Fetch comprehensive weather forecast from Yr"""
        lat, lon = location
        params = {'lat': lat, 'lon': lon}
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract timeseries from API response
            timeseries = data['properties']['timeseries']
            
            result = {
                'timestamp': [],
                'temperature': [],
                'irradiance': [],
                'cloud_cover': [],
                'wind_speed': [],
                'humidity': [],
                'precipitation': [],
                'pressure': []
            }
            
            for entry in timeseries[:hours]:
                time = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                instant = entry['data']['instant']['details']
                
                result['timestamp'].append(time)
                result['temperature'].append(instant.get('air_temperature', 0))
                result['cloud_cover'].append(instant.get('cloud_area_fraction', 0))
                result['wind_speed'].append(instant.get('wind_speed', 0))
                result['humidity'].append(instant.get('relative_humidity', 0))
                result['pressure'].append(instant.get('air_pressure_at_sea_level', 0))
                
                # Calculate irradiance based on cloud cover and solar position
                irradiance = self._calculate_irradiance(time, lat, lon, 
                                                      instant.get('cloud_area_fraction', 0))
                result['irradiance'].append(irradiance)
                
                # Get precipitation for next hour
                if 'next_1_hours' in entry['data']:
                    precip = entry['data']['next_1_hours']['details']['precipitation_amount']
                else:
                    precip = 0
                result['precipitation'].append(precip)
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return self._generate_synthetic_data(hours)
    
    def _calculate_irradiance(self, time: datetime, lat: float, lon: float, 
                            cloud_cover: float) -> float:
        """Calculate solar irradiance based on position and cloud cover"""
        # This is a simplified model - could be enhanced with proper astronomical calculations
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
    
    def _generate_synthetic_data(self, hours: int) -> Dict[str, List]:
        """Generate synthetic weather data for testing"""
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        result = {
            'timestamp': [],
            'temperature': [],
            'irradiance': [],
            'cloud_cover': [],
            'wind_speed': [],
            'humidity': [],
            'precipitation': [],
            'pressure': []
        }
        
        for i in range(hours):
            time = now + timedelta(hours=i)
            hour = time.hour
            
            result['timestamp'].append(time)
            result['temperature'].append(20 + 5 * np.sin(i * np.pi/12))
            result['irradiance'].append(max(0, np.sin(i * np.pi/12) * 1000))
            result['cloud_cover'].append(np.random.uniform(0, 100))
            result['wind_speed'].append(np.random.uniform(0, 10))
            result['humidity'].append(np.random.uniform(30, 90))
            result['precipitation'].append(max(0, np.random.normal(0, 0.5)))
            result['pressure'].append(1013 + np.random.normal(0, 5))
            
        return result
