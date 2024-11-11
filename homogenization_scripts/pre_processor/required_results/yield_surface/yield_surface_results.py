
# Local packages
from ....common_classes.damask_job import create_multiaxial_yield_points_set_names
from ....common_classes.problem_definition import ProblemDefinition
from .manual_stress_state_creation import read_manual_stress_states

def required_results_yield_surface(problem_definition: ProblemDefinition) -> dict[str, dict[str, bool]]:
   
    if problem_definition.yield_surface.stress_state_creation == "automatic":
        required_fields = required_results(problem_definition)
    else:
        required_fields = read_manual_stress_states(problem_definition)

    return required_fields

def required_results(problem_definition: ProblemDefinition) -> dict[str, dict[str, bool]]:

    required_results: dict[str, dict[str, bool]] = dict()
    required_results['yield_surface'] = dict()
    
    if problem_definition.general.dimensions == '2D':
        required_results['yield_surface']['x_y'] = True
    elif problem_definition.general.dimensions == '3D':
        fields_x_y = create_multiaxial_yield_points_set_names(problem_definition, 'x_y')
        fields_x_z = create_multiaxial_yield_points_set_names(problem_definition, 'x_z')
        fields_y_z = create_multiaxial_yield_points_set_names(problem_definition, 'y_z')

        fields = fields_x_y + fields_x_z + fields_y_z
        for key in fields:
            required_results['yield_surface'][key] = True 
    else:
        raise Exception(f"Error while defining jobs for Hill yield surface: dimension = {problem_definition.general.dimensions} not yet implemented.")
    
    return required_results