# System packages
import os
import yaml
import re
import cerberus  # type: ignore
import warnings
import math
from typing import Literal
class DamaskWarning(UserWarning):
    pass
import datetime
from typing import no_type_check, Any

# Local packages
from ..common_classes.problem_definition import ProblemDefinition, Tensor
from .problem_definition_structure.valid_problem_definition import valid_problem_definition_file_scheme  # type: ignore

# These functions rewrites the problem_definition.yaml dictonary into a python class-like object.
# So problem_definition["general"]["simulation_type"] becomes problem_definition.general.simulation_type
# The available fields in the problem_definition object can be found with problem_definition.keys() 
# Or for a section specificly: problem_definition.section.keys()

# Custom fields can be added too, for example, adding this to the problem definition:
# general:
#   ...
#   my_field: my_value
# Becomes problem_definition.general.my_field
# Adding custom fields is possible as well, example:
# general:
#   ... (some fields)
# my_section:
#   my_field: my_value
# Becomes problem_definition.my_section.my_field

# Inputs for read_problem_definition: path to project_folder containing the problem_definition.yaml file
# Outputs:
#   - ProblemDefinition (when succesfull)
#   - None (if problem_definition.yaml file not found)
#   - False (if there are errors found while reading the yaml file, the errors will be displayed)



def check_file_existance(project_folder: str, path:str):
    if path[0] == "\\" or path[0] == "/":
        full_path = path
    else:
        full_path = os.path.join(project_folder, path)

    full_path_fixed = os.path.abspath(full_path)
    file_exists = os.path.isfile(full_path_fixed)

    file_extension = ""

    if not file_exists:
        return (False, full_path_fixed, file_extension)
    
    _, file_extension = os.path.splitext(full_path_fixed)

    return (True, full_path_fixed, file_extension)

def check_input_file_paths(problem_definition: ProblemDefinition):
    # This function checks if the files needed for damask exist.
    all_files_exist = True

    project_path = problem_definition.general.path.project_path

    material_properties_file = problem_definition.general.path.material_properties
    (file_found, file_path, file_extension) = check_file_existance(project_path, material_properties_file)
    if not file_found:
        all_files_exist = False
        print(f"The material properties file was not found at: {file_path}")
    else:
        problem_definition.general.path.material_properties = file_path
    
    # grain_orientation_file = problem_definition.general.path.grain_orientation
    # (file_found, file_path, file_extension) = check_file_existance(project_path, grain_orientation_file)
    # if not file_found:
    #     all_files_exist = False
    #     print(f"The grain_orientation file was not found at {file_path}")
    # else: 
    #     problem_definition.general.path.grain_orientation = file_path

    grid_file = problem_definition.general.path.grid_file
    (file_found, file_path, file_extension) = check_file_existance(project_path, grid_file)
    if not file_found:
        all_files_exist = False
        print(f"The grid file was not found at: {file_path}")
    else:
        problem_definition.general.path.grid_file = file_path
    
    if file_extension == '.txt':
        dimensions_file = problem_definition.general.path.dimensions_file
        (file_dimensions_found, file_dimensions_path, file_extension) = check_file_existance(project_path, dimensions_file)
        if not file_dimensions_found:
            all_files_exist = False
            print("The grid_file has the extension '.txt', this requires the dimensions to be defined in a seperate file")
            print(f"This dimensions_file was not found at {file_dimensions_path}")
        else:
            problem_definition.general.path.dimensions_file = file_dimensions_path
    elif file_extension == '.vti':
        pass
    else:
        if file_found:
            warnings.warn("""The grid file was not defined with either .vti or .txt. This is ok if this was intentional""")
    
    if all_files_exist:
        return problem_definition
    else:
        return None

def set_tensors(problem_definition: ProblemDefinition) -> ProblemDefinition:
    # This function sets the strain/stress definitions.
    match problem_definition.general.stress_tensor_type: # type: ignore
        case 'PK1': # type: ignore
            problem_definition.general.stress_tensor_type = Tensor.Stress.PK1()
        case 'PK2': # type: ignore
            problem_definition.general.stress_tensor_type = Tensor.Stress.PK2()
        case 'Cauchy': # type: ignore
            problem_definition.general.stress_tensor_type = Tensor.Stress.Cauchy()
        
    match problem_definition.general.strain_tensor_type: # type: ignore
        case 'true_strain': # type: ignore
            problem_definition.general.strain_tensor_type = Tensor.Strain.TrueStrain()
        case 'Green_Lagrange': # type: ignore
            problem_definition.general.strain_tensor_type = Tensor.Strain.GreenLagrange()
    
    return problem_definition

    
