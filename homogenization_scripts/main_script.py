# System packages
# import os
import shutil

# Local packages
from .pre_processor.read_input_file import ProblemDefinition
from .common_classes.damask_job import DamaskJobTypes
from .pre_processor.read_input_file import read_problem_definition
from .pre_processor.create_jobs import create_jobs
from .pre_processor.get_project_name_and_folder import get_project_name_and_folder
from .pre_processor.summarize_tasks import summarize_tasks
# from .iterative_modes import *
from .post_processor.yield_surfaces import general_functions
from .damask_monitor.pre_processor.damask_pre_processor import pre_process_damask_files
from .damask_monitor.simulation.damask_monitor import run_and_monitor_damask
from .damask_monitor.post_processor.job_post_processing import run_post_processing_job
from .post_processor.fit_yield_surface import fit_yield_surface_problem_definition
from .post_processor.elastic_tensor_fitting import calculate_elastic_tensor_main
from .messages.messages import Messages

def remove_damask_files(damask_job: DamaskJobTypes):
    try:
        shutil.rmtree(damask_job.runtime.damask_files)
    except Exception as e:
        print(f"Error: {e}")
        print("Failed to clean damask_files folder, see above reason why!")

def main_loop(project_name_input: str, scripts_folder: str, skip_checks: bool = False):
    Messages.Main.Banners.start_pre_process()

    ################################################
    ################ Pre-processing ################
    ################################################

    # Resolve the project name and absolute project folder path
    (project_name, project_path) = get_project_name_and_folder(project_name_input, scripts_folder)

    # Read the problem definition
    problem_definition = read_problem_definition(project_name, project_path)
    if not type(problem_definition) == ProblemDefinition:
        if problem_definition == None:
            problem_with_definition_file = 'Problem definition not found, stopping...'
        elif problem_definition == False:
            problem_with_definition_file = 'Error in problem definition, stopping...'
        else:
            problem_with_definition_file = "Unexpected error happend while reading problem definition, stopping..."
        raise Exception(problem_with_definition_file)

    problem_definition.general.automatic_reevaluate = skip_checks

    # Translate the problem definition into jobs to run in Damask
    (problem_definition, jobs) = create_jobs(problem_definition)

    # Create summary and ask to continue
    user_continue = summarize_tasks(problem_definition, jobs)

    # Continue or stop depending on user input
    if not user_continue:
        Messages.Main.user_did_not_run_queued_jobs()
        Messages.Main.Banners.normal_end_of_script()
        return problem_definition
    
    ###############################################
    ################# Damask loop #################
    ###############################################

    Messages.Main.Banners.start_simulations()

    all_jobs_succeseeded = True
    for damask_job in jobs:

        # Run either the normal procedure or run the iterative mode.

        if problem_definition.general.reduce_parasitic_stresses:
            # Use the iterative mode (experimental)
            raise Exception("iterative modes are currently disabled on public version")
            # run_ended_succesfully = run_iterative_mode(problem_definition, damask_job)
            # run_ended_succesfully = run_iterative_bfgs(problem_definition, damask_job)
        else:
            # Pre-process files needed to run DAMASK_grid per job
            (problem_definition, damask_job) = pre_process_damask_files(problem_definition, damask_job)

            # Run the job
            run_ended_succesfully, damask_job = run_and_monitor_damask(problem_definition, damask_job)
        if not run_ended_succesfully:
            all_jobs_succeseeded = False
            print("There seems to have been an error while running damask, skipping post process!")
            continue

        # Do nesscecary post procssing steps for this job.
        post_process_completed = run_post_processing_job(problem_definition, damask_job)

        # Clear the damask simulation files if needed.
        if problem_definition.general.remove_damask_files_after_job_completion:
            remove_damask_files(damask_job)
            print("Cleaned up the damask_files folder.")

        print("")
        print(f"Job was completed succesfully: {post_process_completed}")
        print("")
        
    # run jobs and store results
    
    match all_jobs_succeseeded:
        case True:
            print(f"All {len(jobs)} job(s) succeeded!")
        case False:
            print("Not all simulations ended succesfully. Review the logs for the possible cause.")
            Messages.Main.Banners.simulations_completed()

            # Stopping before running general post processing as required results are likely missing.
            return problem_definition
        
    Messages.Main.Banners.simulations_completed()
    ###############################################
    ############### Post-processing ###############
    ###############################################

    Messages.Main.Banners.start_post_processing()

    # Pick the right post processing steps for simulations
    match problem_definition.general.simulation_type:
        case 'yield_point':
            # Save the yield_point data to a .csv for better access.
            general_functions.write_dataset(problem_definition)
        case 'yield_surface':
            fit_yield_surface_problem_definition(problem_definition)
        case 'elastic_tensor':
            calculate_elastic_tensor_main(problem_definition)
            pass
        case 'load_path':
            load_path_csv = problem_definition.general.path.load_path_csv
            print(f"Dataset has been writen to .csv file: {load_path_csv}")
        case _: # type: ignore
            print(f"No post-processing to do for simulation type: {problem_definition.general.simulation_type}.")
            pass

    Messages.Main.Banners.post_processing_completed()

    Messages.Main.Banners.normal_end_of_script()

    # End of program
    return problem_definition
