# System packages

# Local packages
from....common_classes.problem_definition import ProblemDefinition

def required_results_elastic_tensor(problem_definition: ProblemDefinition) -> dict[str, dict[str, bool]]:

    # list of supported states 
    # anisotropic: 21
    # monoclinic: 13
    # orthotropic: 9
    # tetragonal: 6
    # cubic: 3
    # isotropic: 2



    required_results: dict[str, dict[str, bool]] = dict()
    required_results['elastic_tensor'] = dict()
    
    material_type = problem_definition.elastic_tensor.material_type

    # all_tensor_components = [
    #     '1-1', '1-2', '1-3', '1-4', '1-5', '1-6',
    #            '2-2', '2-3', '2-4', '2-5', '2-6',
    #                   '3-3', '3-4', '3-5', '3-6',
    #                          '4-4', '4-5', '4-6',
    #                                 '5-5', '5-6',
    #                                        '6-6']

    component_fitting = problem_definition.elastic_tensor.component_fitting
    if component_fitting == "algebraic":
        number_of_load_cases = "minimum"
        problem_definition.elastic_tensor.number_of_load_cases = "minimum"
    else:
        number_of_load_cases = problem_definition.elastic_tensor.number_of_load_cases


    if number_of_load_cases == 'minimum':
        match material_type:
            case 'anisotropic':
                required_fields = [
            "strain_xx", "strain_yy", "strain_zz", "strain_xy", "strain_xz", "strain_yz"
            ]
                
            case 'monoclinic':
                required_fields= [
            "strain_xx", "strain_yy", "strain_zz", "strain_xy", "strain_xz", "strain_yz"
            ]
            case 'orthotropic':
                required_fields= [
            "strain_xx", "strain_yy", "strain_zz", "strain_xy", "strain_xz", "strain_yz"
            ]
                
            case 'tetragonal':
                required_fields= [
            "strain_xx", "strain_zz", "strain_xy", "strain_xz"
            ]
                
            case 'cubic':
                required_fields= [
            "strain_xx", "strain_xy"
            ]

            case 'isotropic':
                required_fields= [
            "strain_xx"
            ]
            case _: # type: ignore
                raise Exception(f"Error while defining jobs for elasticity tensor: material_type = {problem_definition.general.dimensions} not yet implemented.")
    elif number_of_load_cases == 'all_directions':
        required_fields = [
            "strain_xx", "strain_yy", "strain_zz", "strain_xy", "strain_xz", "strain_yz"
            ]
    elif number_of_load_cases == "combined_directions":
        required_fields = [
            "strain_xx", "strain_xx_yy", "strain_xx_zz", "strain_xx_xy", "strain_xx_xz", "strain_xx_yz",
                         "strain_yy"   , "strain_yy_zz", "strain_yy_xy", "strain_yy_xz", "strain_yy_yz",
                                         "strain_zz"   , "strain_zz_xy", "strain_zz_xz", "strain_zz_yz",
                                                         "strain_xy"   , "strain_xy_xz", "strain_xy_yz",
                                                                         "strain_xz"   , "strain_xz_yz",
                                                                                         "strain_yz"
            ]
    else:
        raise Exception(f"number_of_load_cases setting ({number_of_load_cases}), not recognized, this should have been solved by the settings parser!")

    for field in required_fields:
        required_results['elastic_tensor'][field] = True


    return required_results