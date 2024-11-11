# System packages 
import yaml
import re
import cerberus

# Local packages
from ..common_classes.problem_definition import ProblemDefinition
from ..pre_processor.valid_results_database import valid_results_database_file_scheme

def read_results_data(problem_definition: ProblemDefinition) -> dict[str, dict[str, str | float]]:

    results_database_location = problem_definition.general.path.results_database_file

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
    
    with open(results_database_location, 'r') as results_database_file:
        # This function fails if the results_database.yaml has the structure of a yaml file but contains syntax errors
        # If this happens the results database is removed (backup is made) and a new database will be made.
        try:
            results_database: dict[str, dict[str, str | float]]| None = yaml.load(results_database_file, Loader=loader)
        except Exception: 
            raise Exception("An error occured reading with the results_database.yaml file. Make sure the file is valid!")
    
    yaml_validator = cerberus.Validator(valid_results_database_file_scheme, allow_unknown=True) # type: ignore
    
    if results_database is None:
        raise Exception("An error occured reading with the results_database.yaml file. Is the file empty?")
    else:
        results_database_file_is_valid: bool = yaml_validator.validate(results_database) # type: ignore

        if not results_database_file_is_valid:
            print(f"Errors in results_database.yaml: {yaml_validator.errors}") # type: ignore
            raise Exception("An error occured reading with the results_database.yaml file. Make sure the file is valid.")
        
        return results_database