from typing import List, Tuple
import numpy as np

def optimize_battery(
    battery_capacity_kwh: float,
    battery_charge_rate_kw: float,
    spot_prices: List[float],
    load_kwh: List[float],
    pv_production_kwh: List[float],
    initial_soc: float = 50.0
) -> Tuple[List[float], List[float]]:
    """Optimize battery operation based on spot prices and energy flows"""
    
    num_hours = len(spot_prices)
    soc = [initial_soc]  # State of charge in percent
    grid_power = []      # Power from/to grid in kW
    
    for hour in range(num_hours):
        net_load = load_kwh[hour] - pv_production_kwh[hour]
        current_soc = soc[-1]
        
        # Simple price-based strategy
        if spot_prices[hour] > np.mean(spot_prices):
            # High price: Try to discharge
            power_available = min(
                battery_charge_rate_kw,
                (current_soc/100) * battery_capacity_kwh
            )
            battery_power = -min(power_available, net_load)
        else:
            # Low price: Try to charge
            power_available = min(
                battery_charge_rate_kw,
                ((100-current_soc)/100) * battery_capacity_kwh
            )
            battery_power = min(power_available, -net_load)
            
        # Update state of charge
        new_soc = current_soc + (battery_power / battery_capacity_kwh) * 100
        new_soc = np.clip(new_soc, 0, 100)
        soc.append(new_soc)
        
        # Calculate grid power
        grid_power.append(net_load + battery_power)
    
    return soc[1:], grid_power
