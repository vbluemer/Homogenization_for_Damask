# System packages
import subprocess
import traceback
import numpy as np
import os
import time
import shutil
import damask # type: ignore
import datetime

# Local packages
from ..common_classes_damask_monitor.increment_data import IncrementData
from ...common_classes.problem_definition import ProblemDefinition
from ...common_classes.damask_job import DamaskJobTypes
from ...common_classes.damask_job import StopCondition
from ...common_functions import damask_helper

from .error_handling import request_damask_grid_to_stop_or_force_it # type: ignore
from ...common_classes import messages

from ..common_classes_damask_monitor.stop_conditions.yielding.stress_strain_curve_plasticity import slope_stress_strain_curve_monitor
from ..common_classes_damask_monitor.stop_conditions.yielding.modulus_degradation import modulus_degradation_monitor
from ..common_classes_damask_monitor.stop_conditions.yielding.plastic_work import plastic_work_monitor

from ..post_processor.plots import plot_modulus_degradation_monitor
from ..post_processor.plots import plot_stress_strain_curves_monitor

# class SolverSettings:
#     def __init__(self, problem_definition, damask_job):
#         self.cpu_cores = problem_definition.solver.cpu_cores
#         self.stop_after_subsequent_parsing_errors  = problem_definition.solver.stop_after_subsequent_parsing_errors

#         self.FFT_iter = problem_definition.solver.FFT_iter
#         self.num_cutbacks = problem_definition.solver.num_cutbacks
#         self.simulation_time = problem_definition.solver.simulation_time

#         match damask_job.simulation_type:
#             case "yield_point":
#                 self.N_increments = problem_definition.solver.N_increments
#             case "elastic_tensor":
#                 self.N_increments = 1
#             case _:
#                 raise Exception(f"Solver settings for {damask_job.simulation_type} is not yet implemented")
        


def create_launch_command(problem_definition: ProblemDefinition, damask_job: DamaskJobTypes) -> tuple[list[str], dict[str, str]]:


    executable = [f"DAMASK_grid"]
    grid = [f"--geom", f"{damask_job.runtime.grid_file}"]
    loadcase = [f"--load", f"{damask_job.runtime.loadcase_file}"]
    material = [f"--material", f"{damask_job.runtime.material_properties_file}"]
    numerics = [f"--numerics", f"{damask_job.runtime.numerics_file}"]
    jobname = [f"--jobname", f"{problem_definition.general.project_name}"]
    work_directory = [f"--workingdirectory", f"{damask_job.runtime.damask_files}"]
    
    launch_command = executable
    arguments = grid + loadcase + material + numerics + jobname + work_directory

    if getattr(problem_definition.general.path,"restart_file_path",False):
        restart = [f"--restart", f"{damask_job.runtime.restart_file_incs-1}"]
        arguments = grid + loadcase + material + numerics + jobname + work_directory + restart

    # if damask_job.use_restart_file:
    #     restart = [f"--restart", f"{damask_job.use_restart_number}"]
    #     launch_command = launch_command + restart

    env = os.environ.copy()
    if not problem_definition.solver.cpu_cores == 0:
        env["OMP_NUM_THREADS"] = f"{problem_definition.solver.cpu_cores}"

    return launch_command + arguments, env

def check_if_damask_result_file_exists(damask_job: DamaskJobTypes, sleep_time: float) -> bool:
    file_exists = os.path.isfile(damask_job.runtime.damask_result_file)
    if not file_exists:
        messages.Status.intermediate_result_file_not_found() # type: ignore
        normal_end_of_loop_messages_and_wait_untill_next_loop(sleep_time)
    return file_exists

def result_file_is_updated(damask_job: DamaskJobTypes, increment_data: IncrementData) -> bool:
    time_new_result_file_updated = os.path.getmtime(damask_job.runtime.damask_result_file)
    time_last_result_file_updated = increment_data.last_file_timestamp
    file_is_updated = time_new_result_file_updated > time_last_result_file_updated
    if not file_is_updated:
        messages.Status.intermediate_results_file_not_yet_updated(increment_data.sleep_time, increment_data.increment_last_update) # type: ignore
        normal_end_of_loop_messages_and_wait_untill_next_loop(increment_data.sleep_time)
    else:
        increment_data.last_file_timestamp = time_new_result_file_updated
    return file_is_updated

