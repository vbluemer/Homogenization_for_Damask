# System packages
import os
import yaml
import shutil
import re
import cerberus # type: ignore
import copy

# Local packages
from .required_results.general import find_required_results
from .compare_simulation_settings.compare_settings import compare_simulation_settings
from ..common_classes.damask_job import DamaskJob, DamaskJobTypes, create_multiaxial_yield_point_for_yield_locus, create_uniaxial_yield_point
from .valid_results_database import valid_results_database_file_scheme # type: ignore
from ..common_classes.problem_definition import ProblemDefinition
from .common_classes_pre_processor.reused_results import ReusedResults
from ..messages.messages import Messages


def reduce_required_results_list(
        required_results_simulation_type: dict[str, bool], 
        existing_results_simulation_type: dict[str, str | float]) -> tuple[dict[str, bool], bool, list[str]]:
    fields_removed = False
    removed_fields_list: list[str] = []
    required_results_simulation_type = copy.deepcopy(required_results_simulation_type)

    for result_name in copy.deepcopy(required_results_simulation_type):
        stored_result = existing_results_simulation_type.get(result_name)
        if not stored_result == None:
            del required_results_simulation_type[result_name]
            
            removed_fields_list.append(result_name)

            fields_removed = True
    
    return required_results_simulation_type, fields_removed, removed_fields_list

