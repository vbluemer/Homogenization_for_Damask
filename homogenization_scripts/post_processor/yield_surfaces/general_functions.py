# System packages
from pandas import DataFrame
import pandas as pd
import numpy as np
from numpy.typing import NDArray
import scipy # type: ignore
import scipy.optimize # type: ignore
import copy
import os
import csv

# Local packages
from ...messages.messages import Messages
from .yield_surface_template import YieldSurfaces
from ...common_classes.problem_definition import ProblemDefinition
from ...common_functions.read_results_database_file import read_results_data

MPa_to_Pa = 1E6
Pa_to_MPa = 1/MPa_to_Pa

def write_dataset(problem_definition: ProblemDefinition) -> ProblemDefinition:
    # This function takes the yield points in the results_database and saves it to a .csv file

    results_database = read_results_data(problem_definition)

    simulation_type = problem_definition.general.simulation_type

    data_set: list[list[list[float]]] = []
    data_names: list[str] = []
    setting_field_names = ["N_increments", "assume_tensile_compressive_symmetry", "estimated_shear_yield", "estimated_tensile_yield", "points_per_plane", "yield_condition", "yield_condition_value", "stress_state_creation"]
    for keyname in results_database[simulation_type]:
        is_setting_field = keyname in setting_field_names
        if is_setting_field:
            continue
        
        # When a job ended in no yielding, this is omited from the .csv file.
        if results_database[simulation_type][keyname][0][0] == "NO_YIELD_DETECTED": # type: ignore
            continue

        data_point: list[list[float]] = results_database[simulation_type][keyname] # type: ignore
        data_set.append(data_point)
        data_names.append(keyname)

    data_set_dict: list[dict[str, float|str]] = []

    for data_point, data_name in zip(data_set, data_names):
        data_point_dict: dict[str, float|str] = dict()
        data_point_dict['stress_xx'] = data_point[0][0]
        data_point_dict['stress_yy'] = data_point[1][1]
        data_point_dict['stress_zz'] = data_point[2][2]
        data_point_dict['stress_xy'] = data_point[0][1]
        data_point_dict['stress_xz'] = data_point[0][2]
        data_point_dict['stress_yz'] = data_point[1][2]
        data_point_dict["unit"] = "Pa"
        data_point_dict["field_name"] = data_name
        data_set_dict.append(data_point_dict)


    field_names = ["field_name", "unit", "stress_xx", "stress_yy", "stress_zz", "stress_xy", "stress_xz", "stress_yz"]

    yield_points_csv = os.path.join(problem_definition.general.path.results_folder, f"yield_points_{simulation_type}.csv")

    problem_definition.general.path.yield_points_csv = yield_points_csv

    Messages.YieldSurface.writing_dataset_to(yield_points_csv)

    with open(yield_points_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data_set_dict)

    return problem_definition

def read_yield_points(yield_points_file: str) -> DataFrame:
    # This function reads the yield_poitns from .csv (written by write_dataset) to a pandas dataframe
    Messages.YieldSurface.reading_dataset_from(yield_points_file)
    df: DataFrame = pd.read_csv(yield_points_file) # type: ignore

    return df

def fit_surface(yield_surface: YieldSurfaces, data_set: DataFrame) -> YieldSurfaces:
    # This function takes a generic yield surface and data_set of yield points and fits the coefficients to the data_set.
    # For a yield surface to be fitted by this function it must implement the function defined in YieldSurfaces (yield_surface_template.py)


    Messages.YieldSurface.fitting_yield_surface(yield_surface.display_name())
    
    # Format and convert units data_set.
    yield_points = get_yield_points_form_data_set(data_set, yield_surface.unit_conversion())
    number_data_points = np.shape(yield_points)[0]

    # Objective function that is zero for perfect fit.
    def objective(coefficients: list[float]) -> float:

        yield_surface_objective = copy.deepcopy(yield_surface)

        yield_surface_objective.set_coefficients_from_list(coefficients)

        mean_square_error_yield = 0

        for yield_point in yield_points:
            yield_point_error = yield_surface_objective.evaluate(yield_point)
            mean_square_error_yield += yield_point_error**2 / number_data_points
        
        # Include the penalties for constraint adherence.
        penalty_value = yield_surface_objective.penalty_sum()

        objective_value = mean_square_error_yield + penalty_value

        return objective_value
    
    number_optimization_coefficients = yield_surface.number_optimization_coefficients()
    initial_guess: list [float] = np.squeeze(np.ones((1,number_optimization_coefficients))).tolist()

    optimization_result = scipy.optimize.minimize(objective, initial_guess, options={'disp': False }, method="L-BFGS-B") # type: ignore
\
    optimized_coefficients: list[float] = optimization_result.x # type: ignore

    yield_surface_fitted = copy.deepcopy(yield_surface)
    yield_surface_fitted.set_coefficients_from_list(optimized_coefficients) # type: ignore

    mean_square_error_stress = yield_surface_fitted.get_MSE(data_set)
    yield_surface_fitted.set_MSE(mean_square_error_stress)

    return yield_surface_fitted


def get_yield_points_form_data_set(data_set: DataFrame, unit_conversion: float) -> NDArray[np.float64]:
    voight_notation = ['stress_xx', 'stress_yy', 'stress_zz', 'stress_yz', 'stress_xz', 'stress_xy']
    yield_points_pandas = data_set[voight_notation]

    yield_points: NDArray[np.float64] = yield_points_pandas.to_numpy() * unit_conversion # type: ignore
    
    return yield_points


def calculate_MSE_stress(yield_surface: YieldSurfaces, data_set: DataFrame) -> float:
    # This function calculates the MSE of over or under estimation of the yield stress in loading direction.
    mean_square_error = 0.

    yield_points = get_yield_points_form_data_set(data_set, yield_surface.unit_conversion())
    number_data_points = np.shape(yield_points)[0]

    for data_point in yield_points:

        norm_data_point = np.linalg.norm(data_point)

        # At the yield point, the yield surface function should equal zero. x is the factor of the magnutude of the 
        # yield point that describes when the function is actually zero. Whit this x, the magnitude of error over/under-estimation can be found.
        def objective(x: float) -> float:
            yield_surface_value = yield_surface.evaluate(data_point*x) # type: ignore
            yield_surface_error = (yield_surface_value)**2
            return yield_surface_error

        result = scipy.optimize.minimize_scalar(objective, options={'disp': False}, method="Golden") # type: ignore

        fitted_scale = result.x  # type: ignore

        estimated_yield_strength_magnitude = np.linalg.norm(data_point*fitted_scale)  # type: ignore
        mean_square_error += float((estimated_yield_strength_magnitude - norm_data_point)**2 / number_data_points)  # type: ignore


    return mean_square_error