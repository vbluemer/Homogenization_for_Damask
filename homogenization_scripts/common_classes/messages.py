# System packages
import warnings
class DamaskWarning(UserWarning):
    pass
import datetime
import typing



# from input import InputValues as IV
class Stages:
    @typing.no_type_check
    def post_processing():
        print("""

-------------------------------- 
| Starting job post-processing | 
-------------------------------- 
        """)

class Warnings:
    @typing.no_type_check
    def parsing_hdf5_results_error_recoverable(error_message: Warning, subsequent_error_count, max_error_count):
        warnings.warn(f""" 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
A recoverable error has occurred while monitoring the plasticity condition of the simulation: 
While reading the simulation results damask has thrown an error (Result file has missing fields). 
This is expected behavior at the start or sometimes during the simulation.
This error should be resolved after more iterations. 
Currently at {subsequent_error_count} subsequent parsing errors, quiting when this count becomes higher then {max_error_count}.\n
Original error message below: 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """, DamaskWarning)
        print(error_message)
        print(""" 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
End of error message.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """)
    
    @typing.no_type_check
    def parsing_damask_result_missing_increment_keys(error_message):
        warnings.warn(""" 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
A recoverable error has occurred while monitoring the plasticity condition of the simulation: 
While reading the simulation results damask has thrown an error (no increment keys present in simulation data). 
This is expected behavior at the start of the simulation (results file does not contain all information yet). 
This error should be resolved when the solver has performed the first iterations. \n 
Original error message below: 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """, DamaskWarning)
        print(error_message)
        print(""" 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
End of error message. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """)

