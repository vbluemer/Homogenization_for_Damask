# System packages 
import os

# Local packages
from .prepare_damask_files import PrepareFile
from ...common_classes.problem_definition import ProblemDefinition
from ...common_classes.damask_job import DamaskJobTypes, DamaskJob

def pre_process_damask_files(
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJobTypes,
        iteration_mode: bool = False) -> tuple[ProblemDefinition, DamaskJobTypes]:
    # This function performs the final preparations of the damask_job.
    # The simualtion files are moved to the right folder, the working directory is cleaned up, result folders are created.


    # Set some varaibles for convenience:
    simulation_type = damask_job.simulation_type
    load_direction = damask_job.field_name
    
    # Create folders where damask can store files and post results.
    if iteration_mode == False:        
        results_folder = problem_definition.general.path.results_folder
        damask_files_folder = problem_definition.general.path.damask_files_folder
        backup_folder = problem_definition.general.path.backup_results_folder
    else:
        damask_files_folder = os.path.join(problem_definition.general.path.damask_files_folder, 'iteration')
        results_folder = os.path.join(damask_files_folder, 'monitor')
        backup_folder = os.path.join(damask_files_folder, 'backup')
        results_folder_main= problem_definition.general.path.results_folder
        damask_files_folder_main = problem_definition.general.path.damask_files_folder
        backup_folder_main = problem_definition.general.path.backup_results_folder
        damask_files_folder_job_main = damask_files_folder_main
        results_folder_job_main = os.path.join(results_folder_main, 'results')
        os.makedirs(results_folder_job_main, exist_ok=True)

    # The load_path uses a different result structure for now.
    match damask_job:
        case DamaskJob.LoadPath():
            damask_files_folder_job = damask_files_folder
            results_folder_job = os.path.join(results_folder, 'results')
        case _:
            damask_files_folder_job = os.path.join(damask_files_folder, simulation_type, load_direction)
            results_folder_job = os.path.join(results_folder, simulation_type, load_direction)
    

    os.makedirs(damask_files_folder_job, exist_ok=True)
    os.makedirs(results_folder_job, exist_ok=True)

    damask_job.runtime.set_damask_files(damask_files_folder_job)
    damask_job.runtime.set_results_path(results_folder_job)

    damask_grid_log_file = os.path.join(damask_files_folder_job, 'DAMASK_grid.log')

    damask_job.runtime.set_log_file(damask_grid_log_file)

    damask_result_file = os.path.join(damask_files_folder_job, f"{problem_definition.general.project_name}.hdf5")
    damask_temporary_result_file = os.path.join(damask_files_folder_job, f"{problem_definition.general.project_name}_temporary.hdf5")
    damask_restart_file = os.path.join(damask_files_folder_job, f"{problem_definition.general.project_name}_restart.hdf5")

    damask_job.runtime.set_damask_result_file(damask_result_file)
    damask_job.runtime.set_damask_temporary_result_file(damask_temporary_result_file)
    damask_job.runtime.set_damask_restart_file(damask_restart_file)

    backup_folder_job = os.path.join(backup_folder, simulation_type, load_direction)

    damask_job.runtime.set_backup_folder(backup_folder_job)

    if iteration_mode == True:
        damask_job.runtime_main.set_damask_files(damask_files_folder_job_main) # type: ignore
        damask_job.runtime_main.set_results_path(results_folder_job_main) # type: ignore

        damask_grid_log_file = os.path.join(damask_files_folder_job_main, 'DAMASK_grid.log') # type: ignore

        damask_job.runtime_main.set_log_file(damask_grid_log_file)

        damask_result_file = os.path.join(damask_files_folder_job_main, f"{problem_definition.general.project_name}.hdf5") # type: ignore
        damask_temporary_result_file = os.path.join(damask_files_folder_job_main, f"{problem_definition.general.project_name}_temporary.hdf5") # type: ignore
        damask_restart_file = os.path.join(damask_files_folder_job_main, f"{problem_definition.general.project_name}_restart.hdf5") # type: ignore

        damask_job.runtime_main.set_damask_result_file(damask_result_file)
        damask_job.runtime_main.set_damask_temporary_result_file(damask_temporary_result_file)
        damask_job.runtime_main.set_damask_restart_file(damask_restart_file)

        backup_folder_job = os.path.join(backup_folder_main, simulation_type, load_direction) # type: ignore

        damask_job.runtime_main.set_backup_folder(backup_folder_job)

    ########
    # damask preporcessing: Prepare and move the simulation files to the right location.
    if not iteration_mode:
        PrepareFile.make_sure_work_folders_are_empty(problem_definition, damask_job) # type: ignore
    (problem_definition, damask_job) = PrepareFile.material_properties_and_orientation_file(problem_definition, damask_job) # type: ignore
    (problem_definition, damask_job) = PrepareFile.grid_and_dimensions_file(problem_definition, damask_job) # type: ignore
    (problem_definition, damask_job) = PrepareFile.load_case_file(problem_definition, damask_job) # type: ignore
    (problem_definition, damask_job) = PrepareFile.numerics_file(problem_definition, damask_job) # type: ignore

    if problem_definition.general.path.restart_file_path:
        (problem_definition, damask_job) = PrepareFile.restart_file(problem_definition, damask_job) # type: ignore

    return (problem_definition, damask_job) # type: ignore
