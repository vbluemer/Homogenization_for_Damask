# System packages
import os
import csv 
import pandas as pd
from pandas import DataFrame
import numpy as np
from numpy.typing import NDArray
import scipy # type: ignore
from typing import Literal

# Local packages
from ..common_classes.problem_definition import ProblemDefinition
from ..common_functions.read_results_database_file import read_results_data
from .elastic_tensor.types.isotropic import elastic_tensor_isotropic, initial_guess_isotropic
from .elastic_tensor.types.cubic import elastic_tensor_cubic, initial_guess_cubic
from .elastic_tensor.types.tetragonal import elastic_tensor_tetragonal, initial_guess_tetragonal
from .elastic_tensor.types.orthotropic import elastic_tensor_orthotropic, initial_guess_orthotropic
from .elastic_tensor.types.monoclinic import elastic_tensor_monoclinic, initial_guess_monoclinic
from .elastic_tensor.types.anisotropic import elastic_tensor_anisotropic, initial_guess_anisotropic
from .elastic_tensor.algebraic_fitting import algebraic_fit_components
from ..messages.messages import Messages

def write_dataset(problem_definition: ProblemDefinition) -> ProblemDefinition:
    results_database = read_results_data(problem_definition)

    data_set_stress: list[list[list[float]]] = []
    data_set_strain: list[list[list[float]]] = []
    result_names: list[Literal["strain_xx", "strain_yy", "strain_zz", "strain_xy", "strain_xz", "strain_yz"]] = []
    setting_field_names = ["strain_step"]
    
    for keyname in results_database['elastic_tensor']:
        is_setting_field = keyname in setting_field_names
        if is_setting_field:
            continue

        data_point_stress: list[list[float]] = results_database['elastic_tensor'][keyname]['stress'] # type: ignore
        data_point_strain: list[list[float]] = results_database['elastic_tensor'][keyname]['strain'] # type: ignore

        result_names.append(keyname) # type: ignore
        data_set_stress.append(data_point_stress)
        data_set_strain.append(data_point_strain)

    data_set_dict: list[dict[str, float|str]] = []

    for name, stress, strain in zip(result_names, data_set_stress, data_set_strain):
        data_point_dict: dict[str, float|str] = dict()
        data_point_stress = stress
        data_point_strain = strain
        data_point_dict["field_name"] = name

        data_point_dict['stress_xx'] = data_point_stress[0][0]
        data_point_dict['stress_yy'] = data_point_stress[1][1]
        data_point_dict['stress_zz'] = data_point_stress[2][2]
        data_point_dict['stress_xy'] = data_point_stress[0][1]
        data_point_dict['stress_xz'] = data_point_stress[0][2]
        data_point_dict['stress_yz'] = data_point_stress[1][2]

        data_point_dict['strain_xx'] = data_point_strain[0][0]
        data_point_dict['strain_yy'] = data_point_strain[1][1]
        data_point_dict['strain_zz'] = data_point_strain[2][2]
        data_point_dict['strain_xy'] = 2*data_point_strain[0][1]
        data_point_dict['strain_xz'] = 2*data_point_strain[0][2]
        data_point_dict['strain_yz'] = 2*data_point_strain[1][2]

        data_set_dict.append(data_point_dict)


    field_names = ["field_name", "stress_xx", "stress_yy", "stress_zz", "stress_xy", "stress_xz", "stress_yz",
                              "strain_xx", "strain_yy", "strain_zz", "strain_xy", "strain_xz", "strain_yz"]
    

    elastic_tensor_data_csv = os.path.join(problem_definition.general.path.results_folder, 'elastic_tensor_data.csv')

    problem_definition.general.path.elastic_tensor_data_csv = elastic_tensor_data_csv

    Messages.ElasticTensor.writing_dataset_to(elastic_tensor_data_csv)

    with open(elastic_tensor_data_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data_set_dict)

    return problem_definition

