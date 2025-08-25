# System packages
import os
import click
from itertools import chain
import numpy as np
import textwrap

# Local packages
from ..common_classes.problem_definition import ProblemDefinition
from ..common_classes.damask_job import DamaskJob, DamaskJobTypes
from ..damask_monitor.common_classes_damask_monitor.stop_conditions.stop_conditions import StopCondition

def summarize_plastic_strain_yield(yield_value: float):
    pass

def summarize_elastic_energy_yield(yield_value: float):
    pass

def summarize_reuse_of_results(problem_definition: ProblemDefinition):
    print(f"Earlier results have been found: {problem_definition.reused_results.existing_results_found}")
    if not problem_definition.reused_results.existing_results_found:
        return

    print(f"General settings of the existing simulation setting match the current: {problem_definition.reused_results.general_settings_match}")
    if not problem_definition.reused_results.general_settings_match:
        print(f"Listed reason(s) why general simulations do not match: {"".join(problem_definition.reused_results.reasons_general_settings_refused)}")
        return

    print("")
    if problem_definition.reused_results.reused_values == {}:
        print("No results have been reused.")
    else:
        print("The following results have been reused:")
        for simulation_type in problem_definition.reused_results.reused_values:
            for field_name in problem_definition.reused_results.reused_values[simulation_type]:
                print(f"    [{simulation_type}]: {field_name}")
    
    print("")
    if problem_definition.reused_results.reevaluated_simulation_type == {}:
        print("No results have been marked to be reevaluated.")
    else:
        print("The following results have been marked to be reevaluated:")
        for simulation_type in problem_definition.reused_results.reevaluated_simulation_type:
            print(f"    [{simulation_type}]: {"".join(problem_definition.reused_results.reason_reevaluated_simulation_type[simulation_type])}")
            

def summarize_yield_point_job(job: DamaskJob.YieldPointMultiaxial):
    print("    Job type: yield_point")
    print(f"    Load applied in direction: {job.field_name}")
    if not job.reduce_parasitic_stresses:
        message = "1st Piola-Kirchoff stress"
    else:
        message = "Cauchy stress (itterative)"

    number_of_load_steps = len(job.target_stress)
    print(f"    Number of load steps: {number_of_load_steps}")
    target_stress_step = job.target_stress[-1]
    print("")
    print(f"""    Increasing {message} boundary condition with {number_of_load_steps} steps to:
        [{target_stress_step[0][0]}, {target_stress_step[0][1]}, {target_stress_step[0][2]}],
        [{target_stress_step[1][0]}, {target_stress_step[1][1]}, {target_stress_step[1][2]}],
        [{target_stress_step[2][0]}, {target_stress_step[2][1]}, {target_stress_step[2][2]}]""")
    target_stress_flattened = list(chain(*job.target_stress[-1]))
    max_stress_value = max([num for num in target_stress_flattened if isinstance(num, (int,float))], key=abs)
    print(f"    Expecting yielding beheavior at stress: {max_stress_value}")
    print(f"    {job.stop_condition}")

def summarize_elastic_tensor_job(job: DamaskJob.ElasticTensor):
    print("    Job type: elastic tensor")
    print(f"    Strain applied: {job.field_name}")

    F = job.deformation_gradient_tensor[0]
    print("")
    print(f"""    Displacement gradient tensor:
    [{F[0][0]}, {F[0][1]}, {F[0][2]}],
    [{F[1][0]}, {F[1][1]}, {F[1][2]}],
    [{F[2][0]}, {F[2][1]}, {F[2][2]}]""")
    

def summarize_yield_surface_job(job: DamaskJob.YieldPointMultiaxial):
    print("    Job type: yield_point_multiaxial")
    print(f"    Load case: {job.field_name}")

    if not job.reduce_parasitic_stresses:
        message = "1st Piola-Kirchoff stress"
    else:
        message = "Cauchy stress (itterative)"

    number_of_load_steps = len(job.target_stress)
    print(f"    Number of load steps: {number_of_load_steps}")
    target_stress_step = job.target_stress[number_of_load_steps-1]
    print("")
    print(f"""    Increasing {message} boundary condition with {number_of_load_steps} steps to:
    [[{target_stress_step[0][0]}, {target_stress_step[0][1]}, {target_stress_step[0][2]}],
    [{target_stress_step[1][0]}, {target_stress_step[1][1]}, {target_stress_step[1][2]}],
    [{target_stress_step[2][0]}, {target_stress_step[2][1]}, {target_stress_step[2][2]}]]""")
    print(f"    Angle in plane: {job.angle_in_plane}°")
    print(textwrap.fill(f"    {job.stop_condition}",width=80))


