# System packages
from typing import Union

# Local packages
from .general import compare_general_settings
from .yield_point import compare_yield_point_settings
from .yield_surface import compare_yield_surface_settings
from .elastic_tensor import compare_elastic_tensor_settings
from ...common_classes.problem_definition import ProblemDefinition


def compare_simulation_settings(
        problem_definition: ProblemDefinition, 
        required_fields: dict[str, dict[str,bool]], 
        existing_results: dict[str, dict[str,Union[str, bool, float]]]) -> tuple[bool, list[str], list[str], list[str], dict[str, dict[str, Union[bool, list[str]]]]]:
    # This function compares the settings in the problem_defintion and results database and flags all the (in)-compatible results.

    # Check the entries in the general section.
    (differences_in_general_settings, reasons_general) = compare_general_settings(problem_definition, existing_results)
    
    if differences_in_general_settings:
        general_settings_match = False
        # No point in continuing if the general settings dont even match.
        return general_settings_match, reasons_general, [], [], dict()
    else:
        general_settings_match = True

    compatible_settings: dict[str, dict[str, Union[bool, list[str]]]] = dict()
    compatible_fields: list[str] = []    
    incompatible_fields: list[str] = []

    for simulation_type in required_fields.keys():
        field_exists_in_existing_results = not existing_results.get(simulation_type) == None
        if field_exists_in_existing_results:
            
            # Check the settings of the relevant simulation_type
            if simulation_type == 'yield_point' and field_exists_in_existing_results:
                (differences_in_settings, reasons) = compare_yield_point_settings(problem_definition, existing_results)
            elif simulation_type == 'yield_surface' and field_exists_in_existing_results:
                (differences_in_settings, reasons) = compare_yield_surface_settings(problem_definition, existing_results)
            elif simulation_type == 'elastic_tensor' and field_exists_in_existing_results:
                (differences_in_settings, reasons) = compare_elastic_tensor_settings(problem_definition, existing_results)
            else:
                print("Comparison of existing results to new simulation settings not yet implemented for this simulation type.")
                continue

            # Track if the simulation settings have changed or not.
            compatible_settings[simulation_type] = dict()
            if differences_in_settings:
                incompatible_fields.append(simulation_type)
                compatible_settings[simulation_type]['settings_match'] = False
                compatible_settings[simulation_type]['detected_mismatches'] = reasons
            else:
                compatible_fields.append(simulation_type)
                compatible_settings[simulation_type]['settings_match'] = True
                compatible_settings[simulation_type]['detected_mismatches'] = []

    return general_settings_match, reasons_general, compatible_fields, incompatible_fields, compatible_settings