class Errors:

    @typing.no_type_check
    def ERROR():
        print(""" 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                              ERROR! 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """)
    @typing.no_type_check
    def main_process_error_while_simulation(error_message):
        print("""
The main (python) process has encountered an unrecoverable error while monitoring the DAMASK_grid process. 
See the following error message for context: 
              
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")
        print(error_message)
        print(""" 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
End of error message. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """)

class Status:
    @typing.no_type_check
    def completed():
        print("Completed!")
    
    @typing.no_type_check
    def completed_duration(duration):
        print(f"Completed! ({duration} s)")

    @typing.no_type_check
    def completed_timer(timer):
        duration = datetime.datetime.now() - timer
        Status.completed_duration(duration)

    @typing.no_type_check
    def done():
        print("Done!")

    @typing.no_type_check
    def skipped(reason):
        print(f"Skipped ({reason})")
    
    @typing.no_type_check
    def no_iterations_calculated_yet(sleep_time):
        print(f""" 0.
First iteration not calculated yet, waiting for first results.""")

    @typing.no_type_check
    def intermediate_result_file_not_found():
        print(f"""Results file not found, Damask still starting up?""")
        
    @typing.no_type_check
    def intermediate_results_file_found():
        print('Reading hdf5 results file... Status: ', end='', flush=True)

    @typing.no_type_check
    def applying_plasticity_conditions():
        print("New result found, running plasticity conditions")
    
    @typing.no_type_check
    def waiting_longer_for_damask_grid_to_complete_writing_file(sleep_time):
        print(f"Increment number not changed, DAMASK_grid is likely still writing the result. Retrying in {sleep_time} seconds...")
    
    @typing.no_type_check
    def retry_update_after_error_in(sleep_time):
        print(f"""Retrying update in {sleep_time} seconds...""")
        
    @typing.no_type_check
    def conditions_for_simulation_met():
        print("""
Conditions for completion of the simulation have been reached. Stopping monitoring loop.
""")
        
    @typing.no_type_check
    def intermediate_results_file_not_yet_updated(sleep_time, last_increment):
        print(f"""No new data detected.
Reported iteration:  {last_increment}.""")
        
    @typing.no_type_check
    def wait_for_damask_to_stop():
        print("""Requestion DAMASK_grid to stop itself (SIGINT)... Waiting...
Usually DAMASK_grid finishes the current iteration first. Press ctrl+c again to force quit (might corrupt results file)...""", end='', flush=True)

    @typing.no_type_check
    def received_ctrl_c():
        print("\nCtrl+c Received, stopping monitoring.")

    @typing.no_type_check
    def force_stop_damask():
        print("\nCtrl+c received, forcing DAMASK_grid to quit (SIGTERM)... ", end='', flush=True)

    @typing.no_type_check
    def damask_grid_exit_code(damask_process_status):
        if damask_process_status == None:
            print("""
The DAMASK_grid process is still running in the background!
""")
            return
        if damask_process_status == 0:
            print("""
The DAMASK_grid process finished by itself without any errors (exit_code = 0).
""")
        elif damask_process_status < 0:
            print(f"""
The DAMASK_grid process was terminated by the system (most likely by this python script), exit code={damask_process_status}.
""")
        elif damask_process_status > 0:
            warnings.warn(f"""
The DAMASK_grid process exited reporting it had encountered an error. View the DAMASK_grid.log for more information, exit code={damask_process_status}
""", DamaskWarning)
            
    @typing.no_type_check
    def current_iteration(iteration: int) -> None:
        print(iteration)

    @typing.no_type_check
    def tracking_stress_strain() -> None:
        print()
        print("Tracking stress and strain of newest iteration.")

    @typing.no_type_check
    def start_of_this_loop(job_number: int, total_jobs: int, iteration_number: int, total_iterations: int) -> None:
        print(f"~~~~~~~~~~~~~~~~~~~~~~~[Job {job_number} of {total_jobs} ~ iteration {iteration_number} of {total_iterations}]~~~~~~~~~~~~~~~~~~~~~~~")

    @typing.no_type_check
    def end_of_this_loop():
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n")

    @typing.no_type_check
    def created_simlinked_folder_shortcut():
        print("Placed shortcut to latest simulation results in 99_results/00_latest")

    @typing.no_type_check
    def created_simlinked_folder_shortcut():
        print("Failed to place shortcut to latest simulation results in 99_results/00_latest")

    @typing.no_type_check
    def monitor_loop_complete_sleep(sleep_time):
        print(f"Completed monitor step. Rechecking file in {sleep_time} seconds.")

@typing.no_type_check
class Actions:
    def list_outputs(self):
        print(""" \n
[Producing outputs]""")
        
    @typing.no_type_check
    def define_output(output_name: str):
        print(f"{output_name}: ", end='', flush=True)
    
    @typing.no_type_check
    def calculate_field(field_name: str, prefix: str = "") -> None:
        print(f"""{prefix}Calculating: {field_name}... """, end='', flush=True)

    @typing.no_type_check
    def producing_stress_strain_curves():
        print("""Producing stress strain curves...""", end='', flush=True)

    @typing.no_type_check
    def producing_monitor_stress_strain_curves():
        print("""Producing monitoring stress strain curves...""", end='', flush=True)
        
    @typing.no_type_check
    def error_stop_damask():
        print("""Sending request to stop DAMASK_grid process.""")
    
    @typing.no_type_check
    def simulation_done_stop_damask():
        print("""Sending signal to DAMASK_grid to stop.""")

    @typing.no_type_check
    def starting_analysis_of_current_iteration():
        print("Result file is modified.", flush=True)
        print("Reported iteration: ", end="", flush=True)

    @typing.no_type_check
    def starting_analysis():
        print("")
        print("Testing yielding conditions...", end="")
    
    @typing.no_type_check
    def too_many_subsequent_errors_stopping():
        print("Number of allowed subsequent parsing errors exceeded, stopping the simulation")
        



class PlasticityCheck:    
    @typing.no_type_check
    def conclusion(plasticity, yield_value):
        print(f"Yield detected in current iteration: {plasticity}, current yield value: {yield_value}")
        print("")
        

        
