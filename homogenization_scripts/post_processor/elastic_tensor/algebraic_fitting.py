# System packages
import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame

# Local packages
from ...messages.messages import Messages
from .types.isotropic import elastic_tensor_isotropic
from .types.cubic import elastic_tensor_cubic
from .types.tetragonal import elastic_tensor_tetragonal
from .types.orthotropic import elastic_tensor_orthotropic
from .types.monoclinic import elastic_tensor_monoclinic
from .types.anisotropic import elastic_tensor_anisotropic

Voigt_notation_stress = ['stress_xx', 'stress_yy', 'stress_zz', 'stress_yz', 'stress_xz', 'stress_xy']
Voigt_notation_strain = ['strain_xx', 'strain_yy', 'strain_zz', 'strain_yz', 'strain_xz', 'strain_xy']
all_values = Voigt_notation_strain + Voigt_notation_stress

MPa_to_Pa = 1E6
Pa_to_MPA = 1/MPa_to_Pa

def fit_components_isotropic(elastic_tensor_data_pandas: DataFrame) -> NDArray[np.float64]:

    strain_xx_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xx", all_values]

    c_11: float = np.squeeze(strain_xx_data["stress_xx"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_12: float = np.squeeze(strain_xx_data["stress_yy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA

    coefficients: list[float] = [c_11, c_12]

    elastic_tensor = elastic_tensor_isotropic(coefficients)

    return elastic_tensor


def fit_components_cubic(elastic_tensor_data_pandas: DataFrame) -> NDArray[np.float64]:

    strain_xx_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xx", all_values]
    strain_xy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xy", all_values]

    c_11: float = np.squeeze(strain_xx_data["stress_xx"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_12: float = np.squeeze(strain_xx_data["stress_yy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_44: float = np.squeeze(strain_xy_data["stress_xy"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA


    coefficients: list[float] = [c_11, c_12, c_44]

    elastic_tensor = elastic_tensor_cubic(coefficients)

    return elastic_tensor

def fit_components_tetragonal(elastic_tensor_data_pandas: DataFrame) -> NDArray[np.float64]:

    strain_xx_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xx", all_values]
    strain_zz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_zz", all_values]
    strain_xz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xz", all_values]
    strain_xy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xy", all_values]

    c_11: float = np.squeeze(strain_xx_data["stress_xx"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_12: float = np.squeeze(strain_xx_data["stress_yy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_13: float = np.squeeze(strain_xx_data["stress_zz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_33: float = np.squeeze(strain_zz_data["stress_zz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_44: float = np.squeeze(strain_xz_data["stress_xz"]) / np.squeeze(strain_xz_data["strain_xz"]) * Pa_to_MPA
    c_66: float = np.squeeze(strain_xy_data["stress_xy"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA


    coefficients: list[float] = [c_11, c_12, c_13, c_33, c_44, c_66]

    elastic_tensor = elastic_tensor_tetragonal(coefficients)

    return elastic_tensor

def fit_components_orthotropic(elastic_tensor_data_pandas: DataFrame) -> NDArray[np.float64]:

    
    strain_xx_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xx", all_values]
    strain_yy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_yy", all_values]
    strain_zz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_zz", all_values]
    strain_xy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xy", all_values]
    strain_xz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xz", all_values]
    strain_yz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_yz", all_values]

    c_11: float = np.squeeze(strain_xx_data["stress_xx"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_12: float = np.squeeze(strain_xx_data["stress_yy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_13: float = np.squeeze(strain_xx_data["stress_zz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_22: float = np.squeeze(strain_yy_data["stress_yy"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_23: float = np.squeeze(strain_yy_data["stress_zz"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_33: float = np.squeeze(strain_zz_data["stress_zz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_44: float = np.squeeze(strain_yz_data["stress_yz"]) / np.squeeze(strain_yz_data["strain_yz"]) * Pa_to_MPA
    c_55: float = np.squeeze(strain_xz_data["stress_xz"]) / np.squeeze(strain_xz_data["strain_xz"]) * Pa_to_MPA
    c_66: float = np.squeeze(strain_xy_data["stress_xy"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA

    coefficients: list[float] = [c_11, c_12, c_13, c_22, c_23, c_33, c_44, c_55, c_66]

    elastic_tensor = elastic_tensor_orthotropic(coefficients)

    return elastic_tensor

def fit_components_monoclinic(elastic_tensor_data_pandas: DataFrame) -> NDArray[np.float64]:

    strain_xx_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xx", all_values]
    strain_yy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_yy", all_values]
    strain_zz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_zz", all_values]
    strain_xy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xy", all_values]
    strain_xz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xz", all_values]
    strain_yz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_yz", all_values]

    c_11: float = np.squeeze(strain_xx_data["stress_xx"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_12: float = np.squeeze(strain_xx_data["stress_yy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_13: float = np.squeeze(strain_xx_data["stress_zz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_15: float = np.squeeze(strain_xx_data["stress_xz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA    
    c_22: float = np.squeeze(strain_yy_data["stress_yy"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_23: float = np.squeeze(strain_yy_data["stress_zz"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_25: float = np.squeeze(strain_yy_data["stress_xz"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_33: float = np.squeeze(strain_zz_data["stress_zz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_35: float = np.squeeze(strain_zz_data["stress_xz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_44: float = np.squeeze(strain_yz_data["stress_yz"]) / np.squeeze(strain_yz_data["strain_yz"]) * Pa_to_MPA
    c_46: float = np.squeeze(strain_xy_data["stress_yz"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA
    c_55: float = np.squeeze(strain_xz_data["stress_xz"]) / np.squeeze(strain_xz_data["strain_xz"]) * Pa_to_MPA
    c_66: float = np.squeeze(strain_xy_data["stress_xy"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA
    
    coefficients: list[float] = [c_11, c_12, c_13, c_15, c_22, c_23, c_25, c_33, c_35, c_44, c_46, c_55, c_66]

    elastic_tensor = elastic_tensor_monoclinic(coefficients)

    return elastic_tensor


def fit_components_anisotropic(elastic_tensor_data_pandas: DataFrame) -> NDArray[np.float64]:

    strain_xx_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xx", all_values]
    strain_yy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_yy", all_values]
    strain_zz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_zz", all_values]
    strain_xy_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xy", all_values]
    strain_xz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_xz", all_values]
    strain_yz_data = elastic_tensor_data_pandas.loc[elastic_tensor_data_pandas['field_name'] == "strain_yz", all_values]

    c_11: float = np.squeeze(strain_xx_data["stress_xx"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_12: float = np.squeeze(strain_xx_data["stress_yy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_13: float = np.squeeze(strain_xx_data["stress_zz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_14: float = np.squeeze(strain_xx_data["stress_yz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_15: float = np.squeeze(strain_xx_data["stress_xz"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_16: float = np.squeeze(strain_xx_data["stress_xy"]) / np.squeeze(strain_xx_data["strain_xx"]) * Pa_to_MPA
    c_22: float = np.squeeze(strain_yy_data["stress_yy"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_23: float = np.squeeze(strain_yy_data["stress_zz"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_24: float = np.squeeze(strain_yy_data["stress_yz"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_25: float = np.squeeze(strain_yy_data["stress_xz"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_26: float = np.squeeze(strain_yy_data["stress_xy"]) / np.squeeze(strain_yy_data["strain_yy"]) * Pa_to_MPA
    c_33: float = np.squeeze(strain_zz_data["stress_zz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_34: float = np.squeeze(strain_zz_data["stress_yz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_35: float = np.squeeze(strain_zz_data["stress_xz"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_36: float = np.squeeze(strain_zz_data["stress_xy"]) / np.squeeze(strain_zz_data["strain_zz"]) * Pa_to_MPA
    c_44: float = np.squeeze(strain_yz_data["stress_yz"]) / np.squeeze(strain_yz_data["strain_yz"]) * Pa_to_MPA
    c_45: float = np.squeeze(strain_xz_data["stress_yz"]) / np.squeeze(strain_xz_data["strain_xz"]) * Pa_to_MPA
    c_46: float = np.squeeze(strain_xy_data["stress_yz"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA
    c_55: float = np.squeeze(strain_xz_data["stress_xz"]) / np.squeeze(strain_xz_data["strain_xz"]) * Pa_to_MPA
    c_56: float = np.squeeze(strain_xy_data["stress_xz"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA
    c_66: float = np.squeeze(strain_xy_data["stress_xy"]) / np.squeeze(strain_xy_data["strain_xy"]) * Pa_to_MPA



    coefficients: list[float] = [c_11, c_12, c_13, c_14, c_15, c_16, c_22, c_23, c_24, c_25, c_26, c_33, c_34, c_35, c_36, 
                                 c_44, c_45, c_46, c_55, c_56, c_66]


    elastic_tensor = elastic_tensor_anisotropic(coefficients)

    return elastic_tensor

def algebraic_fit_components(material_type: str, elastic_tensor_data_pandas: DataFrame) -> tuple[NDArray[np.float64], float]:
    # This function calculates the elastic tensor with algebraic relationships.
    # The dataset must consist of uni-axial strain steps which must be in specific directions.

    # Returns the elastic tensor (Voigt notation)
    Messages.ElasticTensor.fitting_type_to_dataset(material_type)
    match material_type:
        case "isotropic":
            elastic_tensor = fit_components_isotropic(elastic_tensor_data_pandas)
        case "cubic":
            elastic_tensor = fit_components_cubic(elastic_tensor_data_pandas)
        case "tetragonal":
            elastic_tensor = fit_components_tetragonal(elastic_tensor_data_pandas)
        case "orthotropic":
            elastic_tensor = fit_components_orthotropic(elastic_tensor_data_pandas)
        case "monoclinic":
            elastic_tensor = fit_components_monoclinic(elastic_tensor_data_pandas)
        case "anisotropic":
            elastic_tensor = fit_components_anisotropic(elastic_tensor_data_pandas)
        case _:
            raise ValueError(f"Material type {material_type} not yet implemented in algebraic elastic tensor fitting.")
    
    # At the very least the elastic tensor must be positive definite to be valid.
    eigenvalues_tensor = np.linalg.eigvals(elastic_tensor) # type: ignore
    tensor_is_positive_definite = all(eigenvalues_tensor>0)

    # Calculate the MSE of the fit.
    stress_data_pandas = elastic_tensor_data_pandas[Voigt_notation_stress]
    strain_data_pandas = elastic_tensor_data_pandas[Voigt_notation_strain]
    
    stress_data = stress_data_pandas.to_numpy() * Pa_to_MPA # type: ignore
    strain_data = strain_data_pandas.to_numpy() # type: ignore

    stress_data = np.transpose(stress_data, (1,0))
    strain_data = np.transpose(strain_data, (1,0)) # type: ignore

    number_data_points = np.shape(stress_data)[0]

    fitted_stress = np.matmul(elastic_tensor, strain_data) # type: ignore
    max_stress = stress_data.max()
    MSE = np.sum(((fitted_stress - stress_data)/max_stress)**2) / (number_data_points * 6)
    Messages.ElasticTensor.fitting_result_algebraic(elastic_tensor, tensor_is_positive_definite, MSE) # type: ignore

    return elastic_tensor, float(MSE)