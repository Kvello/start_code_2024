from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def plot_energy_flow(
    timestamps: List[datetime],
    consumption: List[float],
    solar_generation: List[float],
    battery_soc: List[float],
    grid_power: List[float],
    spot_prices: List[float]
) -> None:
    """Create comprehensive energy flow visualization"""
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Power flows
    ax1.plot(timestamps, consumption, 'r', label='Consumption')
    ax1.plot(timestamps, solar_generation, 'y', label='Solar Generation')
    ax1.plot(timestamps, grid_power, 'b', label='Grid Power')
    ax1.set_ylabel('Power (kW)')
    ax1.legend()
    ax1.grid(True)
    
    # Battery state
    ax2.plot(timestamps, battery_soc, 'g')
    ax2.set_ylabel('Battery SoC (%)')
    ax2.grid(True)
    
    # Spot prices
    ax3.plot(timestamps, spot_prices, 'k')
    ax3.set_ylabel('Spot Price (NOK/kWh)')
    ax3.grid(True)
    
    plt.xlabel('Time')
    plt.tight_layout()
    plt.show()