def summarize_load_path_job(job: DamaskJob.LoadPath):
    print("    Job type: load_path")
    breakpoint()
    if job.prescribed_stress:
        number_of_load_steps = len(job.target_stress)
        if not job.reduce_parasitic_stresses:
            message = "1st Piola-Kirchoff stress"
        else:
            message = "Cauchy stress (itterative)"
    
        target_stress_step = job.target_stress[-1]
        print("")
        print(f"""    Increasing {message} boundary condition with {number_of_load_steps} steps to:
            [{target_stress_step[0][0]}, {target_stress_step[0][1]}, {target_stress_step[0][2]}],
            [{target_stress_step[1][0]}, {target_stress_step[1][1]}, {target_stress_step[1][2]}],
            [{target_stress_step[2][0]}, {target_stress_step[2][1]}, {target_stress_step[2][2]}]""")
    
        print(textwrap.fill(f"    {job.stop_condition}",width=80))
    else:
        number_of_load_steps = len(job.target_F)
        
        message = "deformation gradient"
    
        target_F_step = job.target_F[-1]
        print("")
        print(f"""    Increasing {message} boundary condition with {number_of_load_steps} steps to:
            [{target_F_step[0][0]}, {target_F_step[0][1]}, {target_F_step[0][2]}],
            [{target_F_step[1][0]}, {target_F_step[1][1]}, {target_F_step[1][2]}],
            [{target_F_step[2][0]}, {target_F_step[2][1]}, {target_F_step[2][2]}]""")
    
        print(textwrap.fill(f"    {job.stop_condition}",width=80))

def summarize_tasks(problem_definition: ProblemDefinition, jobs_list: list[DamaskJobTypes]):
    print("")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"            Summary of simulation settings for project: {problem_definition.general.project_name}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    print("--------------------------------")
    print("|    Input and output files    |")
    print("--------------------------------")
    print(f"The project folder is located at: {problem_definition.general.path.project_path}")
    print(f"The used problem definition is located at: {problem_definition.general.path.problem_definition_file}")
    print(f"The results will be stored at: {problem_definition.general.path.results_folder}")
    print(f"A database of all results will be written to: {problem_definition.general.path.results_database_file}")
    print("")
    print("--------------------------------")
    print("|     General information      |")
    print("--------------------------------")
    print(f"Selected type to run: {problem_definition.general.simulation_type}")
    print(f"Definition of stress tensor: {problem_definition.general.stress_tensor_type}")
    print(f"Definition of strain tensor: {problem_definition.general.strain_tensor_type}")
    print(f"For post processing purposes, the number of dimensions is assumed to be: {problem_definition.general.dimensions}")
    print(f"The following files will be passed to Damask:")
    print(f"- Material properties: {problem_definition.general.path.material_properties} (Found)")
    # print(f"- Grain orientation: {problem_definition.general.path.grain_orientation} (Found)")
    print(f"- Grid: {problem_definition.general.path.grid_file} (Found)")
    _, file_extension = os.path.splitext(problem_definition.general.path.grid_file)
    if file_extension == '.txt':
        print(f"- Grid dimensions: {problem_definition.general.path.dimensions_file}")
    print("")
    print("--------------------------------")
    print("|     Queued Damask job(s)     |")
    print("--------------------------------")
    print(f"A queue of {len(jobs_list)} job(s) has been created.")
    print(f"Listing the queued job(s)...")
    job_counter = 1
    for job in jobs_list:
        print("")
        print(f"    ~~~~~~~~~ Job {job_counter} of {len(jobs_list)} ~~~~~~~~~")
        match job.simulation_type:
            case 'yield_point':
                summarize_yield_point_job(job) # type: ignore
            case 'load_path':
                summarize_load_path_job(job) # type: ignore
            case 'yield_surface':
                summarize_yield_surface_job(job) # type: ignore
            case 'elastic_tensor':
                summarize_elastic_tensor_job(job)
            case _: # type: ignore
                print(f"    Summary of job type {job.simulation_type} is not yet implemented...")

        job_counter+=1
    print("")
    if problem_definition.general.path.restart_file_path:
        print("--------------------------------")
        print("|       Restart files          |")
        print("--------------------------------")
        print(f"Restarting simulations from file: {problem_definition.general.path.restart_file_path}")
        print(f"With history loadcase: {problem_definition.general.path.history_loadcase_path}")
        print("")
    print("--------------------------------")
    print("|       Reuse of results       |")
    print("--------------------------------")
    summarize_reuse_of_results(problem_definition)
    print("")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("%                        Confirmation                        %")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    summary_accept_promt = "Start running queued jobs? Default = Yes"
    if not problem_definition.general.automatic_reevaluate:
        user_continue = click.confirm(summary_accept_promt, default=True)
    else:
        user_continue = True

    return user_continue