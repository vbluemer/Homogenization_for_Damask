    # System packages
import numpy as np
from numpy.typing import NDArray
import damask # type: ignore

# Local packages
from .....common_functions import damask_helper 
from .....common_classes.damask_job import DamaskJobTypes
from .....common_classes.problem_definition import ProblemDefinition
from ....post_processor.interpolate_results import InterpolatedResults
from .....common_functions import damask_helper
from ....common_classes_damask_monitor.increment_data import IncrementData
from ....post_processor.plots import plot_stress_strain_curves, plot_modulus_degradation

def slope_stress_strain_curve_and_value(
        yield_value: float, 
        loaded_directions: list[list[bool]],
        stress_iteration_1: NDArray[np.float64], 
        strain_iteration_1: NDArray[np.float64], 
        stress: NDArray[np.float64],
        strain: NDArray[np.float64]) -> tuple[bool, float]:
    # This function checks the given stress/strain state for yielding by permanent plastic strain.
    # A direction must be loaded for detection to be enabled (numerical errors would otherwise trigger this condition)

    # NOTE: This function will complete without raising errors even in combined load cases.

    # Returns true or false for yielding detected and the highest plastic strain detected (in loaded direction)

    # Slope stress/strain curve linear domain
    slope_stress_strain_curve_linear = stress_iteration_1 / strain_iteration_1
    #breakpoint()
    # Deduction of elastic strain from total strain
    plastic_strain = strain - stress / slope_stress_strain_curve_linear
    
    # Comparison of plastic strain with yielding condition
    yielding_in_direction = abs(plastic_strain) > yield_value

    # Apply condition that direction is actifly being loaded
    yielding_in_loaded_direction = yielding_in_direction & loaded_directions

    any_yielding_in_a_loaded_direction = any(sum(yielding_in_loaded_direction.tolist(),[])) # type: ignore

    max_yielding_value = 0
    for i in range(3):
        for j in range(3):
            if loaded_directions[i][j]:
                yield_value_direction = abs(plastic_strain[i][j])
                if yield_value_direction > max_yielding_value:
                    max_yielding_value = yield_value_direction


    return any_yielding_in_a_loaded_direction, max_yielding_value

def slope_stress_strain_curve(
        yield_value: float, 
        loaded_directions: list[list[bool]],
        stress_iteration_1: NDArray[np.float64], 
        strain_iteration_1: NDArray[np.float64], 
        stress: NDArray[np.float64],
        strain: NDArray[np.float64]) -> bool:
    # This function redirects to the slope_stress_strain_curve_and_value while pruning the output.

    yield_detected, _ = slope_stress_strain_curve_and_value(
        yield_value, loaded_directions, stress_iteration_1, 
        strain_iteration_1, stress, strain)
    
    return yield_detected

def interpolation_fraction(
        yield_value: float, 
        loaded_directions: list[list[bool]],
        stress_linear: NDArray[np.float64], 
        strain_linear: NDArray[np.float64], 
        stress_before_yield: NDArray[np.float64], 
        strain_before_yield: NDArray[np.float64], 
        stress_after_yield: NDArray[np.float64],
        strain_after_yield: NDArray[np.float64]) -> float:
    # This function finds the interpolation between 2 load states where the yielding condition is approximatly met.
    # Yielding should occour in between the loadcases

    # returns the the fraction (x) used for interpolation: stress_yield = stress_1 + x*(stress_2 - stress_1)

    slope_stress_stain_curve_linear = stress_linear / strain_linear
    slope_stress_strain_interpolation = (stress_after_yield - stress_before_yield) / (strain_after_yield - strain_before_yield)

    strain_yield = (stress_before_yield + slope_stress_stain_curve_linear * yield_value - slope_stress_strain_interpolation * strain_before_yield) / (slope_stress_stain_curve_linear - slope_stress_strain_interpolation)

    fraction_for_interpolation_tensor = (strain_yield - strain_before_yield) / (strain_after_yield - strain_before_yield)

    # Assuming uni-axial load case (only one loaded direction that is yielding)
    for i in range(3):
        for j in range(3):
            direction_is_loaded = loaded_directions[i][j]
            if direction_is_loaded:
                fraction_for_interpolation = fraction_for_interpolation_tensor[i][j]
                return fraction_for_interpolation

    # As there should always at least be one loaded direction, this code should be unreachable.
    raise Exception("Interpolation did not find a loaded direction, this should be impossible.")