def define_required_results(problem_definition: ProblemDefinition):
    # This function makes a list of simulations that needs to be run. This list takes into account if results 
    # from previous simulations still exist and reuse these if needed and wanted.
    
    # Find out what results are needed and list these.
    required_results, existing_results_relavant = find_required_results(problem_definition)


    results_folder = os.path.join(problem_definition.general.path.project_path, 'results')
    results_database = os.path.join(results_folder, 'results_database.yaml')

    existing_results = dict()

    backup_folder_path  = problem_definition.general.path.backup_results_folder

    # Check the results_datase.yaml for existing results.
    if os.path.isfile(results_database) and existing_results_relavant:

        # Define the loader such that 1.25E+03 is read as a number, not text.
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
        
        force_remove_results_database = False
        with open(results_database, 'r') as existing_results_database:
            # This function fails if the results_database.yaml has the structure of a yaml file but contains syntax errors
            # If this happens the results database is removed (backup is made) and a new database will be made.
            try:
                existing_results: dict[str, dict[str, str | float]]| None = yaml.load(existing_results_database, Loader=loader)
            except Exception: 
                existing_results: dict[str, dict[str, str | float]]| None = dict()

            if existing_results == None:
                # Deal with an empty results_database file
                existing_results = dict()
                force_remove_results_database = True
            elif not type(existing_results) == dict:
                # Or when it is not actually a yaml file like a string (this check makes empty file check redundant)
                existing_results = dict()
                force_remove_results_database = True

        # Check if the results database is structured properly, is complete and does not contain illegal values.
        yaml_validator = cerberus.Validator(valid_results_database_file_scheme, allow_unknown=True) # type: ignore
        
        results_database_file_is_valid: bool = yaml_validator.validate(existing_results) # type: ignore

        # if the results_base.yaml is faulty, move it to the backup folder and start fresh.
        if results_database_file_is_valid and not force_remove_results_database:
            previous_results_exist = True
        else:
            Messages.Reuse.invalid_results_database_detected(yaml_validator.errors) # type: ignore
            previous_results_exist = False
            existing_result_files = os.listdir(problem_definition.general.path.results_folder)
            for f in existing_result_files: 
                os.makedirs(backup_folder_path, exist_ok=True)
                shutil.move(os.path.join(problem_definition.general.path.results_folder, f), os.path.join(backup_folder_path,f))
            Messages.Reuse.moved_results_to_backup_folder(backup_folder_path)
            reused_results = ReusedResults(True)
            reused_results.general_settings(False, list("results database was formatted incorrectly."))
            problem_definition.add_reused_results_information(reused_results)
            return (problem_definition, required_results)

    else:
        previous_results_exist = False


    if previous_results_exist:
        # Initialize the object which holds a list of re-useable results
        reused_results = ReusedResults(True)

        Messages.Reuse.Banners.start_resuse_section()

        # This function compares all the settings in the problem_definition with those in the results_database and flags 
        # wether the results are compatible with the existing results
        (general_settings_match, reasons_general_mismatch, compatible_fields, incompatible_fields, compatible_settings) = compare_simulation_settings(problem_definition, required_results, existing_results)

        original_full_results_database = copy.deepcopy(existing_results)

        # If the general settings do not match, move results to backup folder.
        if not general_settings_match:
            Messages.Reuse.general_section_settings_changed(reasons_general_mismatch)
            existing_result_files = os.listdir(problem_definition.general.path.results_folder)
            for f in existing_result_files: 
                os.makedirs(backup_folder_path, exist_ok=True)
                shutil.move(os.path.join(problem_definition.general.path.results_folder, f), os.path.join(backup_folder_path,f))
            shutil.rmtree(problem_definition.general.path.results_folder)
            reused_results.general_settings(general_settings_match, reasons_general_mismatch)
            problem_definition.add_reused_results_information(reused_results)
            Messages.Reuse.moved_results_to_backup_folder(backup_folder_path)
            return (problem_definition, required_results)
        
        
        Messages.Reuse.general_section_settings_compatible()

        reused_results.general_settings(general_settings_match, [''])

        # Deal with the simulation_types that are no longer compatible with current simulation settings.
        for incompatible_field in incompatible_fields:
            Messages.Reuse.detected_incompatible_settings_simulation_type(incompatible_field, compatible_settings[incompatible_field]['detected_mismatches'])
            
            results_folder_simulation_type = os.path.join(problem_definition.general.path.results_folder, incompatible_field)
            full_backup_folder_path_simulation_type      = os.path.join(backup_folder_path, incompatible_field)
            backup_folder_simulation_type_results_database = os.path.join(full_backup_folder_path_simulation_type, 'results_database.yaml')
            os.makedirs(full_backup_folder_path_simulation_type, exist_ok=True)
            if os.path.exists(results_folder_simulation_type):
                existing_result_files = os.listdir(results_folder_simulation_type)
                for f in existing_result_files: 
                    os.makedirs(full_backup_folder_path_simulation_type, exist_ok=True)
                    shutil.move(os.path.join(results_folder_simulation_type, f), os.path.join(full_backup_folder_path_simulation_type,f))
                shutil.rmtree(results_folder_simulation_type)
            with open(backup_folder_simulation_type_results_database, 'w') as backup_results_database:
                yaml.dump(existing_results[incompatible_field], backup_results_database)
            del existing_results[incompatible_field]
            with open(results_database, 'w') as existing_results_database:
                yaml.dump(existing_results, existing_results_database)
            reused_results.add_reevaluated_simulation_type(incompatible_field, compatible_settings[incompatible_field]["detected_mismatches"])  # type: ignore (compatible_settings[incompatible_field]["detected_mismatches"] is always string list)
            Messages.Reuse.moved_results_to_backup_folder(results_folder_simulation_type)

        # Deal with the results that can be reused from earlier simulations.
        # The user is asked if the results should actually be used again or not.
        for compatible_field in compatible_fields:
            reduced_required_results_simulation_type, fields_removed, removed_fields_list = reduce_required_results_list(required_results[compatible_field], existing_results[compatible_field])
            if not fields_removed:
                continue
            if not problem_definition.general.automatic_reevaluate:
                reuse_simulation_results = Messages.Reuse.ask_to_reuse_existing_results(compatible_field, removed_fields_list)
            else:
                reuse_simulation_results = False
            if reuse_simulation_results:
                required_results[compatible_field] = reduced_required_results_simulation_type
                for skipped_field in removed_fields_list:
                    reused_results.add_reused_value(compatible_field, skipped_field)
            else:
                if not problem_definition.general.automatic_reevaluate:
                    move_all_results = Messages.Reuse.ask_to_move_single_or_all_values_in_simulation_type(compatible_field, removed_fields_list)
                else:
                    move_all_results = True
                reused_results.add_reevaluated_simulation_type(compatible_field, list("Users choice"))
                results_folder_simulation_type = os.path.join(problem_definition.general.path.results_folder, compatible_field)
                full_backup_folder_path_simulation_type      = os.path.join(backup_folder_path, compatible_field)
                os.makedirs(full_backup_folder_path_simulation_type, exist_ok=True)
                backup_folder_simulation_type_results_database = os.path.join(full_backup_folder_path_simulation_type, 'results_database.yaml')
                with open(backup_folder_simulation_type_results_database, 'w') as backup_results_database:
                    yaml.dump(existing_results, backup_results_database)

                if move_all_results:
                    items_to_remove = list(existing_results[compatible_field].keys())
                else:
                    items_to_remove = copy.deepcopy(removed_fields_list)
                
                for field_name in items_to_remove:
                    results_folder_field = os.path.join(results_folder_simulation_type, field_name)
                    backup_folder_field = os.path.join(full_backup_folder_path_simulation_type, field_name)
                    if os.path.exists(results_folder_field):
                        existing_result_files = os.listdir(results_folder_field)
                        for f in existing_result_files: 
                            os.makedirs(backup_folder_field, exist_ok=True)
                            if os.path.exists(os.path.join(results_folder_field, f)):
                                shutil.move(os.path.join(results_folder_field, f), os.path.join(backup_folder_field,f))
                        shutil.rmtree(results_folder_field)
                    del existing_results[compatible_field][field_name]
                    if len(list(existing_results[compatible_field].keys())) == 0:
                        del existing_results[compatible_field]
                    with open(results_database, 'w') as existing_results_database:
                        yaml.dump(existing_results, existing_results_database)
                    
                if len(list(existing_results.keys())) == 1:
                    os.remove(results_database)
                
                full_backup_results_database_path = os.path.join(backup_folder_path, 'results_database.yaml')
                with open(full_backup_results_database_path, 'w') as existing_results_database:
                    yaml.dump(original_full_results_database, existing_results_database)
                Messages.Reuse.moved_results_to_backup_folder(full_backup_folder_path_simulation_type)


    else:
        reused_results = ReusedResults(False)

    problem_definition.add_reused_results_information(reused_results)

    return (problem_definition, required_results)

