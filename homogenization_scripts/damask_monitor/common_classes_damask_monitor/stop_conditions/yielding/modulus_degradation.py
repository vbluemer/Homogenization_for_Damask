# System packages
import numpy as np
from numpy.typing import NDArray
import damask # type: ignore
import scipy.optimize # type: ignore

# Local packages
from .....common_functions import damask_helper 
from ....common_classes_damask_monitor.increment_data import IncrementData
from .....common_classes.damask_job import DamaskJobTypes 
from .....common_classes.problem_definition import ProblemDefinition
from ....post_processor.interpolate_results import InterpolatedResults
from ....post_processor.plots import plot_modulus_degradation, plot_stress_strain_curves

# def calculate_linear_deformation_energy(
#         stress_tensor: NDArray[np.float64],
#         strain_tensor: NDArray[np.float64]) -> float:

#     stress_vector = damask_helper.stress_tensor_to_vector_notation(stress_tensor)
#     stress_vector_transposed = np.transpose(stress_vector)

#     strain_vector = damask_helper.strain_tensor_to_vector_notation(strain_tensor)

#     deformation_energy_linear = 0.5 * np.matmul(stress_vector_transposed, strain_vector)

#     return deformation_energy_linear


# def calculate_linear_deformation_stiffness(
#         stress_tensor: NDArray[np.float64],
#         strain_tensor: NDArray[np.float64],) -> float:
    
#     strain_vector = damask_helper.strain_tensor_to_vector_notation(strain_tensor)

#     strain_norm = float(np.linalg.norm(strain_vector))

#     deformation_energy_linear = calculate_linear_deformation_energy(stress_tensor, strain_tensor)

#     deformation_stiffness_linear = deformation_energy_linear / strain_norm**2

#     return deformation_stiffness_linear


def modulus_degradation_and_value(
        yield_value: float, 
        stress_iteration_1: NDArray[np.float64], 
        strain_iteration_1: NDArray[np.float64], 
        stress: NDArray[np.float64],
        strain: NDArray[np.float64]) -> tuple[bool, float]:
    
    deformation_stiffness_linear = damask_helper.calculate_linear_modulus(stress_iteration_1, strain_iteration_1)
    deformation_stiffness = damask_helper.calculate_linear_modulus(stress, strain)

    normalized_linear_deformation_stiffness = deformation_stiffness / deformation_stiffness_linear 

    non_linear_deformation_condition = abs(normalized_linear_deformation_stiffness-1) > yield_value

    if non_linear_deformation_condition:
        non_linear_stiffness_detected = True
        
    else:
        non_linear_stiffness_detected = False

    return non_linear_stiffness_detected, np.squeeze(abs(normalized_linear_deformation_stiffness-1))

def modulus_degradation(
        yield_value: float, 
        stress_iteration_1: NDArray[np.float64], 
        strain_iteration_1: NDArray[np.float64], 
        stress: NDArray[np.float64],
        strain: NDArray[np.float64]) -> bool:
    # This function redirects to the modulus_degradation_and_value function while pruning its output

    yield_deteced, _ = modulus_degradation_and_value(yield_value, stress_iteration_1, strain_iteration_1, stress, strain)

    return yield_deteced

def interpolation_fraction(
        yield_value: float, 
        stress_linear: NDArray[np.float64], 
        strain_linear: NDArray[np.float64], 
        stress_before_yield: NDArray[np.float64], 
        strain_before_yield: NDArray[np.float64], 
        stress_after_yield: NDArray[np.float64],
        strain_after_yield: NDArray[np.float64]) -> float:
    # This function finds to interpolate between the loadstates before and after yield such that the yield condition is met.
    # It is assumed that the yielding actually happens in between the load states
    
    # Returns the fraction for interpolation (x): stress_yield = stress_before + x * (stress_after - stress_before)

    stiffness_linear = damask_helper.calculate_linear_modulus(stress_linear, strain_linear)
    stiffness_before = damask_helper.calculate_linear_modulus(stress_before_yield, strain_before_yield)
    stiffness_after = damask_helper.calculate_linear_modulus(stress_after_yield, strain_after_yield)

    normalized_stiffness_before = stiffness_before / stiffness_linear
    normalized_stiffness_after = stiffness_after / stiffness_linear

    strain_vector_before = damask_helper.strain_tensor_to_vector_notation(strain_before_yield)
    strain_vector_after = damask_helper.strain_tensor_to_vector_notation(strain_after_yield)
    strain_norm_before = float(np.linalg.norm(strain_vector_before))
    strain_norm_after = float(np.linalg.norm(strain_vector_after))

    slope_stiffness_over_strain = (normalized_stiffness_after - normalized_stiffness_before) / (strain_norm_after - strain_norm_before)
    if slope_stiffness_over_strain >=0:
        threshold = 1+yield_value
    else:
        threshold = 1-yield_value
        
    modulus_linear = damask_helper.calculate_linear_modulus(stress_linear, strain_linear)

    # Finding the intersection of the yield condition and the interpolated state with a optimizer
    # Due non-linearity involved in the relationship between stress/strain and modulus.
    def objective_function(x: float) -> float:
        stress = stress_before_yield + x*(stress_after_yield - stress_before_yield)
        strain = strain_before_yield + x*(strain_after_yield - strain_before_yield)
        modulus = damask_helper.calculate_linear_modulus(stress, strain)

        normalized_modulus = modulus / modulus_linear

        objective_value = (normalized_modulus-threshold)**2 
        return objective_value

    optimization_result = scipy.optimize.minimize_scalar(objective_function, options={'disp': False}, method="Golden")

    fraction_for_interpolation = optimization_result.x
    # fraction_for_interpolation = ( strain_norm_yield - strain_norm_before ) / ( strain_norm_after - strain_norm_before )

    return fraction_for_interpolation
    

