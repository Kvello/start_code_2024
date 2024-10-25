from typing import List
import numpy as np

def get_spot_prices(hours: int = 24) -> List[float]:
    """Get spot prices (simulated for demo)"""
    
    base_price = 1.0  # NOK/kWh
    
    # Create daily price pattern
    hourly_factors = [
        0.8, 0.7, 0.6, 0.6, 0.7, 0.9, 1.2, 1.4,  # 00-07
        1.3, 1.2, 1.1, 1.0, 1.0, 0.9, 0.9, 1.0,  # 08-15
        1.2, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8   # 16-23
    ]
    
    prices = []
    for hour in range(hours):
        price = base_price * hourly_factors[hour % 24]
        # Add random variation
        price *= (1 + np.random.normal(0, 0.1))
        prices.append(max(0, price))
        
    return prices
