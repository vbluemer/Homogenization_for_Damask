# System packages
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
import os
import typing

# Local packages
from ...common_functions import damask_helper
from ...common_classes.problem_definition import ProblemDefinition
from ...common_classes.damask_job import DamaskJobTypes, DamaskJob
from ...damask_monitor.common_classes_damask_monitor.increment_data import IncrementData
from ..post_processor.interpolate_results import InterpolatedResults


def plot_stress_strain_curves(
        problem_definition: ProblemDefinition,
        damask_job: DamaskJobTypes, 
        stress_per_increment: NDArray[np.float64], 
        strain_per_increment: NDArray[np.float64], 
        interpolated_yield: InterpolatedResults | None = None,
        file_name: str | None = None,
        plot_title: str | None = None):
    
    # print("TODO: Refractor the plot stress_strain_curve function")

    fig = plt.figure(layout='constrained', figsize=(20, 20)) # type: ignore
    subplot = fig.subplots(3,3) # type: ignore

    if file_name is None:
        stress_strain_plot_path = os.path.join(damask_job.runtime.results_folder, 'stress_strain_curve.png')
    else:
        stress_strain_plot_path = os.path.join(damask_job.runtime.results_folder, file_name)

    if plot_title is None:
        plot_title = 'Stress strain curves'
    


    for i in range(3):
        stress_piola_kirchoff_values_x = np.take(stress_per_increment, indices=[i], axis=1)
        strain_green_lagrange_values_x = np.take(strain_per_increment, indices=[i], axis=1)
        for j in range(3):
            stress_piola_kirchoff_values_y = np.take(stress_piola_kirchoff_values_x, indices=[j], axis=2)
            strain_green_lagrange_values_y = np.take(strain_green_lagrange_values_x, indices=[j], axis=2)

            stress_piola_kirchoff_values_y = np.squeeze(stress_piola_kirchoff_values_y)
            strain_green_lagrange_values_y = np.squeeze(strain_green_lagrange_values_y)
            subplot[i][j].plot(strain_green_lagrange_values_y, stress_piola_kirchoff_values_y, '--', marker='x', markersize=8, label='homogonized stress')
            subplot[i][j].legend()

            subplot[i][j].grid()

            subplot[i][j].set_xlabel('strain [-]')
            subplot[i][j].set_ylabel('stress [Pa]')

            if not interpolated_yield == None:
                stress_yield = interpolated_yield.stress[i][j]
                strain_yield = interpolated_yield.strain[i][j]
                subplot[i][j].plot(strain_yield, stress_yield, 'g', marker='o', markersize=8, label="Interpolated result")
                subplot[i][j].legend()

            if True:
                subplot[i][j] = stress_strain_curves_plastic_yield_lines(subplot[i][j], i, j, stress_per_increment, strain_per_increment, problem_definition, damask_job)

    subplot_titles = np.array([
        ["x-x", "x-y", "x-z"], 
        ["y-x", "y-y", "y-z"], 
        ["z-x", "z-y", "z-z"]
        ])
    
    for i in range(3):
        for j in range(3):
            subplot[i][j].set_title(subplot_titles[i][j])

    fig.suptitle(plot_title, fontsize='xx-large') # type: ignore
    
    fig.savefig(stress_strain_plot_path) # type: ignore
    
    plt.close(fig)

def stress_strain_curves_plastic_yield_lines( # type: ignore
        subplot,  # type: ignore
        i: int, j: int, 
        stress_piola_kirchoff_per_increment: NDArray[np.float64], 
        strain_green_lagrange_per_increment: NDArray[np.float64], 
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJobTypes): 
    
    match damask_job:
        case DamaskJob.LoadPath():
            direction_is_loaded = damask_job.loaded_directions[0][i][j]
        case _:
            direction_is_loaded = damask_job.loaded_directions[i][j]

    if not(direction_is_loaded):
        return subplot  # type: ignore

    stress_difference_1st: np.float64 = stress_piola_kirchoff_per_increment[1][i][j] - stress_piola_kirchoff_per_increment[0][i][j]
    strain_difference_1st: np.float64 = strain_green_lagrange_per_increment[1][i][j] - strain_green_lagrange_per_increment[0][i][j]

    slope_stress_strain_1st: np.float64 = stress_difference_1st / strain_difference_1st

    strain_lim_plot: NDArray[np.float64] = subplot.get_xlim() # type: ignore
    strain_max_magnitude: np.float64 = max([strain_lim_plot[0], strain_lim_plot[1]], key=abs) # type: ignore

    sign_slope = 1
    if stress_difference_1st < 0:
        sign_slope = -1

    @typing.no_type_check
    def stress_line(strain, slope) -> float:
        stress = slope * (strain - strain[0])
        return stress
    
    yield_value = problem_definition.yielding_condition.plastic_strain_yield

    strains_plot: NDArray[np.float64] = np.linspace(sign_slope * yield_value, strain_max_magnitude*10, num=2) # type: ignore

    stress_plot = stress_line(strains_plot, slope_stress_strain_1st)

    subplot.plot(strains_plot, stress_plot, 'r--', scalex=False, scaley=False, label='Yielding threshold') # type: ignore
    subplot.legend() # type: ignore

    return subplot # type: ignore