def check_if_damask_is_writing_to_file(damask_job: DamaskJobTypes, sleep_time: float) -> bool:
    damask_folder = os.path.dirname(damask_job.runtime.damask_result_file)
    damask_files_folder_files = os.listdir(damask_folder)
    is_lock_file = [".lock" in file_name and not "restart" in file_name for file_name in damask_files_folder_files]
    if any(is_lock_file):
        print(f"DAMASK_grid is writing to a file.")
        is_currently_writing = True
        normal_end_of_loop_messages_and_wait_untill_next_loop(sleep_time)
        return is_currently_writing
    else:
        is_currently_writing = False
        return is_currently_writing

def normal_end_of_loop_messages_and_wait_untill_next_loop(sleep_time: float):
    messages.Status.monitor_loop_complete_sleep(sleep_time) # type: ignore
    messages.Status.end_of_this_loop()
    time.sleep(sleep_time)

def ended_loop_with_error_and_wait_untill_next_loop(sleep_time: float):
    messages.Status.retry_update_after_error_in(sleep_time) # type: ignore
    messages.Status.end_of_this_loop()
    time.sleep(sleep_time)

def copy_and_read_newest_damask_result_file(
        problem_definition: ProblemDefinition,
        damask_job: DamaskJobTypes, 
        increment_data: IncrementData, 
        damask_grid_process: subprocess.Popen # type: ignore
        ) -> tuple[damask.Result, IncrementData]:
    
    shutil.copy2(damask_job.runtime.damask_result_file, damask_job.runtime.damask_temporary_result_file)
    try:
        damask_result_update = damask.Result(damask_job.runtime.damask_temporary_result_file)
        increment_data.subsequent_parsing_errors = 0
    except Exception:
        damask_result_update = None
        if increment_data.increment_last_update == -1:
            print("Damask is still in initial starting phase.")
            normal_end_of_loop_messages_and_wait_untill_next_loop(sleep_time=increment_data.sleep_time)
        else:
            increment_data = deal_with_damask_result_reading_error(damask_grid_process, problem_definition, increment_data)
            if increment_data.stop_condition_reached:
                increment_data.run_ended_succesfully = False
    return damask_result_update, increment_data # type: ignore

def deal_with_damask_result_reading_error(
        damask_grid_process: subprocess.Popen,  # type: ignore
        problem_definition: ProblemDefinition, 
        increment_data: IncrementData) -> IncrementData:
    # If there was an error while reading the damask result file (expected behavior), stop if this happened too often in a row.
    increment_data.subsequent_parsing_errors += 1
    subsequent_parsing_errors = increment_data.subsequent_parsing_errors
    print("")
    messages.Errors.ERROR
    error_message = traceback.format_exc()
    messages.Warnings.parsing_hdf5_results_error_recoverable( # type: ignore
        error_message, increment_data.subsequent_parsing_errors, 
        problem_definition.solver.stop_after_subsequent_parsing_errors
        )
    if subsequent_parsing_errors > problem_definition.solver.stop_after_subsequent_parsing_errors:
        print("Too many subsequent reading errors detected! Stopping.")
        request_damask_grid_to_stop_or_force_it(damask_grid_process, try_quick_shutdown=True)
        increment_data.stop_condition_reached = True
    else:
        ended_loop_with_error_and_wait_untill_next_loop(increment_data.sleep_time)

    return increment_data
    
def updated_result_contains_new_iteration(
        updated_results: damask.Result, increment_data: IncrementData) -> tuple[bool, IncrementData]:
    ## DAMASK_GRID writes updates to the result file in steps
    ## Hence, it might be that the updated result does not contain the new iteration yet.
    ## So, check and wait untill the iteration number is incremented before 
    ## analysing the result.
    newest_increment_in_updated_results = updated_results.increments_in_range()[-1]
    last_analysed_incremement = increment_data.increment_last_update
    new_iteration_found  = newest_increment_in_updated_results > last_analysed_incremement
    if not new_iteration_found:
        wait_longer_for_results_to_be_fully_written_and_wait_for_next_loop(increment_data.sleep_time)
    
    increment_data.tracked_increments.append(newest_increment_in_updated_results)
    increment_data.increment_last_update = newest_increment_in_updated_results
    return new_iteration_found, increment_data