@no_type_check
def display_problem_definition_errors(yaml_errors): # type: ignore
    print("An error occurred while reading the problem_definition.yaml file, the following problems where encountered:")
    for problematic_field in yaml_errors:
        field_error = yaml_errors[problematic_field][0]
        if type(field_error) == str:
            if field_error == 'must be of dict type':
                print(f"Error reading the section [{problematic_field}]: it is not a dictonary.")
                print(f"It should be in the form of...")
                print(f"[{problematic_field}]:")
                print(f"    some_name: some_value")
            elif field_error == 'required field':
                print(f"The required section [{problematic_field}] is missing.")
            elif field_error == 'null value not allowed':
                print(f"The section [{problematic_field}] may not be empty. Add the field names that are missing or put a # in front of the section name.")
            else:
                print(f"Error reading the section [{problematic_field}]: [{field_error}]")
        
        elif type(field_error) == dict:
            for key in field_error.keys():
                if field_error[key][0] == 'required field':
                    print(f"In section [{problematic_field}]: the required field [{key}] is missing.")
                elif field_error[key][0] == 'null value not allowed':
                    print(f"In section [{problematic_field}]: the value for [{key}] may not be empty. Use at very least 0 for numbers, or '' for empty text fields.")
                print(f"In section [{problematic_field}], there is an error in [{key}]: {field_error[key][0]}.")
        else:
            print(f"Error reading the section [{problematic_field}]: [{field_error}]")


def check_load_path_settings(problem_definition_dict: dict[str, Any]):
    # This function makes sure that for each load step all stresses are defined.
    
    load_path_settings_correct = True

    load_path_settings = problem_definition_dict.get('load_path')
    if load_path_settings is None:
        load_path_settings_correct = False
        print("The load_path section is missing from the problem_definition.yaml file!")
        return problem_definition_dict, load_path_settings_correct

    if "stress_x_x" in load_path_settings:      
        if isinstance(load_path_settings['stress_x_x'], (int, float)):
            problem_definition_dict['load_path']['stress_x_x'] = [problem_definition_dict['load_path']['stress_x_x']]
        
        load_steps = len(problem_definition_dict['load_path']['stress_x_x'])
    
        other_directions = ["stress_x_y", "stress_x_z", "stress_y_y", "stress_y_z", "stress_z_z"]
    
        for direction in other_directions:
            if isinstance(load_path_settings[direction], (int, float)):
                problem_definition_dict['load_path'][direction] = [problem_definition_dict['load_path'][direction]]
    
            if not len(problem_definition_dict['load_path'][direction]) == load_steps:
                load_path_settings_correct = False
                print("Not all load directions have the same amount of load steps.")
                return problem_definition_dict, load_path_settings_correct

    if "F_x_x" in load_path_settings:      
        if isinstance(load_path_settings['F_x_x'], (int, float)):
            problem_definition_dict['load_path']['F_x_x'] = [problem_definition_dict['load_path']['F_x_x']]
        
        load_steps = len(problem_definition_dict['load_path']['F_x_x'])
    
        other_directions = ["F_x_y", "F_x_z", "F_y_y", "F_y_z", "F_z_z"]
    
        for direction in other_directions:
            if isinstance(load_path_settings[direction], (int, float)):
                problem_definition_dict['load_path'][direction] = [problem_definition_dict['load_path'][direction]]
    
            if not len(problem_definition_dict['load_path'][direction]) == load_steps:
                load_path_settings_correct = False
                print("Not all load directions have the same amount of load steps.")
                return problem_definition_dict, load_path_settings_correct
            
    return problem_definition_dict, load_path_settings_correct

def check_yield_surface_settings(problem_definition_dict: dict[str, Any]):
    # This function makes sure that for all stress states all stresses are defined.
    
    yield_surface_settings_correct = True
    load_path_settings = problem_definition_dict.get('yield_surface')
    
    def is_power_of_two(x):
        if x <= 0:
            return False
        return math.log2(x).is_integer()

    if not is_power_of_two(load_path_settings['load_points_per_quadrant']):
        yield_surface_settings_correct = False
        print("Load points per quadrant is not a power of 2!")
        return problem_definition_dict, yield_surface_settings_correct

    if load_path_settings is None:
        yield_surface_settings_correct = False
        print("The yield_surface section is missing from the problem_definition.yaml file!")
        return problem_definition_dict, yield_surface_settings_correct
    
    if isinstance(load_path_settings['stress_x_x'], (int, float)):
        problem_definition_dict['yield_surface']['stress_x_x'] = [problem_definition_dict['yield_surface']['stress_x_x']]
    
    load_steps = len(problem_definition_dict['yield_surface']['stress_x_x'])

    other_directions = ["stress_x_y", "stress_x_z", "stress_y_y", "stress_y_z", "stress_z_z"]

    for direction in other_directions:
        if isinstance(load_path_settings[direction], (int, float)):
            problem_definition_dict['yield_surface'][direction] = [problem_definition_dict['yield_surface'][direction]]

        if not len(problem_definition_dict['yield_surface'][direction]) == load_steps:
            yield_surface_settings_correct = False
            print("Not all load directions have the same amount of stress states.")
            return problem_definition_dict, yield_surface_settings_correct

    return problem_definition_dict, yield_surface_settings_correct

