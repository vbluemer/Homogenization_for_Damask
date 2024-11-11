# System packages
import sys
import os
import numpy as np
from pandas import DataFrame
import scipy.optimize # type: ignore
import scipy.optimize._minimize # type: ignore
import yaml
from typing import Any
import re
import pandas as pd
import scipy # type: ignore

# Local-packages
from run_project import run_project

####### README:
# Use:
# python optimize_material_file_for_elastic_tensor.py project_name

# This is an example to how material properties can be refined to match with experimental data.
# Here, a isotropic material is assumed and the elastic material properties are optimized 
# such that the homogonized elastic tensor components C_11 is decreased by 10% and C_12 by 15%.
# These are arbitrary values that serve as stand-in for experimental data.
# In this example, the following steps are taken.
# 1. The user specifies the project to use. This should be a fully defined project where:
#       - The simulation_type is elastic_tensor
#       - The material_properties_file is to be optimized (this file will be altered, the user should keep a backup)
#           - This should contain a reasonable estimtate of the properties
#       - The component_fitting option is set to algebraic (recommened, "optimization" introduces numerical noise)
#       - The material_type matches with the experimental tensor that is to be fitted (recommended but not nesscecary)
# 2. The project is run with existing settings. This is to check for a properly defined problem_definition.yaml 
#    and extract some settings.
# 3. The optimization is setup:
#       - The values that are optimized in the material_properties_file must be defined.
#       - The values that have to be compared to the experimental data have to be defined.
#       - The quality of the fit is reduced to a single scaler value (MSE is recommended)
# 4. The material properties are optimized using a scipy optimizer.
# 5. The optimized material properties are shown to the screen and can be found in the projects material_properties_file

# In this example, the elastic material properties are fitted to a elastic tensor. However, the code can be changed 
# to optimize any result to any input. Fitting the material properties to experimental yield data is theorettically possible as well,
# although this might require a more detailed optimization process due to stronger numerical noise in the yielding results and larger
# quantity of optimization variables.

# NOTE: This optimization script might run for a long time before convergence

#######

## 1: Get the name of the project to optimize
# Get the project name
project_name = sys.argv[1] 

## 2: Run the project.
# Run the project to check if the problem_definition is valid.
problem_definition = run_project(project_name, skip_checks=True)

## 3: setup all the functions needed to iterate/optimize the project.

# Get the path of the material_properties.yaml that will to be optimized.
material_properties_file = problem_definition.general.path.material_properties

# Define function that reads the current material properties
def read_material_properties(material_properties_file: str) -> dict[str, Any]:
    
    # By default, scientific notation (i.e. 1.25E+05) is read in a YAML file as a string (text).
    # The following expressions instructs python to read scientific notation as a number.
    loader = yaml.SafeLoader
    loader.add_implicit_resolver( # type: ignore
        u'tag:yaml.org,2002:float',
        re.compile(u'''^(?:
        [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$''', re.X),
        list(u'-+0123456789.')) 
    
    with open(material_properties_file, 'r') as material_properties_file_reader:
        material_properties = yaml.load(material_properties_file_reader, Loader=loader)

    return material_properties

# Define a function that rewrites the material properties.
def write_material_properties(material_properties_file: str, material_properties: Any):
    with open(material_properties_file, 'w') as file:
        yaml.safe_dump(material_properties, file)

# Define a function that reads the relavant results
def read_elastic_tensor(elastic_tensor_path: str) -> DataFrame:

    elastic_tensor = pd.read_csv(elastic_tensor_path) # type: ignore
    return elastic_tensor

# Define that the values C_11, C_12, C_13, C33, C_44 under mechanical->elastic are the optimization variables.
initial_values: list[float] = []
values_names: list[str] = []
material_properties = read_material_properties(material_properties_file)
for coefficient_name in material_properties["mechanical"]["elastic"].keys():
    if coefficient_name == "type":
        continue
    values_names.append(coefficient_name)
    initial_values.append(material_properties["mechanical"]["elastic"][coefficient_name])

# The optimization variables should be normalized. This is done by making the actual optimization variable a 
# factor of the magnitude compared to the initial value. So for factor 1, the initial values remains unchanged,
# for factor 0.5, the material property is scaled to 50% its initial value. 
initial_factors: list[float] = [1.] * len(initial_values) 

# Restrict the optimizer with bounds, in this case the lower bound for each variable (factor)
# is 0.6 and 1.4 for the upper bound.
# Lower bound (60% of initial value) and upper bound is used to prevent the optimizer from running non-physical properties
# and because of that getting stuck. This limits how far off the initial estimate can be from the optimum value.
bounds = [(0.6, 1.4) for _ in initial_factors]

# Dummy values to stand in for experimental results. 
# Simulate a C_11 value that is 10% off, C_12 that is 15% off.
elastic_tensor_path = problem_definition.general.path.elastic_tensor_csv
initial_elastic_tensor = read_elastic_tensor(elastic_tensor_path)
c_11_experimental = initial_elastic_tensor["C_11"][0] * 0.9
c_12_experimental = initial_elastic_tensor["C_12"][0] * 0.85

# Define the objective function expresses the fitting quality in a scalar.
def objective_function(material_factors: list[float]) -> float:
    
    # Read the current material properties file.
    material_properties = read_material_properties(material_properties_file)

    # Adjust the material properties
    for coeff_name, initial_value, factor in zip(values_names, initial_values, material_factors):
        material_properties["mechanical"]["elastic"][coeff_name] = float(initial_value * factor)

    # Re-write the material properties file with adjusted values.
    write_material_properties(material_properties_file, material_properties)    

    # Before run, delete results_database to make sure new results are aquired (not strictly nesscecary)
    os.remove(problem_definition.general.path.results_database_file)
    os.remove(problem_definition.general.path.elastic_tensor_csv)

    # Run the project to find the new elastic tensor
    _ = run_project(project_name, skip_checks=True)

    # Read the updated elastic tensor and compare to experimental data.    
    elastic_tensor = read_elastic_tensor(elastic_tensor_path)

    c_11: np.float64 = elastic_tensor["C_11"][0]
    c_12: np.float64 = elastic_tensor["C_12"][0]

    mse: float = (c_11 - c_11_experimental)**2 + (c_12 - c_12_experimental)**2 # type: ignore

    return mse

## 4: Run the optimizer
# This optimization seems to be quite dependant on the optimizer chosen. COBYQA seems to be working best
optimization_result = scipy.optimize.minimize(objective_function, initial_factors, options={'disp':True}, method="COBYQA", bounds=bounds) # type: ignore

## 5: extract the optimized values (already stored in material_properties_file)
optimized_coefficients: list[float] = []

for initial_value, factor in zip(initial_values, optimization_result.x): # type: ignore
    optimized_value = float(initial_value * factor) # type: ignore
    optimized_coefficients.append(optimized_value)

# Display optimized values
for name, initial_value, opt_value in zip(values_names, initial_values, optimized_coefficients):
    print(f"{name} was {initial_value} and is optimized to be {opt_value}")