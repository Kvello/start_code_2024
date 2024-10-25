# start_code_2024

# Building Energy System Simulator

A Python simulator for building energy systems with solar panels and battery storage. Simulates power consumption, solar generation, and optimizes battery usage based on spot prices.

## Installation


## TODOs


- [ ] Verify that the weather data is correct
- [ ] Add more weather data that impacts solar generation and consumption in CREST model
    - [ ] Temperature
    - [ ] Irradiance
    - [ ] Cloud coverage
    - [ ] Wind speed
    - [ ] Humidity
    - [ ] Precipitation
- [ ] Add more complex CREST model
- [ ] Add chosen crest model as input to the simulation
- [ ] Add actual prediction algorithms for solar generation and spot prices
- [ ] Add more buidning parameters
    - [ ] Coordinates
    - [ ] Different tariffs for grid power
    - [ ] Solar panel direction
    - [ ] Type of building (fabrikk/næringsbygg/bolig)




### Core Functionality & Correctness
- [ ] Implement proper solar angle calculations based on latitude/longitude
- [ ] Add temperature effects on solar panel efficiency
- [ ] Include battery charging/discharging efficiency losses
- [ ] Add proper error handling for API calls
- [ ] Validate CREST model parameters against real consumption data
- [ ] Add input validation and bounds checking
- [ ] Implement proper weather API parsing instead of synthetic data
- [ ] Add tests for core calculations

### Optimization & Performance
- [ ] Implement proper battery optimization using linear programming
- [ ] Add multi-day forecasting and optimization
- [ ] Cache weather API results
- [ ] Parallelize simulations for parameter sweeps
- [ ] Profile and optimize computation bottlenecks

### Features & Enhancements
- [ ] Add GUI for parameter adjustment
- [ ] Implement real-time spot price API integration
- [ ] Add export of simulation results to CSV/Excel
- [ ] Create more sophisticated consumption profiles
- [ ] Add solar panel shading model
- [ ] Include battery degradation model
- [ ] Add economic analysis (ROI, payback period)
- [ ] Create configuration file support
- [ ] Add logging system

### Documentation & Analysis
- [ ] Add detailed API documentation
- [ ] Create example notebooks
- [ ] Add performance benchmarks
- [ ] Document model assumptions and limitations
- [ ] Add validation against real building data
- [ ] Create user guide with typical usage patterns
