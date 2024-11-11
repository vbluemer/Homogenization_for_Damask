import subprocess
import click
import os

def ask_to_continue_or_stop() -> bool:
    stop_program = not click.confirm("Forcefully stopped Damask. Want to continue with the other jobs? (default = No)", default=False)
    continue_program = not stop_program
    if continue_program: 
        return continue_program
    else:
        exit()

def request_damask_grid_to_stop_or_force_it(
        damask_grid_process: subprocess.Popen, # type: ignore
        try_quick_shutdown: bool = False, 
        result_file: str = '', 
        manual_stop:bool =False
    ) -> bool: # type: ignore

    # This function quits the DAMASK_grid process
    # If setup to, it will try quit damask forcefully (quick_shutdown) if DAMASK_grid is currently not 
    # writing to a result file (a .lock file exists in this case). If that exists, just request the process
    # to stop which should not take too long as it is already at the end of an iteration.
    # NOTE: quick shutdown can happen in between the moment when the result_file and the restart_file
    # is being writen. Hence, disable quick_shutdown when these must remain synchronized (restart_file only contains the information on one iteration)

    # When request is send to DAMASK_grid, DAMASK_grid will complete the iteration it is currently working on (can take significant time).
    # ctrl+c can be pressed during this time to forcefully close the process, .lock files will not be 
    # respected in this case, so the danger for corrupted results_file exists.

    if try_quick_shutdown:
        quick_shutdown_succesful = quick_shutdown(damask_grid_process, result_file)
        if quick_shutdown_succesful:
            continue_program = True
            if manual_stop:
                continue_program = ask_to_continue_or_stop()
                return continue_program
            else:
                continue_program = True
                return continue_program

    try:
        damask_grid_process.send_signal(2)
        print("Sent message to DAMASK_grid to close, this can take a while as DAMASK_grid finishes the last iteration.")
        print("Press ctrl+c to force DAMASK_grid to close. WARNING: This can corrupt the results file needed for post-processing!")
        damask_grid_process.wait()
        continue_program = True
        if manual_stop:
            continue_program = ask_to_continue_or_stop()
            return continue_program
        else:
            continue_program = True
            return continue_program
        
    except KeyboardInterrupt:
        damask_grid_process.send_signal(15)
        damask_grid_process.wait()
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        if manual_stop:
            continue_program = ask_to_continue_or_stop()
            return continue_program
        else:
            continue_program = True
            return continue_program


def quick_shutdown(damask_grid_process: subprocess.Popen, result_file: str) -> bool: # type: ignore
    damask_folder = os.path.dirname(result_file)
    damask_files_folder_files = os.listdir(damask_folder)
    is_lock_file = [".lock" in file_name for file_name in damask_files_folder_files]
    if any(is_lock_file):
        can_shutdown_quickly = False
        print("DAMASK_grid is updating files, requesting DAMASK_grid to stop after to prevent file corruption.")
        return can_shutdown_quickly
    else:
        print("DAMASK_grid does not seem to be updating any files, performing quick shutdown of DAMASK_grid.")
        damask_grid_process.send_signal(15)
        damask_grid_process.wait()
        quick_shutdown_performed = True
        return quick_shutdown_performed