def slope_stress_strain_curve_monitor(damask_job: DamaskJobTypes, increment_data: IncrementData) -> tuple[bool, float]:
    current_iteration = increment_data.increment_last_update
    # This function formats the data to be used for yield point detection while monitoring damask.
    # Data from the first, second to last and last increment is needed.

    # Returns true or false for yielding and the plastic deformation measured.

    if current_iteration == 0:
        yielding_detected = False
        return yielding_detected, 0

    if getattr(damask_job,"existing_incs",False):
        if len(increment_data.stress_averaged_per_increment)<3:
            yielding_detected = False
            return yielding_detected, 0
        else:
            stress_iteration_1 = increment_data.stress_averaged_per_increment[2] - increment_data.stress_averaged_per_increment[1]
            strain_iteration_1 = increment_data.strain_averaged_per_increment[2] - increment_data.strain_averaged_per_increment[1]
    else:
        stress_iteration_1 = increment_data.stress_averaged_per_increment[1]
        strain_iteration_1 = increment_data.strain_averaged_per_increment[1]
        
    stress_current = increment_data.stress_averaged_per_increment[-1]
    strain_current = increment_data.strain_averaged_per_increment[-1]

    loaded_directions = damask_job.loaded_directions[0]
    #breakpoint()
    yielding_detected, yield_value = slope_stress_strain_curve_and_value(
        damask_job.general_yield_value_plastic_strain, loaded_directions,
        stress_iteration_1, strain_iteration_1,
        stress_current, strain_current)

    return yielding_detected, yield_value

def slope_stress_strain_curve_post_process(problem_definition: ProblemDefinition, damask_job: DamaskJobTypes) -> InterpolatedResults | None:
    # This function finds the two iterations before and after the yielding condition is met. 
    # Intented to be used when the simulation is completed.

    # Returns None if no yielding is found or the fraction used for linear interpolation between the states where yielding is met.

    damask_results       = damask.Result(damask_job.runtime.damask_result_file)
    stress_tensor_type = problem_definition.general.stress_tensor_type
    strain_tensor_type = problem_definition.general.strain_tensor_type

    display_prefix = "[Post process] "

    (damask_results, stress_averaged_per_increment) = damask_helper.get_averaged_stress_per_increment(damask_results, stress_tensor_type, display_prefix=display_prefix)
    (damask_results, strain_averaged_per_increment) = damask_helper.get_averaged_strain_per_increment(damask_results, strain_tensor_type, display_prefix=display_prefix)

    stored_iteration = damask_results.increments_in_range()

    if getattr(damask_job,"existing_incs",False):
        stress_iteration_1 = stress_averaged_per_increment[damask_job.existing_incs + 1] - stress_averaged_per_increment[damask_job.existing_incs]
        strain_iteration_1 = strain_averaged_per_increment[damask_job.existing_incs + 1] - strain_averaged_per_increment[damask_job.existing_incs]
    else:
        stress_iteration_1 = stress_averaged_per_increment[1]
        strain_iteration_1 = strain_averaged_per_increment[1]
    #breakpoint()
    # yield_value = damask_job.general_yield_value_plastic_strain

    iteration_before_yield = 0
    iteration_after_yield  = 0
    yield_found = False


    # detect iteration numbers with yielding
    if getattr(damask_job,"existing_incs",False):
        stored_iteration = [x for x in stored_iteration if x > damask_job.existing_incs]
        
    for iteration in stored_iteration:
        if iteration == 0:
            continue

        stress = stress_averaged_per_increment[iteration]
        strain = strain_averaged_per_increment[iteration]
        
        loaded_directions = damask_job.loaded_directions[0]


        yield_detected = slope_stress_strain_curve(
            damask_job.general_yield_value_plastic_strain, loaded_directions,
            stress_iteration_1, strain_iteration_1,
            stress, strain)
        
        if yield_detected:
            iteration_before_yield = iteration - 1
            iteration_after_yield = iteration
            yield_found = True
            break

    # Produce the completed set of plots including the interpolated yielding value.


    if not yield_found:
        plot_stress_strain_curves(problem_definition, damask_job, stress_averaged_per_increment,strain_averaged_per_increment)
        plot_modulus_degradation(problem_definition, damask_job, stress_averaged_per_increment,strain_averaged_per_increment)
        yield_detected = False # type: ignore
        return None
    
    stress_before_yield = stress_averaged_per_increment[iteration_before_yield]
    strain_before_yield = strain_averaged_per_increment[iteration_before_yield]
    
    stress_after_yield = stress_averaged_per_increment[iteration_after_yield]
    strain_after_yield = strain_averaged_per_increment[iteration_after_yield]
    
    
    loaded_directions = damask_job.loaded_directions[0]

    fraction_for_interpolation = interpolation_fraction(damask_job.general_yield_value_plastic_strain, loaded_directions,
                                                    stress_iteration_1, strain_iteration_1,
                                                    stress_before_yield, strain_before_yield,
                                                    stress_after_yield, strain_after_yield)
    # probably add existing incs here
    
    interpolated_results = InterpolatedResults(fraction_for_interpolation, damask_results, iteration_before_yield, iteration_after_yield, stress_tensor_type, strain_tensor_type)
    breakpoint()

    plot_stress_strain_curves(problem_definition, damask_job, stress_averaged_per_increment, strain_averaged_per_increment, interpolated_results)
    plot_modulus_degradation(problem_definition, damask_job, stress_averaged_per_increment, strain_averaged_per_increment, interpolated_results)

    post_process_succeeded = True # type: ignore
    return interpolated_results
    