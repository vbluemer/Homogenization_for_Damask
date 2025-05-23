# System packages
import datetime
from typing import Dict, Any
import numpy as np
from numpy.typing import NDArray
import damask # type: ignore


# Local packages
from  ..common_classes import messages
import homogenization_scripts.common_functions.consolelog as consolelog
from ..common_classes.problem_definition import Tensor, StrainTensors, StressTensors

def strain_tensor_to_vector_notation(tensor: NDArray[np.float64]):
    # Transform the strain tensor to vector Voigt notation.
    tensor = np.squeeze(tensor)
    if not np.shape(tensor) == (3,3):
        raise Exception(f"Can not form strain vector from stress tensor as tensor is not 3x3! Shape is: {np.shape(tensor)}")

    vector = np.empty((6,1))

    vector[0] = tensor[0][0]
    vector[1] = tensor[1][1]
    vector[2] = tensor[2][2]
    vector[3] = 2*tensor[1][2]
    vector[4] = 2*tensor[0][2]
    vector[5] = 2*tensor[0][1]

    return vector

def stress_tensor_to_vector_notation(tensor: NDArray[np.float64]):
    # Transform the stress tensor to vector Voigt notation. 

    tensor = np.squeeze(tensor)
    if not np.shape(tensor) == (3,3):
        raise Exception(f"Can not form stress vector from stress tensor as tensor is not 3x3! Shape is: {np.shape(tensor)}")

    vector = np.empty((6,1))

    vector[0] = tensor[0][0]
    vector[1] = tensor[1][1]
    vector[2] = tensor[2][2]
    vector[3] = tensor[1][2]
    vector[4] = tensor[0][2]
    vector[5] = tensor[0][1]
    

    return vector

get_result_type = dict[str, dict[str, dict[str, dict[str,  dict[str, NDArray[np.float64]]]]]]

def extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(
        damask_get_result: get_result_type, 
        property_name: str,
        per_value_size: tuple[Any]) -> NDArray[np.float64]:
    # The output of damask.get() depends by default on many properties (default option: flatten = True). 
    # This function takes the output when a the default behaviour of Damask.get() is overriden with flatten = False. 
    # The output is the (mechanical) property for each grid point, for each phase, for each iteration.
    # Indexing is: (n_increments, n_gridpoints, per_value_size[1], per_value_size[2])
    #   Example outputs: stress&strain: (n_increments, n_gridpoints, 3, 3), per_value_size = (0, 3, 3)
    #       determinant displacement gradient tensor (det('F')): (n_increments, n_gridpoints), per_value_size = (0)

    all_values = None# type: ignore
    
    for increment in damask_get_result.keys():
        increment_values: NDArray[np.float64] = np.ndarray(per_value_size)

        increment_dict = damask_get_result[increment]['phase']
        for phase in increment_dict.keys():
            phase_values = increment_dict[phase]['mechanical'][property_name]
            increment_values = np.append(increment_values, phase_values, axis=0) # type: ignore

        if all_values is None:# type: ignore
            all_values = [increment_values]# type: ignore
        else:
            all_values: NDArray[np.float64] = np.append(all_values, [increment_values], axis=0)# type: ignore
    
    if all_values is None:# type: ignore
        raise Exception(f"No {property_name} data was gathered. This should be impossible")
    else:
        return all_values