def wait_longer_for_results_to_be_fully_written_and_wait_for_next_loop(sleep_time: float):
    messages.Status.waiting_longer_for_damask_grid_to_complete_writing_file(sleep_time) # type: ignore
    messages.Status.end_of_this_loop()
    time.sleep(sleep_time)

def first_iteration_completed(increment_data: IncrementData) -> bool:
    newest_increment = increment_data.increment_last_update
    first_iteration_completed = newest_increment > 0
    if not first_iteration_completed:
        messages.Status.no_iterations_calculated_yet(increment_data.sleep_time) # type: ignore
        normal_end_of_loop_messages_and_wait_untill_next_loop(increment_data.sleep_time)
    return first_iteration_completed

def calculate_domain_averaged_stress_and_strain(
        updated_damask_results: damask.Result, 
        increment_data: IncrementData) -> IncrementData:
    
    # This function calculates the homogonized stress and strain for the last iteration

    current_iteration = updated_damask_results.increments_in_range()[-1]

    damask_result_intermediate_pruned = updated_damask_results.view(increments=current_iteration)

    stress_tensor_type = increment_data.stress_tensor_type
    strain_tensor_type = increment_data.strain_tensor_type

    display_prefix = "  "

    (damask_result_intermediate_pruned, plastic_strain_all) = damask_helper.get_averaged_plastic_strain_per_increment(damask_result_intermediate_pruned, strain_tensor_type, display_prefix=display_prefix)
    (damask_result_intermediate_pruned, strain_all) = damask_helper.get_averaged_strain_per_increment(damask_result_intermediate_pruned, strain_tensor_type, display_prefix=display_prefix)
    (damask_result_intermediate_pruned, stress_all) = damask_helper.get_averaged_stress_per_increment(damask_result_intermediate_pruned, stress_tensor_type, display_prefix=display_prefix)

    stress_domain_averaged = np.mean(stress_all,0)
    strain_domain_averaged = np.mean(strain_all,0)
    plastic_strain_domain_averaged = np.mean(plastic_strain_all,0)

    increment_data.add_increment_stress_tensor(stress_domain_averaged)
    increment_data.add_increment_strain_tensor(strain_domain_averaged)
    increment_data.add_increment_plastic_strain_tensor(plastic_strain_domain_averaged)

    return increment_data

def calculate_slip_system_xi_gamma(
        updated_damask_results: damask.Result, 
        increment_data: IncrementData) -> IncrementData:
    
    # This function calculates the homogonized stress and strain for the last iteration

    current_iteration = updated_damask_results.increments_in_range()[-1]

    #damask_result_intermediate_pruned = updated_damask_results.view(increments=current_iteration)

    # stress_tensor_type = increment_data.stress_tensor_type
    # strain_tensor_type = increment_data.strain_tensor_type

    display_prefix = "  "

    (updated_damask_results, xi) = damask_helper.get_slip_system_xi(updated_damask_results, display_prefix=display_prefix)
    (updated_damask_results, gamma) = damask_helper.get_slip_system_gamma(updated_damask_results, display_prefix=display_prefix)

    N_matpoints = np.shape(gamma[0])[0]
    #t = updated_damask_results.times
    gamma_delta = np.zeros_like(gamma)
    for e,inc in enumerate(updated_damask_results.increments):
        if e>0:
            gamma_delta[e,:,:] = (gamma[e,:,:]-gamma[e-1,:,:]) 
            
    Wp_sum = np.sum(gamma_delta * xi) / N_matpoints
    
    increment_data.add_increment_Wp(Wp_sum)
    return increment_data

def check_for_stop_conditions(
        damask_job: DamaskJobTypes,
        increment_data: IncrementData) -> IncrementData:
    # This function redirects to the stop criteria of this damask_job

    match damask_job.stop_condition:
        case StopCondition.Yielding():
            stop_condition_reached = yielding_conditions(damask_job, increment_data)
        case StopCondition.NoConditions():
            stop_condition_reached = False
        case _: # type: ignore
            raise Exception(f"Stop condition {damask_job.stop_condition.name} is not yet implemented in the damask monitor.")
    
    increment_data.stop_condition_reached = stop_condition_reached

    return increment_data

