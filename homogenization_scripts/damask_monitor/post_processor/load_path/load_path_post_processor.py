# System packages
import damask
from numpy.typing import NDArray
import numpy as np
import os
import shutil
import csv

# Local packages
from ....common_classes.damask_job import DamaskJob
from ....common_classes.problem_definition import ProblemDefinition
from ....common_functions import damask_helper
from ..plots import plot_modulus_degradation, plot_stress_strain_curves
from ..interpolate_results import InterpolatedResults


class LoadCaseResults:
    damask_result: damask.Result
    stress_per_material_point: NDArray[np.float64]
    strain_per_material_point: NDArray[np.float64]
    stress_homogonized: NDArray[np.float64]
    strain_homogonized: NDArray[np.float64]
    interpolated_yield_value: InterpolatedResults | None
    processed_succesfully: bool

    def __init__(self, problem_definition: ProblemDefinition, damask_job: DamaskJob.LoadPath, results_path : str, interpolated_yield_value: InterpolatedResults | None = None):
        post_process_succeeded = True

        damask_results_file = damask_job.runtime.damask_result_file

        try: 
            damask_result: damask.Result = damask.Result(damask_results_file)
        except Exception:
            post_process_succeeded = False
            print("[ERROR] Error occurred during reading the damask .hdf5 file for the load path post processing!")
            self.processed_succesfully = post_process_succeeded
            return

        stress_tensor_type = problem_definition.general.stress_tensor_type
        strain_tensor_type = problem_definition.general.strain_tensor_type

        # Calculate homogonized strain
        damask_result, strain_per_material_point = damask_helper.get_strain(damask_result, strain_tensor_type)
        damask_result, strain_homogonized = damask_helper.get_averaged_strain_per_increment(damask_result, strain_tensor_type)

        # Calculate homogonized stress
        damask_result, stress_per_material_point = damask_helper.get_stress(damask_result, stress_tensor_type)
        damask_result, stress_homogonized = damask_helper.get_averaged_stress_per_increment(damask_result, stress_tensor_type)
        damask_result, Wp_per_increment = damask_helper.get_Wp_per_increment(damask_result)

        # find yield and interpolate.
        #interpolated_results = None
        self.interpolated_yield_value = interpolated_yield_value

        # plot stress-strain curves and modulus curves
        plot_stress_strain_curves(problem_definition, damask_job, stress_homogonized, strain_homogonized, interpolated_yield_value, plot_title="Stress strain curves")
        plot_modulus_degradation(problem_definition, damask_job, stress_homogonized, strain_homogonized, interpolated_yield_value, plot_title="Modulus degradation curves")

        # create Results structure

        # Make sure all the files are in the result folder
            # problem_definition
            # human readable Result thing?
            # pickle with material points included
            # result database
        
        problem_definition_file = problem_definition.general.path.problem_definition_file
        results_folder = problem_definition.general.path.results_folder
        backup_problem_definition_file = os.path.join(results_folder, 'problem_definition.yaml.backup')
        shutil.copyfile(problem_definition_file, backup_problem_definition_file)

        # displacement_gradients_damask_dict = damask_result.get('F', flatten=False)
        # displacement_gradients_damask = damask_helper.extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(displacement_gradients_damask_dict, 'F', (0,3,3))
        # displacement_gradients_damask = np.mean(displacement_gradients_damask, axis=1)
        # displacement_gradients_tracked = damask_job.F_increments

        directions: list[str]= ["xx", "yy", "zz", "yz", "xz", "xy"]
        directions_indices: list[int] = [0, 1, 2, 3, 4, 5]
        increment_list: list[dict[str, float|int]] = list()
        
        buffer = 15
        increment_counter = 0
        for stress, strain, Wp in zip(stress_homogonized, strain_homogonized, Wp_per_increment):
            stress_vector = damask_helper.stress_tensor_to_vector_notation(stress)
            strain_vector = damask_helper.strain_tensor_to_vector_notation(strain)
            increment_data: dict[str, float|int|str] = dict()
            increment_data["increment".rjust(buffer)] = f"{increment_counter:{buffer}d}"
            for direction, index in zip(directions, directions_indices):
                increment_data[f"stress_{direction}[MPa]".rjust(buffer)] = f"{np.squeeze(stress_vector[index]/1e6):{buffer}.2f}"
                increment_data[f"strain_{direction}".rjust(buffer)] = f"{np.squeeze(strain_vector[index]):{buffer}.6f}"
            increment_data[f"Wp[J/m3]".rjust(buffer)] = f"{Wp:{buffer}.4f}"

            increment_list.append(increment_data)
        
            increment_counter += 1

        if interpolated_yield_value:
            stress = interpolated_yield_value.stress
            strain = interpolated_yield_value.strain
            Wp     = interpolated_yield_value.wp 
        
            stress_vector = damask_helper.stress_tensor_to_vector_notation(stress)
            strain_vector = damask_helper.strain_tensor_to_vector_notation(strain)
            increment_data["increment".rjust(buffer)] = f"yieldpoint".rjust(buffer)
            for direction, index in zip(directions, directions_indices):
                increment_data[f"stress_{direction}[MPa]".rjust(buffer)] = f"{np.squeeze(stress_vector[index]/1e6):{buffer}.2f}"
                increment_data[f"strain_{direction}".rjust(buffer)] = f"{np.squeeze(strain_vector[index]):{buffer}.6f}"
            increment_data[f"Wp[J/m3]".rjust(buffer)] = f"{Wp:{buffer}.4f}"
            
        field_names: list[str] = ["increment".rjust(buffer)]
        for direction in directions:
            field_names.append(f"stress_{direction}[MPa]".rjust(buffer))
        for direction in directions:
            field_names.append(f"strain_{direction}".rjust(buffer))
        field_names.append(f"Wp[J/m3]".rjust(buffer))

        with open(results_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(increment_list)
                    
        self.stress_per_material_point = stress_per_material_point
        self.strain_per_material_point = strain_per_material_point

        self.stress_homogonized = stress_homogonized
        self.strain_homogonized = strain_homogonized

        self.damask_result = damask_result

        self.processed_succesfully = post_process_succeeded



def load_path_post_process(problem_definition: ProblemDefinition, damask_job: DamaskJob.LoadPath, interpolated_results: InterpolatedResults | None = None):
    results_folder = problem_definition.general.path.results_folder
    readable_results_file = os.path.join(results_folder, 'load_path_results.csv')
    problem_definition.general.path.load_path_csv = readable_results_file

    load_path_results = LoadCaseResults(problem_definition, damask_job, readable_results_file, interpolated_results)

    post_process_succeeded = load_path_results.processed_succesfully
    return post_process_succeeded