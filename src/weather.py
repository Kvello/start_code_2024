from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import requests
import numpy as np
from dataclasses import dataclass

@dataclass
class WeatherData:
    """Weather data handler for Yr API"""
    
    def __init__(self):
        self.base_url = "https://api.met.no/weatherapi/locationforecast/2.0/complete"
        self.headers = {
            'User-Agent': 'BuildingEnergySimulator/1.0 (danielrs@stud.ntnu.no)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.cache = {}

    def get_forecast(self, location: Tuple[float, float]) -> Dict[str, List]:
        """
        Fetch weather forecast for next day from Yr
        Returns data for 00:00-23:00 tomorrow
        """
        lat, lon = self._round_coordinates(location)
        
        if cached_data := self._get_cached_data(lat, lon):
            return cached_data
        
        try:
            data = self._fetch_weather_data(lat, lon)
            return self._process_timeseries(data, lat, lon)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return self._generate_synthetic_data()

    def _round_coordinates(self, location: Tuple[float, float]) -> Tuple[float, float]:
        """Round coordinates to 4 decimals as per API TOS"""
        return round(location[0], 4), round(location[1], 4)

    def _get_cached_data(self, lat: float, lon: float) -> Optional[Dict[str, List]]:
        """Check and return cached data if valid"""
        cache_key = f"{lat},{lon}"
        if cache_key in self.cache:
            cached_data, expires = self.cache[cache_key]
            if datetime.now() < expires:
                return cached_data
        return None

    def _fetch_weather_data(self, lat: float, lon: float) -> Dict:
        """Fetch and cache raw weather data from API"""
        params = {'lat': lat, 'lon': lon}
        response = requests.get(self.base_url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            expires = datetime.strptime(response.headers['Expires'], '%a, %d %b %Y %H:%M:%S GMT')
            self.cache[f"{lat},{lon}"] = (data, expires)
            return data
        raise requests.exceptions.RequestException(f"API returned status code {response.status_code}")

    def _process_timeseries(self, data: Dict, lat: float, lon: float) -> Dict[str, List]:
        """Process raw API data into structured timeseries for next day"""
        tomorrow = datetime.now().date() + timedelta(days=1)
        start_time = datetime.combine(tomorrow, datetime.min.time())
        
        timeseries = data['properties']['timeseries']
        result = {
            'timestamp': [],
            'temperature': [],
            'cloud_cover': [],
            'wind_speed': [],
            'humidity': [],
            'precipitation': [],
            'pressure': []
        }
        
        # Filter and process only next day's data
        for entry in timeseries:
            time = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
            if time.date() == tomorrow:
                instant = entry['data']['instant']['details']
                
                result['timestamp'].append(time)
                result['temperature'].append(instant.get('air_temperature', 0))
                result['cloud_cover'].append(instant.get('cloud_area_fraction', 0))
                result['wind_speed'].append(instant.get('wind_speed', 0))
                result['humidity'].append(instant.get('relative_humidity', 0))
                result['pressure'].append(instant.get('air_pressure_at_sea_level', 0))
                
                # Get precipitation for next hour
                precip = entry['data'].get('next_1_hours', {}).get('details', {}).get('precipitation_amount', 0)
                result['precipitation'].append(precip)
        
        return result

    def _generate_synthetic_data(self) -> Dict[str, List]:
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
        
        for i in range(24):
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