def yielding_conditions(
        damask_job: DamaskJobTypes, 
        increment_data: IncrementData) -> bool:
    # This function redirects to the yield condition of this damask_job

    yield_detected = False
    messages.Actions.starting_analysis()
    timer = datetime.datetime.now()
    match damask_job.stop_condition.yield_condition:
        case 'stress_strain_curve':
            yield_detected, yield_value = slope_stress_strain_curve_monitor(damask_job, increment_data)
        case 'modulus_degradation':
            yield_detected, yield_value = modulus_degradation_monitor(damask_job, increment_data)
        case 'plastic_work':
            yield_detected, yield_value = plastic_work_monitor(damask_job, increment_data)
        case _: 
            raise Exception(f"The {damask_job.stop_condition} has not yet been implemented in the damask monitor")
    

    runtime = datetime.datetime.now() - timer
    messages.Status.completed_duration(runtime)  # type: ignore
    messages.PlasticityCheck.conclusion(yield_detected, yield_value) # type: ignore

    return yield_detected

def make_plots(problem_definition: ProblemDefinition, damask_job: DamaskJobTypes, increment_data: IncrementData):
    if not increment_data.increment_last_update < 2:
        plot_modulus_degradation_monitor(problem_definition, damask_job, increment_data)
        plot_stress_strain_curves_monitor(problem_definition, damask_job, increment_data)

