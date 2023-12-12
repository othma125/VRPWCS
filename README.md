# VRP with Stationary Charging Stations

## Overview
This project implements a solution for the Vehicle Routing Problem (VRP) with stationary charging stations using the PuLP optimization library in Python. The objective is to minimize the total cost, considering factors like travel distance, driver wages, and battery charging costs.

## Installation
Requires Python 3.x and PuLP library. Install used libs using `pip install -r requirements.txt`.

## Files
- `mathematical_model.pdf`: Describes the mathematical model, objective function, and constraints.
- `model_construction.py`: Builds the optimization model using PuLP, integrating the objective function and constraints.
- `decision_variable.py`: Defines decision variables for the model, such as routes, vehicle loads, and charging states.

## Usage
1. Review `mathematical_model.pdf` for an understanding of the problem and its formulation.
2. Run `model_construction.py` to set up and solve the optimization problem.
3. Modify `decision_variable.py` to experiment with different scenarios or constraints.

## Contributing
Contributions to improve the model or its implementation are welcome. Please submit a pull request or open an issue for discussion.

## License
No license