def read_elastic_tensor_data_points(elastic_tensor_data_file: str) -> DataFrame:

    Messages.ElasticTensor.reading_dataset_from(elastic_tensor_data_file)

    df: DataFrame = pd.read_csv(elastic_tensor_data_file) # type: ignore

    all_required_collumns = ['field_name', 'stress_xx', 'stress_yy', 'stress_zz', 'stress_yz', 'stress_xz', 'stress_xy',
                                        'strain_xx', 'strain_yy', 'strain_zz', 'strain_yz', 'strain_xz', 'strain_xy']

    dataset_collumns = list(df.columns)

    missing_fields: list[str] = []

    for required_collumn in all_required_collumns:
        is_in_data_set = required_collumn in dataset_collumns
        if not is_in_data_set:
            missing_fields = missing_fields + [required_collumn]
    
    if len(missing_fields) > 0:
        Messages.ElasticTensor.fields_missing_in_dataset(missing_fields)
        raise ValueError("Required fields are missing from the dataset. See above messages what fields are missing.")

    return df

def fit_elastic_tensor(material_type: str, elastic_tensor_data_pandas: DataFrame) -> tuple[NDArray[np.float64], float]:
    # This function fits the components of the elastic tensor using a optimization scheme. 

    # It returns the elastic tensor (Voigt notation).
    
    MPa_to_Pa = 1E6
    Pa_to_MPA = 1/MPa_to_Pa

    Messages.ElasticTensor.fitting_type_to_dataset(material_type)

    Voigt_notation_stress = ['stress_xx', 'stress_yy', 'stress_zz', 'stress_yz', 'stress_xz', 'stress_xy']
    Voigt_notation_strain = ['strain_xx', 'strain_yy', 'strain_zz', 'strain_yz', 'strain_xz', 'strain_xy']

    # Make sure the data is represented in voihgt notation
    stress_data_pandas = elastic_tensor_data_pandas[Voigt_notation_stress]
    strain_data_pandas = elastic_tensor_data_pandas[Voigt_notation_strain]
    
    stress_data = stress_data_pandas.to_numpy() * Pa_to_MPA # type: ignore
    strain_data = strain_data_pandas.to_numpy() # type: ignore

    number_data_points = np.shape(stress_data)[0]

    # transposing the data from (n x 6) to (6 x n)
    stress_data = np.transpose(stress_data, (1,0))
    strain_data = np.transpose(strain_data, (1,0)) # type: ignore

    # setting up elastic_tensor_function to return the elastic tensor from a set of coefficients
    # initial_guess is used to define the number of independant coefficients in the tensor.
    match material_type:
        case 'isotropic':
            initial_guess = initial_guess_isotropic()
            elastic_tensor_function = elastic_tensor_isotropic
        case 'cubic':
            initial_guess = initial_guess_cubic()
            elastic_tensor_function = elastic_tensor_cubic
        case 'tetragonal':
            initial_guess = initial_guess_tetragonal()
            elastic_tensor_function = elastic_tensor_tetragonal
        case 'orthotropic':
            initial_guess = initial_guess_orthotropic()
            elastic_tensor_function = elastic_tensor_orthotropic
        case 'monoclinic':
            initial_guess = initial_guess_monoclinic()
            elastic_tensor_function = elastic_tensor_monoclinic
        case 'anisotropic':
            initial_guess = initial_guess_anisotropic()
            elastic_tensor_function = elastic_tensor_anisotropic
        case _:
            raise Exception(f"Material type {material_type} not yet implemented for fitting of elastic tensor!")
    

    def objective_function(coefficients: list[float]) -> float:
        elastic_tensor = elastic_tensor_function(coefficients)

        # elastic_tensor = 6 x 6, strain_data = 6 x n. Hence, stress_fitted = 6 x n.
        # Here, each collumn represents a strain step experiment.
        # Doing so, the entire data set is calculated with just one step.
        stress_fitted = np.matmul(elastic_tensor, strain_data) # type: ignore
        stress_difference_squared = ((stress_fitted - stress_data) * MPa_to_Pa)**2
        MSE = np.sum(stress_difference_squared) / (number_data_points * 6)
        return MSE

    result = scipy.optimize.minimize(objective_function, initial_guess, method='BFGS', options={'gtol': 1e-3}) # type: ignore

    # Finally calculate the elastic tensor from the fitted data.
    elastic_tensor: NDArray[np.float64] = elastic_tensor_function(result.x) # type: ignore

    # At the very least the elastic tensor should be positive definite to be valid.
    eigenvalues_tensor = np.linalg.eigvals(elastic_tensor_function(result.x)) # type: ignore
    tensor_is_positive_definite = all(eigenvalues_tensor>0)

    fitted_stress = np.matmul(elastic_tensor_function(result.x), strain_data) # type: ignore
    max_stress = stress_data.max()
    MSE = np.sum(((fitted_stress - stress_data)/max_stress)**2) / (number_data_points * 6)

    Messages.ElasticTensor.fitting_result(result, elastic_tensor, tensor_is_positive_definite, MSE) # type: ignore

    return elastic_tensor, float(MSE)

