# System packages
import damask

# Local packages 
from ...common_classes.damask_job import DamaskJobTypes, DamaskJob
from ...common_classes.problem_definition import ProblemDefinition
from ...common_classes import messages
from ...common_functions import damask_helper
from ..common_classes_damask_monitor.stop_conditions.yielding.modulus_degradation import modulus_degradation_post_process
from ..common_classes_damask_monitor.stop_conditions.yielding.plastic_work import plastic_work_post_process
from ..common_classes_damask_monitor.stop_conditions.yielding.stress_strain_curve_plasticity import slope_stress_strain_curve_post_process
from .load_path.load_path_post_processor import load_path_post_process
from .interpolate_results import InterpolatedResults
from .store_result_to_database import store_result_to_database


def yield_point_post_processing(
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJob.YieldPointMultiaxial) -> InterpolatedResults | None:
    
    match damask_job.stop_condition.yield_condition:
        case 'modulus_degradation':
            interpolated_results = modulus_degradation_post_process(problem_definition, damask_job)
        case 'stress_strain_curve':
            interpolated_results = slope_stress_strain_curve_post_process(problem_definition, damask_job)
        case 'plastic_work':
            interpolated_results = plastic_work_post_process(problem_definition, damask_job)
        case _:
            raise Exception(f"Yield point post processing of damask results not yet implemented for {damask_job.stop_condition.yield_condition}")

    return interpolated_results

def load_path_post_processing(
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJob.LoadPath) -> bool:
    
    process_succesfull = load_path_post_process(problem_definition, damask_job)

    return process_succesfull


def run_post_processing_job(
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJobTypes) -> bool:
    # This function selects the post processing to run on a job.
    # Job post-processing involves finding certain stress/strain or yield point and storing this 
    # to the results_database for use in the general post post-processing
    messages.Stages.post_processing()

    match damask_job:
        case DamaskJob.LoadPath():
            # load_path post-processing saves the homogenized stresses and strains for each iteration
            post_process_succeeded = load_path_post_processing(problem_definition, damask_job)
        case DamaskJob.YieldPointMultiaxial():
            # Used for yield_surface and yield_point. Saves the stress state at the interpolated yield point.
            # NO_YIELD_DETECTED if the simulation did not find yielding.

            interpolated_result = yield_point_post_processing(problem_definition, damask_job)
            if interpolated_result is None:
                post_process_succeeded = False
                value_to_store = [
                    ["NO_YIELD_DETECTED", "NO_YIELD_DETECTED", "NO_YIELD_DETECTED"],
                    ["NO_YIELD_DETECTED", "NO_YIELD_DETECTED", "NO_YIELD_DETECTED"],
                    ["NO_YIELD_DETECTED", "NO_YIELD_DETECTED", "NO_YIELD_DETECTED"]
                ]
            else:
                post_process_succeeded = True
                value_to_store = interpolated_result.stress
            store_result_to_database(problem_definition, damask_job.simulation_type, damask_job.field_name, value_to_store)
        case DamaskJob.ElasticTensor():
            # elastic_tensor jobs store the stress and strains at the strain step.
            value_to_store = dict()
            value_to_store["stress"] = list()
            value_to_store["strain"] = list()

            damask_results       = damask.Result(damask_job.runtime.damask_result_file)

            stress_tensor_type = problem_definition.general.stress_tensor_type
            strain_tensor_type = problem_definition.general.strain_tensor_type

            (damask_results, stress_averaged_per_increment) = damask_helper.get_averaged_stress_per_increment(damask_results, stress_tensor_type)
            (damask_results, strain_averaged_per_increment) = damask_helper.get_averaged_strain_per_increment(damask_results, strain_tensor_type)

            value_to_store['stress'] = stress_averaged_per_increment[-1].tolist()
            value_to_store['strain'] = strain_averaged_per_increment[-1].tolist()

            store_result_to_database(problem_definition, damask_job.simulation_type, damask_job.field_name, value_to_store)

            post_process_succeeded = True
        case _: # type: ignore
            raise Exception(f"Post processing of damask results not yet implemented for {damask_job.simulation_type}")
    
    return post_process_succeeded