def get_strain(damask_result: damask.Result, tensor_type: StrainTensors, display_prefix: str = "")-> tuple[damask.Result, NDArray[np.float64]]:
    # This function gets the strain values for each grid point for each iteration visible in the damask_result.
    # The output is of size (n_increments_visible, n_gridpoints, 3, 3) always.

    # Definition of strain to use.
    match tensor_type:
        case Tensor.Strain.TrueStrain():
            tensor_damask_name = 'epsilon_V^0(F)'
            display_name = "true strain"
            m = 0
        case Tensor.Strain.GreenLagrange():
            tensor_damask_name = 'epsilon_V^1(F)'
            display_name = "Green Lagrange strain"
            m = 1
        case _: # type: ignore
            raise Exception(f"Strain tensor {tensor_type} not yet implemented")

    # Try to get the strain if it is already present, suppress console to override progress reporting
    consolelog.suppress_console_logging()
    strain_dict: get_result_type | None = damask_result.get(tensor_damask_name, flatten=False)
    consolelog.restore_console_logging()
    
    if strain_dict is None:
        timer = datetime.datetime.now()
        messages.Actions.calculate_field(display_name, prefix=display_prefix) # type: ignore

        consolelog.suppress_console_logging()
        # The strain must be added to the result
        damask_result.add_strain(F='F',m=m)
        strain_dict: get_result_type | None= damask_result.get(tensor_damask_name, flatten=False)

        consolelog.restore_console_logging()

        messages.Status.completed_timer(timer) # type: ignore
         
    if strain_dict is None:
        # Explicit call for strain calculation failed, there must be a problem with the result file.
        raise Exception("Failed to calculate the Green Lagrange strain tensor!")
    else:
        # Format the result into a useable format.
        strain: NDArray[np.float64] = extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(strain_dict, 
                                        tensor_damask_name, 
                                        (0,3,3)) # type: ignore
        return damask_result, strain
    
def get_plastic_strain(damask_result: damask.Result, tensor_type: StrainTensors, display_prefix: str = "")-> tuple[damask.Result, NDArray[np.float64]]:
    # This function gets the strain values for each grid point for each iteration visible in the damask_result.
    # The output is of size (n_increments_visible, n_gridpoints, 3, 3) always.

    # Definition of strain to use.
    match tensor_type:
        case Tensor.Strain.TrueStrain():
            tensor_damask_name = 'epsilon_V^0(F_p)'
            display_name = "true strain"
            m = 0
        case Tensor.Strain.GreenLagrange():
            tensor_damask_name = 'epsilon_V^1(F_p)'
            display_name = "Green Lagrange strain"
            m = 1
        case _: # type: ignore
            raise Exception(f"Strain tensor {tensor_type} not yet implemented")
            
    # Try to get the strain if it is already present, suppress console to override progress reporting
    consolelog.suppress_console_logging()
    strain_dict: get_result_type | None = damask_result.get(tensor_damask_name, flatten=False)
    consolelog.restore_console_logging()
    
    if strain_dict is None:
        timer = datetime.datetime.now()
        messages.Actions.calculate_field(display_name, prefix=display_prefix) # type: ignore

        consolelog.suppress_console_logging()
        # The strain must be added to the result
        damask_result.add_strain(F='F_p',m=m)
        strain_dict: get_result_type | None= damask_result.get(tensor_damask_name, flatten=False)

        consolelog.restore_console_logging()

        messages.Status.completed_timer(timer) # type: ignore
         
    if strain_dict is None:
        # Explicit call for strain calculation failed, there must be a problem with the result file.
        raise Exception("Failed to calculate the Green Lagrange strain tensor!")
    else:
        # Format the result into a useable format.
        strain: NDArray[np.float64] = extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(strain_dict, 
                                        tensor_damask_name, 
                                        (0,3,3)) # type: ignore
        return damask_result, strain

def get_slip_system_xi(damask_result: damask.Result, display_prefix: str = "")-> tuple[damask.Result, NDArray[np.float64]]:
    # This function gets the strain values for each grid point for each iteration visible in the damask_result.
    # The output is of size (n_increments_visible, n_gridpoints, 3, 3) always.

    # Definition of strain to use.
    tensor_damask_name = 'xi_sl'
    display_name = "CRSS"

    # Try to get the strain if it is already present, suppress console to override progress reporting
    consolelog.suppress_console_logging()
    xi_dict: get_result_type | None = damask_result.get(tensor_damask_name, flatten=False)
    consolelog.restore_console_logging()

    xi: NDArray[np.float64] = extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(xi_dict, 
                                    tensor_damask_name, 
                                    (0,18)) # currently hardcoded to hcp
    return damask_result, xi