def read_problem_definition(project_name: str, project_path: str) -> None | ProblemDefinition | Literal[False]:
    # This function finds and reads the problem_definition.yaml file.
    # Also checks for errors (properly structured and valid values).
    # Outputs a ProblemDefinition class object if succesfull
    
    # Check if specified problem_defintion.yaml exists.
    problem_definition_file = os.path.join(project_path, 'problem_definition.yaml')
    problem_definition_present = os.path.isfile(problem_definition_file)
    if not problem_definition_present:
        print(f"Could not find problem definition file at: {problem_definition_file}")
        return None
    
    # Specify the loader such that 1.25E+05 is read as a number, not a string.
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
    
    # Read the problem definition into a dict
    with open(problem_definition_file, 'r') as problem_definition_file_reader:
        problem_definition_dict = yaml.load(problem_definition_file_reader, Loader=loader)

    # Check for missing fields and proper values.
    yaml_validator = cerberus.Validator(valid_problem_definition_file_scheme, allow_unknown=True) # type: ignore
    
    problem_definition_file_is_valid: bool = yaml_validator.validate(problem_definition_dict) # type: ignore
    if not problem_definition_file_is_valid:
        display_problem_definition_errors(yaml_validator.errors) # type: ignore
        no_errors_while_reading = False
        return no_errors_while_reading

    # Make sure the settings for the chosen simulation type are present.
    simulation_type = problem_definition_dict['general']['simulation_type']
    simulation_type_settings = problem_definition_dict.get(simulation_type)
    if simulation_type_settings == None:
        print(f"The settings needed for {simulation_type} where not provided in the problem_definition.yaml file. Make sure to add the {simulation_type} section.")
        no_errors_while_reading = False
        return no_errors_while_reading

    # Specify where the files are asscociated to the project will be found.
    problem_definition_dict['general']['path'] = dict()
    problem_definition_dict['general']['path']['project_path'] = project_path
    problem_definition_dict['general']['project_name'] = project_name

    match problem_definition_dict["general"]["simulation_type"]:
        case "load_path":
            load_path_subdirectory = '{}_{date:%Y-%m-%d_%H-%M-%S}'.format( "load_path",date=datetime.datetime.now() )
            results_folder = os.path.join(project_path, 'results', 'load_path', load_path_subdirectory)
            damask_files_folder = os.path.join(results_folder, 'damask_files')
        case _:
            results_folder = os.path.join(project_path, 'results')
            damask_files_folder = os.path.join(project_path, 'damask_files')
            

    problem_definition_dict['general']['path']['results_folder'] = results_folder
    results_database_file = os.path.join(results_folder, 'results_database.yaml')
    problem_definition_dict['general']['path']['results_database_file'] = results_database_file
    problem_definition_dict['general']['path']['damask_files_folder'] = damask_files_folder

    problem_definition_dict['general']['path']['problem_definition_file'] = problem_definition_file

    backup_results_sub_folder   = '{}_{date:%Y-%m-%d_%H-%M-%S}'.format( "results",date=datetime.datetime.now() )
    backup_folder = os.path.join(project_path, 'results_backup', backup_results_sub_folder)
    problem_definition_dict['general']['path']['backup_results_folder'] = backup_folder

    problem_definition_dict['general']['path']['material_properties'] = problem_definition_dict['general']['material_properties']
    problem_definition_dict['general']['path']['postprocessing_only'] = problem_definition_dict['general']['postprocessing_only']
    del problem_definition_dict['general']['postprocessing_only']

    if "restart_file_path" in problem_definition_dict["general"]:
        problem_definition_dict['general']['path']['restart_file_path'] = problem_definition_dict['general']['restart_file_path']
        del problem_definition_dict['general']['restart_file_path']
    if "history_loadcase_path" in problem_definition_dict["general"]:
        problem_definition_dict['general']['path']['history_loadcase_path'] = problem_definition_dict['general']['history_loadcase_path']
        del problem_definition_dict['general']['history_loadcase_path']

    if problem_definition_dict['general'].get('dimensions_file') == None:
        problem_definition_dict['general']['path']['dimensions_file'] = ''
    else:
        problem_definition_dict['general']['path']['dimensions_file'] = problem_definition_dict['general']['dimensions_file']
        del problem_definition_dict['general']['dimensions_file']
    problem_definition_dict['general']['path']['grid_file'] = problem_definition_dict['general']['grid_file']


    del problem_definition_dict['general']['material_properties']
    del problem_definition_dict['general']['grid_file']

    # load_path and yield_surface have settings that need aditional checking.
    if simulation_type == 'load_path':
        problem_definition_dict, load_path_set_correctly = check_load_path_settings(problem_definition_dict)
        if not load_path_set_correctly:
            return False

    if simulation_type == 'yield_surface':
        problem_definition_dict, yield_surface_set_correctly = check_yield_surface_settings(problem_definition_dict)
        if not yield_surface_set_correctly:
            return False

    problem_definition_dict['general']['dimensions'] = '3D'
    problem_definition_dict['general']['reduce_parasitic_stresses'] = False

    # Transform the dict to a class object.
    problem_definition = ProblemDefinition(problem_definition_dict)

    # Check that all specified files actually exist.
    updated_problem_definition = check_input_file_paths(problem_definition)
    if updated_problem_definition == None:
        return False
    else:
        problem_definition = updated_problem_definition

    # Define the tensor definition used for stress/strain
    problem_definition = set_tensors(problem_definition)

    return problem_definition
