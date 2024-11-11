# System packages

# Local packages
from....common_classes.problem_definition import ProblemDefinition

def is_out_of_simulation_plane(selected_direction: str, simulation_dimension_mode: str) -> bool:
    if simulation_dimension_mode == '3D':
        return False
    else:
        is_out_of_simulation_plane = 'z' in selected_direction
        if is_out_of_simulation_plane:
            return True
        else:
            return False

def required_results_yield_point(problem_definition: ProblemDefinition) -> dict[str, dict[str, bool]]:

    required_results: dict[str, dict[str, bool]] = dict()
    required_results['yield_point'] = dict()

    selected_load_directions = problem_definition.yield_point.load_direction
    dimensional_mode = problem_definition.general.dimensions

    match selected_load_directions:
        case str():
            load_direction_is_out_of_plane = is_out_of_simulation_plane(selected_load_directions, dimensional_mode)
            if load_direction_is_out_of_plane:
                print(f"Selected load direction for yield point detection ({selected_load_directions}) not inside in physical domain (currently in 2D mode!)")
            else:
                required_results['yield_point'][selected_load_directions] = True
        case list():
            for load_direction in selected_load_directions:
                load_direction_is_out_of_plane = is_out_of_simulation_plane(load_direction, dimensional_mode)
                if load_direction_is_out_of_plane:
                    print(f"Selected load direction for yield point detection ({load_direction}) not inside in physical domain (currently in 2D mode!)")
                else:
                    required_results['yield_point'][load_direction] = True
                
        case _: # type: ignore
            raise Exception(f"Input at the load directions for yield point simulation type not recognized as either str or list: input is: {selected_load_directions}. Type of input is: {type(selected_load_directions)}")

    return required_results