def get_slip_system_gamma(damask_result: damask.Result, display_prefix: str = "")-> tuple[damask.Result, NDArray[np.float64]]:
    # This function gets the strain values for each grid point for each iteration visible in the damask_result.
    # The output is of size (n_increments_visible, n_gridpoints, 3, 3) always.

    # Definition of strain to use.
    tensor_damask_name = 'gamma_sl'
    display_name = "slip_rate"

    # Try to get the strain if it is already present, suppress console to override progress reporting
    consolelog.suppress_console_logging()
    gamma_dict: get_result_type | None = damask_result.get(tensor_damask_name, flatten=False)
    consolelog.restore_console_logging()

    xi: NDArray[np.float64] = extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(gamma_dict, 
                                    tensor_damask_name, 
                                    (0,18)) # currently hardcoded to hcp
    return damask_result, xi
    
def get_stress(damask_result: damask.Result, tensor_type: StressTensors, display_prefix: str = "") -> tuple[damask.Result, NDArray[np.float64]]:
    # This function gets the stress values for each grid point for each iteration visible in the damask_result.
    # The output is of size (n_increments_visible, n_gridpoints, 3, 3) always.

    # Definition of stress to use.
    match tensor_type:
        case Tensor.Stress.PK1():
            tensor_damask_name = 'P'
            display_name = "First Piola-Kirchoff stress"
        case Tensor.Stress.PK2():
            tensor_damask_name = 'S'
            display_name = "Second Piola-Kirchoff stress"
        case Tensor.Stress.Cauchy():
            tensor_damask_name = 'sigma'
            display_name = "Cauchy stress"
        case _: # type: ignore
            raise Exception(f"Stress tensor {tensor_type} not yet implemented")
        
    # Try to get the stress if it is already present, suppress console to override progress reporting
    consolelog.suppress_console_logging()
    stress_dict: get_result_type | None = damask_result.get(tensor_damask_name, flatten=False)
    consolelog.restore_console_logging()
           
    if stress_dict == None:
        timer = datetime.datetime.now()
        messages.Actions.calculate_field(display_name, prefix=display_prefix) # type: ignore

        consolelog.suppress_console_logging()

        # Let damask calculate the stress tensor for each gridpoint
        match tensor_type:
            case Tensor.Stress.PK1():
                pass
            case Tensor.Stress.PK2():
                damask_result.add_stress_second_Piola_Kirchhoff()
            case Tensor.Stress.Cauchy():
                damask_result.add_stress_Cauchy()
            case _: # type: ignore
                raise Exception(f"Stress tensor {tensor_type} not yet implemented")
        
        stress_dict: get_result_type | None = damask_result.get(tensor_damask_name, flatten=False)

        consolelog.restore_console_logging()
        messages.Status.completed_timer(timer) # type: ignore

    if stress_dict is None:
        # Explicit call for stress calculation failed, there must be a problem with the result file.
        raise Exception(f"Failed to calculate the {display_name}!")
    else:
        # Format the result into a useable format.
        strain: NDArray[np.float64] = extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(stress_dict, 
                                        tensor_damask_name,
                                        (0,3,3)) # type: ignore
        return damask_result, strain
 
def get_determinant(damask_result: damask.Result, field_name: str, display_name: str, display_prefix:str = "") -> tuple[damask.Result, NDArray[np.float64]]:
    # This function calculates the determinant of a property per grid point.
    tensor_damask_name = f"det({field_name})"

    consolelog.suppress_console_logging()
    determinant_dict: None | Dict[str, Any] = damask_result.get(tensor_damask_name, flatten=False)
    consolelog.restore_console_logging()

    if determinant_dict is None:

        timer = datetime.datetime.now()
        messages.Actions.calculate_field(display_name, prefix=display_prefix) # type: ignore

        consolelog.suppress_console_logging()
        damask_result.add_determinant(field_name)

        determinant_dict = damask_result.get(tensor_damask_name, flatten=False)

        consolelog.restore_console_logging()
        messages.Status.completed_timer(timer) # type: ignore

    if determinant_dict is None:
        raise Exception(f"Failed to calculate the {display_name}!")
    else:
        determinant: NDArray[np.float64] = extract_mechanical_property_per_iteration_per_grid_point_from_results_dict(determinant_dict, 
                                            tensor_damask_name,
                                            (0)) # type: ignore
        return damask_result, determinant

