# Local packages
from .yield_surface.yield_surface_results import required_results_yield_surface
from ...common_classes.problem_definition import ProblemDefinition
from .yield_point.yield_point import required_results_yield_point
from .elastic_tensor.elastic_tensor import required_results_elastic_tensor

def find_required_results(problem_definition: ProblemDefinition) -> tuple[dict[str, dict[str, bool]], bool]:
    # This function specifies results that are needed for the choosen simulation type.
    
    match problem_definition.general.simulation_type:
        case 'yield_surface':
            required_fields = required_results_yield_surface(problem_definition)
            existing_results_are_relavant = True
        case 'yield_point':
            required_fields = required_results_yield_point(problem_definition)
            existing_results_are_relavant = True
        case 'load_path':
            required_fields: dict[str, dict[str, bool]] = dict()
            required_fields['load_path'] = dict()
            required_fields['load_path']['stress_path'] = True
            existing_results_are_relavant = False
        case 'elastic_tensor':
            required_fields = required_results_elastic_tensor(problem_definition)
            existing_results_are_relavant = True
        case _: # type: ignore
            raise Exception(f"Definition of required results for {problem_definition.general.simulation_type} has not been implemeted yet!")
    
    return required_fields, existing_results_are_relavant