def modulus_degradation_monitor(damask_job: DamaskJobTypes, increment_data: IncrementData) -> tuple[bool, float]:
    # This function is used during monitoring of the DAMASK_grid process and test for yielding by the modulus degradation.

    # Output of this function is true or false for yielding detection and the degradation of the modulus.

    current_iteration = increment_data.increment_last_update
    if current_iteration == 0:
        yield_detected = False
        return yield_detected, 0
    
    stress_iteration_1: NDArray[np.float64] = increment_data.stress_averaged_per_increment[1]
    stress_current: NDArray[np.float64] = increment_data.stress_averaged_per_increment[-1]

    strain_iteration_1: NDArray[np.float64] = increment_data.strain_averaged_per_increment[1]
    strain_current: NDArray[np.float64] = increment_data.strain_averaged_per_increment[-1]

    yield_value = damask_job.stop_condition.yield_value

    # If there is an error in the code, the yield value will not be set, likely stop conditions have gotten mixed up.
    if  yield_value is None:
        raise Exception("Yield value has not been set for the yielding condition. This should not be possible, please report it if you find this error.")


    yield_detected, yield_value = modulus_degradation_and_value(yield_value,
                                         stress_iteration_1, strain_iteration_1,
                                        stress_current, strain_current)

    if yield_detected:
        print(f"Yielding detected in the deformation energy condition")
    
    return yield_detected, yield_value

def modulus_degradation_post_process(problem_definition: ProblemDefinition, damask_job: DamaskJobTypes) -> InterpolatedResults | None:
    # This function finds the yield point occourding to modulus degradation. This is meant to be run after the simulation is completed.

    # Output is the interpolated stress/strain state at which the yielding condition is met. 
    damask_results       = damask.Result(damask_job.runtime.damask_result_file)

    stress_tensor_type = problem_definition.general.stress_tensor_type
    strain_tensor_type = problem_definition.general.strain_tensor_type

    display_prefix = "[Post process] "

    (damask_results, stress_averaged_per_increment) = damask_helper.get_averaged_stress_per_increment(damask_results, stress_tensor_type, display_prefix=display_prefix)
    (damask_results, strain_averaged_per_increment) = damask_helper.get_averaged_strain_per_increment(damask_results, strain_tensor_type, display_prefix=display_prefix)

    stored_iteration = damask_results.increments_in_range()

    stress_iteration_1 = stress_averaged_per_increment[1]
    strain_iteration_1 = strain_averaged_per_increment[1]

    yield_value = damask_job.general_yield_value_modulus_degradation

    iteration_before_yield = 0
    iteration_after_yield  = 0
    yield_found = False

    # detect iteration numbers with yielding
    for iteration in stored_iteration:
        if iteration == 0:
            continue

        stress = stress_averaged_per_increment[iteration]
        strain = strain_averaged_per_increment[iteration]

        yield_detected = modulus_degradation(yield_value,
                                             stress_iteration_1, strain_iteration_1,
                                             stress, strain)
        
        if yield_detected:
            iteration_before_yield = iteration - 1
            iteration_after_yield = iteration
            yield_found = True
            break


    
    if not yield_found:
        plot_stress_strain_curves(problem_definition, damask_job, stress_averaged_per_increment,strain_averaged_per_increment)
        plot_modulus_degradation(problem_definition, damask_job, stress_averaged_per_increment,strain_averaged_per_increment)
        yield_detected = False
        return None 
    
    stress_before_yield = stress_averaged_per_increment[iteration_before_yield]
    strain_before_yield = strain_averaged_per_increment[iteration_before_yield]

    stress_after_yield = stress_averaged_per_increment[iteration_after_yield]
    strain_after_yield = strain_averaged_per_increment[iteration_after_yield]
    
    fraction_for_interpolation = interpolation_fraction(yield_value,
                                                        stress_iteration_1, strain_iteration_1,
                                                        stress_before_yield, strain_before_yield,
                                                        stress_after_yield, strain_after_yield)

    # interpolate the yield value

    interpolated_results = InterpolatedResults(fraction_for_interpolation, damask_results, iteration_before_yield, iteration_after_yield,stress_tensor_type, strain_tensor_type)

    damask_results = damask_results.view_all()
    # Make the plots including the interpolated yield point
    plot_stress_strain_curves(problem_definition, damask_job, stress_averaged_per_increment,strain_averaged_per_increment, interpolated_results)
    plot_modulus_degradation(problem_definition, damask_job, stress_averaged_per_increment,strain_averaged_per_increment, interpolated_results)

    post_process_succeeded = True # type: ignore
    return  interpolated_results