def run_and_monitor_damask(
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJobTypes) -> tuple[bool, DamaskJobTypes]:

    (launch_command, env) = create_launch_command(problem_definition, damask_job)

    if damask_job.use_restart_file and hasattr(damask_job, 'increment_data'):
        increment_data = damask_job.increment_data
    else: 
        increment_data = IncrementData(problem_definition)
        #increment_data.increment_last_update = damask_job.runtime.restart_file_incs-1
    
    # print(launch_command)
    with open(damask_job.runtime.log_file, 'a') as f:
        # Run the command and redirect both stdout and stderr (console messages and errors) to the log file
        damask_grid_process = subprocess.Popen(args=launch_command, env=env, text=True,
                                shell=False, stdout=f, stderr=subprocess.STDOUT)

    # From this point on DAMASK_grid runs independantly from the python process.
    # If DAMASK_grid needs to be closed, this should be done explicitly, even when python encounters a problem.
    # Hence, the entire monitor flow must be within a try: catch: block to cath exceptions (erorrs) and stop
    # DAMASK_grid in case this happens. 
    
    job_number = damask_job.job_number
    total_jobs = damask_job.total_jobs
    
    total_iterations = len(damask_job.target_stress) * problem_definition.solver.N_increments
    # if problem_definition.general.simulation_type=="load_path":
    #     total_iterations = len(damask_job.target_stress) * problem_definition.solver.N_increments
    # else:
    #     total_iterations = len(damask_job.target_stress) 


    
    if getattr(problem_definition.general.path,"history_loadcase_path",False):
        total_iterations = total_iterations + damask_job.runtime.restart_file_incs
        
    # if getattr(problem_definition.load_path,"unloading",False):
    #     total_iterations = total_iterations - 1 + problem_definition.solver.N_increments    
 

    try:
        sleep_time = increment_data.sleep_time

        # Continue for as longs as the DAMASK_grid process is running.
        while damask_grid_process.poll() is None:
            iteration_number = increment_data.increment_last_update
            messages.Status.start_of_this_loop(job_number, total_jobs, iteration_number, total_iterations) # type: ignore

            # Check for the existance of the results .hdf5 file.
            damask_result_file_exists = check_if_damask_result_file_exists(damask_job, sleep_time)
            if not damask_result_file_exists:
                continue
            
            messages.Status.intermediate_results_file_found()

            # Check if the results file is altered by investigating the modification time indicated by the OS.
            result_file_is_updated_since_last_check = result_file_is_updated(damask_job, increment_data)
            if not result_file_is_updated_since_last_check:
                continue
            
            # DAMASK_grid presents a .lock file when the process is currently writing data to a file.
            # Respecting this .lock to prevent reading a unfinished state which causes reading errors.
            damask_is_writing_to_file = check_if_damask_is_writing_to_file(damask_job, sleep_time)
            if damask_is_writing_to_file:
                continue

            messages.Actions.starting_analysis_of_current_iteration()

            # Copy the result file to a temporary file where alterations can be made and no new data will be 
            # written to. 
            # This process can fail if in the time between checking for the .lock file and now damask has 
            # started writing to file. Stopping simulation if this happens too often in subsequent monitoring loops.
            updated_results, increment_data = copy_and_read_newest_damask_result_file(
                problem_definition, damask_job,
                increment_data, damask_grid_process)
            if not increment_data.run_ended_succesfully:
                break
            elif updated_results == None: # type: ignore
                continue

            # Check if there is actually new useable data in the result file.
            result_contains_newer_iteration, increment_data = updated_result_contains_new_iteration(updated_results, increment_data)
            if not result_contains_newer_iteration:
                continue
            
            # The first iteration is always a 0 state, analysing before first is calculated can give undefined behaviour
            first_iteration_is_completed = first_iteration_completed(increment_data)
            if not first_iteration_is_completed:
                continue

            messages.Status.current_iteration(increment_data.increment_last_update) # type: ignore
            messages.Status.tracking_stress_strain()
            
            # Calcuate the stress and strain values and track it in increment_data
            increment_data = calculate_domain_averaged_stress_and_strain(updated_results, increment_data)
            increment_data = calculate_slip_system_xi_gamma(updated_results, increment_data)
            # Check if stopping conditions (yielding criteria) are met 
            increment_data = check_for_stop_conditions(damask_job, increment_data)

            # Make plots so a live image of the simulation can be seen.
            make_plots(problem_definition, damask_job, increment_data)

            # Stop if stopping conditions are met
            if increment_data.stop_condition_reached:
                increment_data.run_ended_succesfully = True
                print("")
                print("Simulation completed")
                messages.Status.end_of_this_loop()
                print("")
                print("[Stopping DAMASK_grid process!]")
                request_damask_grid_to_stop_or_force_it(damask_grid_process, try_quick_shutdown=True, result_file=damask_job.runtime.damask_result_file)
                break

            normal_end_of_loop_messages_and_wait_untill_next_loop(sleep_time)

    except Exception:

        print("~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~ERROR~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~")
        # In case any uncaught errors (exceptions) are thrown, make sure the DAMASK_grid process is terminated as well.
        error_message = traceback.format_exc()
        
        print(error_message)
        request_damask_grid_to_stop_or_force_it(damask_grid_process, try_quick_shutdown=True, result_file=damask_job.runtime.damask_result_file)
        increment_data.run_ended_succesfully = False
    except KeyboardInterrupt:
        print("")
        print("Ctrl+c pressed, requesting DAMASK_grid to stop.")
        request_damask_grid_to_stop_or_force_it(
            damask_grid_process, 
            try_quick_shutdown=True, 
            result_file=damask_job.runtime.damask_result_file, 
            manual_stop=True
        )
        increment_data.run_ended_succesfully = False


    
    # At this point DAMASK_grid should have been closed. Checking to make sure:
    if damask_grid_process.poll() is None:
        print("It was expected that the DAMASK_grid process had closed by now.")
        print("Resending a signal to stop...")
        request_damask_grid_to_stop_or_force_it(damask_grid_process, try_quick_shutdown=True)

    print(f"DAMASK_grid exited with code {damask_grid_process.returncode}", end="")
    match damask_grid_process.returncode:
        case 0:
            print(": Damask ended itself normally.")
        case 1:
            print(": Damask reported a error in the internal logic. Printing out the last entries of the logs to help figure out what is wrong.")
            print("Showing the last 50 lines of out of the DAMASK_grid process:")
            with open(damask_job.runtime.log_file, "r") as log_file:
                lines = log_file.readlines()
                for line in lines[-50:]:
                    print(f"[DAMASK ERROR LOG]: {line}", end='')

            print("\n")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("End of DAMASK_grid log file")
            print("These were the last 50 entries in the log file of DAMASK_grid.")
            print("These were shown because an error occurred in DAMASK_grid.")
            print(f"For the full log file, see: {damask_job.runtime.log_file}")
        case -2:
            print(": Damask ended itself after being requested to do so. Likely because of a keyboard interupt (ctrl+c).")
        case -15:
            print(": Damask ended itself forcefully. Likely because of a keyboard interupt (ctrl+c + ctrl+c) or quick shutdown.")
        case _:
            print(".")
    
    if damask_grid_process.returncode == 1:
        increment_data.run_ended_succesfully = False

    damask_job.increment_data = increment_data
    return increment_data.run_ended_succesfully, damask_job    
