# System packages
from typing import Union

# Local packages
from ...common_classes.problem_definition import ProblemDefinition

def compare_general_settings(
        problem_definition: ProblemDefinition, 
        existing_results: dict[str, dict[str,Union[str, float]]]) -> tuple[bool, list[str]]:
    
    differences_detected = False
    reasons: list[str] = []

    existing_general_settings = existing_results['general_settings']
    if not existing_general_settings['material_properties'] == problem_definition.general.path.material_properties:
        differences_detected = True
        reasons.append("material_properties path changed")

    # if not existing_general_settings['grain_orientation'] == problem_definition.general.path.grain_orientation:
    #     differences_detected = True
    #     reasons.append("grain_orientation path changed")

    if not existing_general_settings['grid_file'] == problem_definition.general.path.grid_file:
        differences_detected = True
        reasons.append("grid_file path changed")

    if not existing_general_settings['stress_tensor_type'] == problem_definition.general.stress_tensor_type.str():
        differences_detected = True
        reasons.append("stress_tensor_type changed")

    if not existing_general_settings['strain_tensor_type'] == problem_definition.general.strain_tensor_type.str():
        differences_detected = True
        reasons.append("strain_tensor_type changed")

    return differences_detected, reasons