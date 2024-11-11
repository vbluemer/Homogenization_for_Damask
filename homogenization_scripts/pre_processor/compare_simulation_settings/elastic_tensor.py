# System packages
from typing import Union

# Local packages
from ...common_classes.problem_definition import ProblemDefinition

def compare_elastic_tensor_settings(
        problem_definition: ProblemDefinition, 
        existing_results: dict[str, dict[str, Union[str, bool, float]]]):
    
    differences_detected = False
    reasons: list[str] = []

    existing_settings = existing_results['elastic_tensor']
    if not existing_settings['strain_step'] == problem_definition.elastic_tensor.strain_step:
        differences_detected = True
        reasons.append("load magnitude of elasticity condition changed")

    return (differences_detected, reasons)