def write_elastic_tensor_to_file(elastic_tensor: NDArray[np.float64], file_name: str, MSE: float) -> None:
    component_names = [
        ["C_11", "C_12", "C_13", "C_14", "C_15", "C_16"],
        ["C_21", "C_22", "C_23", "C_24", "C_25", "C_26"],
        ["C_31", "C_32", "C_33", "C_34", "C_35", "C_36"],
        ["C_41", "C_42", "C_43", "C_44", "C_45", "C_46"],
        ["C_51", "C_52", "C_53", "C_54", "C_55", "C_56"],
        ["C_61", "C_62", "C_63", "C_64", "C_65", "C_66"],
    ]

    result_dict: list[dict[str, float|str]] = [dict()]

    for i in range(6):
        for j in range(6):
            result_dict[0][component_names[i][j]] = elastic_tensor[i][j]
    
    component_names_flat = [value for row in component_names for value in row]
    component_names_flat =  ["unit_stress", "MSE"] + component_names_flat
    result_dict[0]["unit_stress"] = "MPa"
    result_dict[0]["MSE"] = MSE
    Messages.ElasticTensor.writing_results(file_name)

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=component_names_flat)
        writer.writeheader()
        writer.writerows(result_dict)

def calculate_elastic_tensor_main(problem_definition: ProblemDefinition) -> None:
    # This function redirects to either calculate_elastic_tensor_algebraic or calculate_elastic_tensor_common
    # based on the settings in problem_definition. 

    Messages.ElasticTensor.Banners.start_fitting()

    problem_definition = write_dataset(problem_definition)

    data_set_file = problem_definition.general.path.elastic_tensor_data_csv
    material_type = problem_definition.elastic_tensor.material_type
    output_file_name = os.path.join(problem_definition.general.path.results_folder, 'elastic_tensor.csv')
    problem_definition.general.path.elastic_tensor_csv = output_file_name

    if problem_definition.elastic_tensor.component_fitting == "optimization":
        calculate_elastic_tensor_common(material_type, data_set_file, output_file_name)
    else:
        calculate_elastic_tensor_algebraic(material_type, data_set_file, output_file_name)

def calculate_elastic_tensor_common(material_type: str, data_set_file: str, output_file_name: str) -> NDArray[np.float64]:
    # This function redirects to the optimization based fitting of the elastic_tensor (fit_elastic_tensor)
    data_set = read_elastic_tensor_data_points(data_set_file)
    elastic_tensor, MSE = fit_elastic_tensor(material_type, elastic_tensor_data_pandas=data_set)
    write_elastic_tensor_to_file(elastic_tensor, output_file_name, MSE)

    return elastic_tensor

def calculate_elastic_tensor_algebraic(material_type: str, data_set_file: str, output_file_name: str) -> NDArray[np.float64]:
    # This function redirects to the algebraic fitting of the elastic_tensor (algebraic_fit_components)
    data_set = read_elastic_tensor_data_points(data_set_file)
    elastic_tensor, MSE = algebraic_fit_components(material_type, elastic_tensor_data_pandas=data_set)
    write_elastic_tensor_to_file(elastic_tensor, output_file_name, MSE)

    return elastic_tensor