def create_jobs(problem_definition: ProblemDefinition) -> tuple[ProblemDefinition, list[DamaskJobTypes]]:
    # Get a list (dict) of all the results that are needed for the chosen simulation_type and its settings.
    # The list contains names of the needed results. These names are compared to existing results and results that 
    # already exist will be removed (if the user chooses to).
    # It will also be compared if the existing results have been gathered using similar settings.
    (problem_definition, required_results) = define_required_results(problem_definition)

    damask_jobs: list[DamaskJobTypes] = []

    # From the list of result names that are needed, create a DamaskJob with all the specifics. 
    for simulation_type in required_results:
        for load_case in required_results[simulation_type]:
            if simulation_type == 'yield_point':
                damask_job: DamaskJobTypes = create_uniaxial_yield_point(problem_definition, load_case)
                damask_jobs.append(damask_job)
            elif simulation_type == 'load_path':
                damask_job: DamaskJobTypes = DamaskJob.LoadPath(problem_definition)
                damask_jobs.append(damask_job)
            elif simulation_type == 'yield_surface':
                damask_job_list = create_multiaxial_yield_point_for_yield_locus(problem_definition, load_case, required_results=required_results['yield_surface'].keys())# type: ignore
                damask_jobs = damask_jobs + damask_job_list
            elif simulation_type == 'elastic_tensor':
                damask_job: DamaskJobTypes = DamaskJob.ElasticTensor(problem_definition, load_case)
                damask_jobs.append(damask_job)
            else:
                raise Exception(f"Job queing of {simulation_type} Jobs not yet implemented!")
            
    # Track the number of jobs that have been sheduled and label the jobs with a number.
    total_number_damask_jobs = len(damask_jobs)    
    for damask_job_index in range(total_number_damask_jobs):
        damask_jobs[damask_job_index].job_number = damask_job_index + 1
        damask_jobs[damask_job_index].total_jobs = total_number_damask_jobs

    return problem_definition, damask_jobs

