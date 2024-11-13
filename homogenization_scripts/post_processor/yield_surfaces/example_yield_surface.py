# System packages
from pandas import DataFrame
import numpy as np

# Local packages
from ...messages.messages import Messages
from .general_functions import calculate_MSE_stress

class ExampleYieldSurface():
    mean_square_error_stress: float
    some_constant: float
    coefficient_1: float

    def __init__(self, some_constant: float) -> None:
        self.some_constant = some_constant
        return

    def set_coefficients_from_list(self, coefficients_list: list[float]) -> None:
        self.coefficient_1 = coefficients_list[0]
        return
    
    def number_optimization_coefficients(self) -> int:
        number_of_coefficients = 1
        return number_of_coefficients
    
    def display_name(self) -> str:
        display_name = "Example yield surface"
        return display_name
    
    def unit_conversion(self) -> float:
        # The yield point data is in Pascal, this translates the stresses to another unit
        Pa_to_MPa = 1/1E3
        return Pa_to_MPa
    
    def unit_name(self) -> str:
        unit_name = "kPa"
        return unit_name
    
    def evaluate(self, stress_Voigt: list[float]) -> float:
        
        stress_numpy = np.array(stress_Voigt)

        # Non-physical example: only take stress magnitude into account.
        stress_magnitude: float = float(np.linalg.norm(stress_numpy))

        # Get the constants and coefficients from memory:
        some_constant = self.some_constant
        coefficient_1 = self.coefficient_1
        unit_conversion = self.unit_conversion()

        # Calculate the yield surface value:
        yield_surface_value = -1/unit_conversion - some_constant * coefficient_1 * stress_magnitude**2

        return yield_surface_value
    
    def penalty_sum(self) -> float:
        # Suppose coefficient_1 needs to be larger then 0
        coefficient_1 = self.coefficient_1

        penalty = 10000*min([0, coefficient_1])**2
        return penalty
    
    def write_to_file(self, path:str, MSE: float | None = None) -> None:
        Messages.YieldSurface.writing_results(self.display_name(), path)
        with open(path, "w") as file:
            if MSE == None:
                file.write(f"coefficient_1 = {self.coefficient_1}, unit_stress = {self.unit_name()}")
            else:
                file.write(f"coefficient_1 = {self.coefficient_1}, MSE = {MSE}, unit_stress = {self.unit_name()}")

        return
    
    def get_MSE(self, data_set: DataFrame) -> float:
        # Calculate the mean square error of over/under estimation of yield stresses
        mean_square_error = calculate_MSE_stress(self, data_set) # type: ignore
        return mean_square_error
    
    def set_MSE(self, mean_square_error_stress: float) -> None:
        # Store the mean square error of over/under estimation of yield stresses
        self.mean_square_error_stress = mean_square_error_stress
        return
    
    def get_and_set_MSE(self, data_set: DataFrame) -> float:
        mean_square_error_stress = self.get_MSE(data_set)
        self.set_MSE(mean_square_error_stress)
        return mean_square_error_stress
    