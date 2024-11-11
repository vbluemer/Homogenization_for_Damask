import textwrap
import numpy as np

class ElasticTensor:

    class Banners:
        def start_fitting():
            print("")
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"                       Fitting elastic tensor components                       ")
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("")

    def writing_dataset_to(self, dataset_path: str) -> None:
        print(f"Writing dataset to .csv file: {dataset_path}")

    def reading_dataset_from(self, dataset_path: str) -> None:
        print(f"Reading dataset from .csv file: {dataset_path}")

    def fields_missing_in_dataset(self, missing_fields: list[str]) -> None:
        print("")
        error_string = "Error! The following fields are missing:"
        for missing_field in missing_fields:
            error_string = error_string + " " + missing_field
        
        print(textwrap.fill(error_string,width=80))
        print("")

    def fitting_type_to_dataset(self, elastic_tensor_name: str) -> None:
        print("")
        print(textwrap.fill(f"Fitting components of the {elastic_tensor_name} elastic tensor to dataset.", width=80))
    
    def fitting_result(self, 
                       scipy_result, # type: ignore
                       elastic_tensor: list[list[float]], 
                       positive_definite: bool, MSE: float) -> None:
        print("")
        if scipy_result.success: # type: ignore
            print("Scipy reports a successful fit")
        else:
            print(textwrap.fill(f"Scipy reports an unsuccessful fit, reason: {scipy_result.message}", width=80)) # type: ignore
            print("If reason is precision loss, fitted result could still be acceptable.")
        print("")
        print("Components of the elastic tensor: ")
        np.set_printoptions(linewidth=1000)
        print(elastic_tensor)
        np.set_printoptions()
        print("")
        print(f"Unit used for stress: MPa")
        print(f"Normalized mean square error of dataset fit: {MSE}")
        print(f"Tensor is positive definite: {positive_definite}")

    def fitting_result_algebraic(self, 
                       elastic_tensor: list[list[float]], 
                       positive_definite: bool, MSE: float) -> None:
        print("")
        print("Components of the elastic tensor: ")
        np.set_printoptions(linewidth=1000)
        print(elastic_tensor)
        np.set_printoptions()
        print("")
        print(f"Unit used for stress: MPa")
        print(f"Normalized mean square error of dataset fit: {MSE}")
        print(f"Tensor is positive definite: {positive_definite}")

    def writing_results(self, path:str) -> None:
        print("")
        print(f"Writing elastic tensor to .csv file: {path}")
        