def get_averaged_stress_per_increment(damask_results: damask.Result, tensor_type: StressTensors, display_prefix: str = ""):
    (damask_results, stress) = get_stress(damask_results, tensor_type, display_prefix=display_prefix)
    stress_averaged_per_increment = np.empty((0, 3, 3))
    # This function calculates the homogonized stress per increment visible in the damask_result.

    # Shape of output is (n_increments_visible, 3, 3) always

    match tensor_type:
        # In case of the Cauchy stress tensor, use volume-adjusted averaging, otherwise, take numeric averaging.
        case Tensor.Stress.Cauchy():
            display_name = "determinant of deformation gradient tensor"
            field_name = 'F'
            (damask_results, determinant) = get_determinant(damask_results, field_name, display_name, display_prefix=display_prefix)
            determinant = np.array(determinant)
            determinant_reshaped = determinant[:, :, np.newaxis, np.newaxis]
            stress_volume_corrected = determinant_reshaped * stress
            stress_domain_summed = np.sum(stress_volume_corrected, axis=(1))
            determinant_summed = np.sum(determinant, axis=1)
            determinant_summed_reshaped = determinant_summed[:, np.newaxis, np.newaxis]
            stress_averaged_per_increment = stress_domain_summed / determinant_summed_reshaped
        case _:
            for increment in range(np.shape(stress)[0]):
                stress_domain_averaged = np.mean(stress[increment],0)
                stress_averaged_per_increment = np.append(stress_averaged_per_increment, np.array([stress_domain_averaged]), axis=0)

    return (damask_results, stress_averaged_per_increment)

def get_averaged_strain_per_increment(damask_results: damask.Result, tensor_type: StrainTensors, display_prefix:str = "") -> tuple[damask.Result, NDArray[np.float64]]:
    (damask_results, strain) = get_strain(damask_results, tensor_type, display_prefix=display_prefix)
    strain_per_increment = np.empty((0, 3, 3))
    # This function calculates the homogonized strain per increment visible in the damask_result.

    # Shape of output is (n_increments_visible, 3, 3) always
    for increment in range(np.shape(strain)[0]):
        strain_domain_averaged = np.mean(strain[increment],axis=0)
        strain_per_increment = np.append(strain_per_increment, np.array([strain_domain_averaged]), axis=0)

    return (damask_results, strain_per_increment)

def get_averaged_plastic_strain_per_increment(damask_results: damask.Result, tensor_type: StrainTensors, display_prefix:str = "") -> tuple[damask.Result, NDArray[np.float64]]:
    (damask_results, plastic_strain) = get_plastic_strain(damask_results, tensor_type, display_prefix=display_prefix)
    plastic_strain_per_increment = np.empty((0, 3, 3))
    # This function calculates the homogonized strain per increment visible in the damask_result.

    # Shape of output is (n_increments_visible, 3, 3) always
    for increment in range(np.shape(plastic_strain)[0]):
        strain_domain_averaged = np.mean(plastic_strain[increment],axis=0)
        plastic_strain_per_increment = np.append(plastic_strain_per_increment, np.array([strain_domain_averaged]), axis=0)

    return (damask_results, plastic_strain_per_increment)

def calculate_linear_deformatation_energy(stress_tensor: NDArray[np.float64], strain_tensor: NDArray[np.float64]) -> float:
    # This function calculates the deformation energy the material has stored, assuming linear deformation (Hooks law)
    
    # The input is the homogonized stress and strain tensors.

    stress_vector = stress_tensor_to_vector_notation(stress_tensor)
    stress_vector_transposed = np.transpose(stress_vector)
    strain_vector = strain_tensor_to_vector_notation(strain_tensor)

    linear_deforamtion_energy = 0.5 * np.matmul(stress_vector_transposed, strain_vector)

    return linear_deforamtion_energy

def calculate_linear_modulus(stress_tensor: NDArray[np.float64], strain_tensor: NDArray[np.float64]) -> float:
    # This function calculates the modulus of the material. 
    # Here, the modulus is the ratio between the linear deformation energy and the absolute strain 
    
    # The input is the homogonized stress and strain tensors.
    
    deformation_energy: float = calculate_linear_deformatation_energy(stress_tensor, strain_tensor)
    strain_norm = np.linalg.norm( strain_tensor_to_vector_notation(strain_tensor) )
    calculate_linear_modulus = float(deformation_energy / strain_norm**2)
    return calculate_linear_modulus

