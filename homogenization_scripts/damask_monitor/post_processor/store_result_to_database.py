# System packages
import os
import yaml
import warnings
import numpy as np
from numpy.typing import NDArray
# Local packages
from ...common_classes.problem_definition import ProblemDefinition

def store_general_settings(
        problem_definition: ProblemDefinition, 
        results_database: dict[str, dict[str, str | float | bool]]) -> dict[str, dict[str, str | float | bool]]:
    
    if results_database.get('general_settings') == None:
        results_database['general_settings'] = dict()
    
    results_database['general_settings']['grid_file'] = problem_definition.general.path.grid_file
    results_database['general_settings']['material_properties'] = problem_definition.general.path.material_properties
    # results_database['general_settings']['grain_orientation'] = problem_definition.general.path.grain_orientation
    results_database['general_settings']['stress_tensor_type'] = problem_definition.general.stress_tensor_type.str()
    results_database['general_settings']['strain_tensor_type'] = problem_definition.general.strain_tensor_type.str()

    return results_database

def store_yield_point_settings(
        problem_definition: ProblemDefinition, 
        results_database: dict[str, dict[str, str | float | bool]]) -> dict[str, dict[str, str | float | bool]]:
    
    if results_database.get('yield_point') == None:
        results_database['yield_point'] = dict()
    
    results_database['yield_point']['N_increments'] = problem_definition.solver.N_increments
    results_database['yield_point']['yield_condition'] = problem_definition.yielding_condition.yield_condition
    match problem_definition.yielding_condition.yield_condition:
        case 'modulus_degradation':
            yield_value = problem_definition.yielding_condition.modulus_degradation_percentage
        case 'stress_strain_curve':
            yield_value = problem_definition.yielding_condition.plastic_strain_yield
        case _:
            yield_value = 0
            warnings.warn(f"storing of setting the yield value for yield condition {problem_definition.yielding_condition.yield_condition} not yet implemented!")
    results_database['yield_point']['yield_condition_value'] = yield_value
    results_database['yield_point']['estimated_tensile_yield'] = problem_definition.yielding_condition.estimated_tensile_yield
    results_database['yield_point']['estimated_shear_yield'] = problem_definition.yielding_condition.estimated_shear_yield

    return results_database

def store_yield_surface_settings(
        problem_definition: ProblemDefinition, 
        results_database: dict[str, dict[str, str | float | bool]]) -> dict[str, dict[str, str | float | bool]]:
    
        if results_database.get('yield_surface') == None:
            results_database['yield_surface'] = dict()

        results_database['yield_surface']['N_increments'] = problem_definition.solver.N_increments
        results_database['yield_surface']['yield_condition'] = problem_definition.yielding_condition.yield_condition
        match problem_definition.yielding_condition.yield_condition:
            case 'modulus_degradation':
                yield_value = problem_definition.yielding_condition.modulus_degradation_percentage
            case 'stress_strain_curve':
                yield_value = problem_definition.yielding_condition.plastic_strain_yield
            case _:
                yield_value = 0
                warnings.warn(f"storing of setting the yield value for yield condition {problem_definition.yielding_condition.yield_condition} not yet implemented!")
        results_database['yield_surface']['yield_condition_value'] = yield_value
        results_database['yield_surface']['estimated_tensile_yield'] = problem_definition.yielding_condition.estimated_tensile_yield
        results_database['yield_surface']['estimated_shear_yield'] = problem_definition.yielding_condition.estimated_shear_yield

        results_database['yield_surface']['points_per_plane'] = problem_definition.yield_surface.load_points_per_plane
        results_database['yield_surface']['asume_tensile_compressive_symmetry'] = problem_definition.yield_surface.asume_tensile_compressive_symmetry

        results_database['yield_surface']['stress_state_creation'] = problem_definition.yield_surface.stress_state_creation

        return results_database

def store_elastic_tensor_settings(
        problem_definition: ProblemDefinition, 
        results_database: dict[str, dict[str, str | float | bool]]) -> dict[str, dict[str, str | float | bool]]:
    
        if results_database.get('elastic_tensor') == None:
            results_database['elastic_tensor'] = dict()

        results_database['elastic_tensor']['strain_step'] = problem_definition.elastic_tensor.strain_step

        return results_database

def store_simulation_type_settings(
        problem_definition: ProblemDefinition, 
        results_database: dict[str, dict[str, str | float | bool]], 
        simulation_type: str) -> dict[str, dict[str, str | float | bool]]:
    match simulation_type:
        case 'yield_point':
            results_database = store_yield_point_settings(problem_definition, results_database)
        case 'yield_surface':
            results_database = store_yield_surface_settings(problem_definition, results_database)
        case 'elastic_tensor':
            results_database = store_elastic_tensor_settings(problem_definition, results_database)
        case _:
            warnings.warn(f"Storing of {simulation_type} settings in results database is not yet implemented!")

    return results_database

def store_result_to_database(problem_definition: ProblemDefinition, simulation_type: str, field_name: str, value: bool | str | float | NDArray[np.float64] | list[list[str]]):
    # This function takes a value from the damask_job post-processing process and stores it in the results_databse
    # The relavant settings used in this simulation are stored along side it for later reference.

    result_database_file = problem_definition.general.path.results_database_file

    result_database_file_exists = os.path.exists(result_database_file)

    if result_database_file_exists:
        with open(result_database_file, 'r') as results_database_reader:
            results_database: dict[str, dict[str, str | float | bool]] = yaml.safe_load(results_database_reader) or {}
    else:
        results_database = {}

    results_database = store_general_settings(problem_definition, results_database)
    results_database = store_simulation_type_settings(problem_definition, results_database, simulation_type)

    if results_database.get(simulation_type) == None:
        results_database[simulation_type] = dict()

    match value:
        case np.ndarray():
            results_database[simulation_type][field_name] = value.tolist() 
        case list():
            results_database[simulation_type][field_name] = value # type: ignore
        case _:
            results_database[simulation_type][field_name] = value
    

    with open(result_database_file, 'w') as results_database_writer:
        yaml.dump(results_database, results_database_writer)
