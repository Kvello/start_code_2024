from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QFormLayout, QSpinBox, 
                           QDoubleSpinBox, QPushButton)
from PyQt6.QtCore import Qt
import sys
import os
from visualization import ResultsPlotter

# Import backend functionality
import sys
sys.path.append('/Users/danielskauge/start_code_2024/src')  # Add src directory to path
from building import Building, SolarSetup
from weather import WeatherData
from consumption import simulate_simple_consumption
from solar import simulate_solar
from battery import optimize_battery
from spot_prices import get_spot_prices, get_price_area_from_location

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Building Energy Simulator")
        self.setMinimumSize(1200, 800)
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Add configuration panel
        config_panel = self.create_config_panel()
        layout.addWidget(config_panel, stretch=1)
        
        # Add results panel
        self.results_plotter = ResultsPlotter()
        layout.addWidget(self.results_plotter, stretch=2)
        
    def create_config_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form = QFormLayout()
        
        # Location
        self.lat = QDoubleSpinBox()
        self.lat.setRange(58, 71)  # Norway's latitude range
        self.lat.setDecimals(6)
        self.lon = QDoubleSpinBox()
        self.lon.setRange(4, 31)   # Norway's longitude range
        self.lon.setDecimals(6)
        form.addRow("Latitude:", self.lat)
        form.addRow("Longitude:", self.lon)
        
        # Solar setup
        self.solar_power = QDoubleSpinBox()
        self.solar_power.setRange(0, 100)
        self.solar_power.setSuffix(" kW")
        self.solar_azimuth = QSpinBox()
        self.solar_azimuth.setRange(0, 359)
        self.solar_azimuth.setSuffix("°")
        self.solar_tilt = QSpinBox()
        self.solar_tilt.setRange(0, 90)
        self.solar_tilt.setSuffix("°")
        form.addRow("Solar Peak Power:", self.solar_power)
        form.addRow("Panel Azimuth:", self.solar_azimuth)
        form.addRow("Panel Tilt:", self.solar_tilt)
        
        # Battery setup
        self.battery_capacity = QDoubleSpinBox()
        self.battery_capacity.setRange(0, 100)
        self.battery_capacity.setSuffix(" kWh")
        self.battery_power = QDoubleSpinBox()
        self.battery_power.setRange(0, 50)
        self.battery_power.setSuffix(" kW")
        form.addRow("Battery Capacity:", self.battery_capacity)
        form.addRow("Battery Max Power:", self.battery_power)
        
        layout.addLayout(form)
        
        # Run button
        run_button = QPushButton("Run Simulation")
        run_button.clicked.connect(self.run_simulation)
        layout.addWidget(run_button)
        
        return panel
    
    def run_simulation(self):
        # Create Building object from UI inputs
        solar = SolarSetup(
            peak_power_kw=self.solar_power.value(),
            azimuth_angle=self.solar_azimuth.value(),
            tilt_angle=self.solar_tilt.value()
        )
        
        building = Building(
            battery_capacity_kwh=self.battery_capacity.value(),
            battery_max_power_kw=self.battery_power.value(),
            location=(self.lat.value(), self.lon.value()),
            solar=solar
        )
        
        try:
            # Get weather forecast
            weather_data = WeatherData().get_forecast(building.location)
            
            # Run simulations
            consumption = simulate_simple_consumption(building, weather_data)
            solar_gen = simulate_solar(building.solar, weather_data, building.location)
            
            # Get spot prices
            price_area = get_price_area_from_location(*building.location)
            spot_prices = get_spot_prices(price_area)
            
            # Optimize battery
            soc, grid = optimize_battery(
                building.battery_capacity_kwh,
                building.battery_max_power_kw,
                spot_prices,
                consumption,
                solar_gen
            )
            
            # Update plots
            self.results_plotter.update_plots({
                'timestamps': weather_data['timestamp'],
                'consumption': consumption,
                'solar_generation': solar_gen,
                'battery_soc': soc,
                'grid_power': grid,
                'spot_prices': spot_prices
            })
            
        except Exception as e:
            print(f"Error running simulation: {e}")
            # TODO: Show error dialog to user

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
