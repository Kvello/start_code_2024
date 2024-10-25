from datetime import datetime
from building import Building
from weather import WeatherData
from consumption import simulate_consumption
from solar import simulate_solar
from battery import optimize_battery
from spot_prices import get_spot_prices
from visualization import plot_energy_flow

def main():
    # Initialize building
    building = Building(
        battery_capacity_kwh=10.0,
        battery_max_power_kw=5.0,
        solar_peak_kw=7.0,
        num_occupants=4,
        location=(63.4, 10.4)  # Trondheim
    )
    
    # Get weather data
    weather = WeatherData().get_forecast(building.location)
    
    # Simulate consumption
    consumption = simulate_consumption(
        building.num_occupants,
        weather['timestamp'],
        is_weekend=False
    )
    
    # Simulate solar generation
    solar = simulate_solar(
        building.solar_peak_kw,
        weather['irradiance'],
        weather['timestamp']
    )
    
    # Get spot prices
    spot_prices = get_spot_prices()
    
    # Optimize battery operation
    soc, grid = optimize_battery(
        building.battery_capacity_kwh,
        building.battery_max_power_kw,
        spot_prices,
        consumption,
        solar
    )
    
    # Visualize results
    plot_energy_flow(
        weather['timestamp'],
        consumption,
        solar,
        soc,
        grid,
        spot_prices
    )

if __name__ == "__main__":
    main()