def plot_stress_strain_curves_monitor(problem_definition: ProblemDefinition,
        damask_job: DamaskJobTypes, 
        increment_data: IncrementData, 
        interpolated_yield: InterpolatedResults | None = None,
        file_name: str | None = None,
        plot_title: str | None = None):
    
    stress_per_increment = increment_data.stress_averaged_per_increment
    strain_per_increment = increment_data.strain_averaged_per_increment

    plot_stress_strain_curves(problem_definition, damask_job, stress_per_increment, strain_per_increment, interpolated_yield, file_name=file_name, plot_title=plot_title)


def plot_modulus_degradation(
        problem_definition: ProblemDefinition, 
        damask_job: DamaskJobTypes, 
        stress_per_increment: NDArray[np.float64], 
        strain_per_increment: NDArray[np.float64], 
        interpolated_yield: InterpolatedResults | None = None,
        file_name: str | None = None,
        plot_title: str | None = None):

    if file_name is None:
        modulus_degradation_plot_path = os.path.join(damask_job.runtime.results_folder, 'modulus_degradation.png')
    else:
        modulus_degradation_plot_path = os.path.join(damask_job.runtime.results_folder, file_name)

    if plot_title is None:
        plot_title = 'Modulus degradation'

    elastic_energy_per_increment: list[float] = []
    
    abs_deformation: list[float] = []
    for increment in range(np.shape(stress_per_increment)[0]):
        abs_deformation.append(float(np.linalg.norm(strain_per_increment[increment])))
        elastic_energy = damask_helper.calculate_linear_deformatation_energy(stress_per_increment[increment], strain_per_increment[increment])

        elastic_energy_per_increment.append(float(np.squeeze(elastic_energy)))    


    fig = plt.figure(layout='constrained', figsize=(12.4, 6.2)) # type: ignore
    ax = fig.subplots(1,2) # type: ignore

    ax[0].plot(abs_deformation, elastic_energy_per_increment, '--', marker='x', markersize=8, label='Deformation energy')
    ax[0].title.set_text('Linear deformation energy (E =  k * |strain|^2) -> E')
    ax[0].legend()
    ax[0].set_xlabel("|strain| [-]")
    ax[0].set_ylabel("Deformation energy [Pa]")
    ax[0].grid()

    if np.shape(abs_deformation)[0] > 0:

        modulus_linear = damask_helper.calculate_linear_modulus(stress_per_increment[1], strain_per_increment[1])
        modulus: list[float] = []
        modulus_normalized: list[float] = [1]
        energy_linear: list[float] = [0]
        for i in range(1, len(abs_deformation)):
            modulus_i = damask_helper.calculate_linear_modulus(stress_per_increment[i], strain_per_increment[i])
            modulus.append(modulus_i)
            modulus_normalized.append(modulus_i / modulus_linear)
            strain_vector = damask_helper.strain_tensor_to_vector_notation(strain_per_increment[i])
            energy_linear.append( modulus_linear * float(np.linalg.norm(strain_vector)**2))

        linear_elastic_deformation_condition_plus = np.repeat([1+problem_definition.yielding_condition.modulus_degradation_percentage], len(abs_deformation))
        linear_elastic_deformation_condition_min = np.repeat([1-problem_definition.yielding_condition.modulus_degradation_percentage], len(abs_deformation))

        
        ax[0].plot(abs_deformation, energy_linear, 'r--', label='Linear deformation energy')
        ax[0].legend()

        ax[1].plot(abs_deformation, modulus_normalized, '--', marker='x', markersize=8, label="Normalized deformation stiffness")
        ax[1].plot(abs_deformation, linear_elastic_deformation_condition_plus, '--r', label="Yielding threshold")
        ax[1].plot(abs_deformation, linear_elastic_deformation_condition_min, '--r')
        ax[1].title.set_text('Normalized spring stiffness (E = k * |strain|^2) -> k / k_0')
        ax[1].legend()
        ax[1].set_xlabel("|strain| [-]")
        ax[1].set_ylabel("Normalized linear spring stiffness [-]")
        ax[1].grid()


    if not interpolated_yield == None:
        ax[0].plot(interpolated_yield.strain_norm, interpolated_yield.deformation_energy, marker='o', markersize=8, color="green", label="Interpolated result")
        ax[0].legend()
        
        normalized_deformation_stiffness = interpolated_yield.deformation_modulus / modulus_linear
        ax[1].plot(interpolated_yield.strain_norm, normalized_deformation_stiffness, '', marker='o', markersize=8, color="green", label="Interpolated result")
        ax[1].legend()
    fig.suptitle(plot_title) # type: ignore
    fig.savefig(modulus_degradation_plot_path) # type: ignore

    plt.close(fig)


def plot_modulus_degradation_monitor(problem_definition: ProblemDefinition,
        damask_job: DamaskJobTypes, 
        increment_data: IncrementData, 
        interpolated_yield: InterpolatedResults | None = None,
        file_name: str | None = None,
        plot_title: str | None = None):
    
    stress_per_increment = increment_data.stress_averaged_per_increment
    strain_per_increment = increment_data.strain_averaged_per_increment

    plot_modulus_degradation(problem_definition, damask_job, stress_per_increment, strain_per_increment, interpolated_yield, file_name=file_name, plot_title=plot_title)

