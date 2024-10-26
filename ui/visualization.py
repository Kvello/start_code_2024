from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ResultsPlotter(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Create figure with three subplots
        self.figure = Figure(figsize=(8, 10))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Create subplots
        self.power_ax = self.figure.add_subplot(311)
        self.battery_ax = self.figure.add_subplot(312)
        self.price_ax = self.figure.add_subplot(313)
        
        # Configure subplots
        self.power_ax.set_title('Power Flows')
        self.power_ax.set_ylabel('Power (kW)')
        
        self.battery_ax.set_title('Battery State of Charge')
        self.battery_ax.set_ylabel('SoC (%)')
        
        self.price_ax.set_title('Spot Prices')
        self.price_ax.set_ylabel('NOK/kWh')
        self.price_ax.set_xlabel('Time')
        
        self.figure.tight_layout()
    
    def update_plots(self, results):
        # Clear previous plots
        self.power_ax.clear()
        self.battery_ax.clear()
        self.price_ax.clear()
        
        # Plot power flows
        self.power_ax.plot(results['timestamps'], results['consumption'], 
                          'r', label='Consumption')
        self.power_ax.plot(results['timestamps'], results['solar_generation'], 
                          'y', label='Solar')
        self.power_ax.plot(results['timestamps'], results['grid_power'], 
                          'b', label='Grid')
        self.power_ax.legend()
        self.power_ax.grid(True)
        
        # Plot battery SoC
        self.battery_ax.plot(results['timestamps'], results['battery_soc'], 'g')
        self.battery_ax.grid(True)
        
        # Plot spot prices
        self.price_ax.plot(results['timestamps'], results['spot_prices'], 'k')
        self.price_ax.grid(True)
        
        # Update canvas
        self.canvas.draw()
