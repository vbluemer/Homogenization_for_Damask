# System packages
import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame
import copy
import csv

# Local packages
from ...messages.messages import Messages
from .general_functions import calculate_MSE_stress

class CazacuPlunkettBarlat:
    c: NDArray[np.float64]
    k: float
    a: int
    mean_square_error_stress: float

    #def __init__(self, a: int) -> None:
    #    self.a = a
    def __init__(self) -> None:
        pass
        
    def set_yield_stress_ref(self, yield_stress_ref: float):
        self.yield_stress_ref = yield_stress_ref
        
    def set_coefficients_from_list(self, coefficients_list: list[float]) -> None:
        k: float = coefficients_list[0]
        c = np.zeros((6,6))
        c[0][0] = coefficients_list[1]
        c[1][1] = coefficients_list[2]
        c[2][2] = coefficients_list[3]
        c[3][3] = coefficients_list[4]
        c[4][4] = coefficients_list[5]
        c[5][5] = coefficients_list[6]
        c[1][2] = coefficients_list[7]
        c[2][1] = c[1][2]
        c[0][2] = coefficients_list[8]
        c[2][0] = c[0][2]
        c[0][1] = coefficients_list[9]
        c[1][0] = c[0][1]
        
        a: float = coefficients_list[10]

        self.k = k
        self.c = c
        self.a = a

        return

    def display_name(self) -> str:
        # display_name= f"CPB (a = {self.a})"
        display_name= f"CPB"
        return display_name
    
    def unit_conversion(self) -> float:
        # The yield point data is in Pascal, this translates the stresses to another unit
        Pa_to_MPa = 1/1E6
        return Pa_to_MPa
    
    def unit_name(self) -> str:
        unit_name = "MPa"
        return unit_name

    def evaluate(self, stress_Voigt: list[float]) -> float:

        stress: NDArray[np.float64] = np.array(stress_Voigt)

        hydrostatic_pressure = np.sum(stress[0:3])/3

        deviatoric_stress_Voigt = copy.deepcopy(stress)

        for i in range(3):
            deviatoric_stress_Voigt[i] = deviatoric_stress_Voigt[i] - hydrostatic_pressure

        Sigma_Voigt = np.matmul(self.c, deviatoric_stress_Voigt)
        Sigma = np.zeros((3,3))
        for diagonal in range(3):
            Sigma[diagonal][diagonal] = Sigma_Voigt[diagonal]
        Sigma[1][2] = Sigma_Voigt[3]
        Sigma[0][2] = Sigma_Voigt[4]
        Sigma[0][1] = Sigma_Voigt[5]
        Sigma[2][1] = Sigma[1][2]
        Sigma[2][0] = Sigma[0][2]
        Sigma[1][0] = Sigma[0][1]

        principle_stresses = np.linalg.eig(Sigma).eigenvalues
        p1 = principle_stresses[0]
        p2 = principle_stresses[1]
        p3 = principle_stresses[2]

        k = self.k
        a = self.a
        yield_stress_ref = self.yield_stress_ref
        # = self.unit_conversion()

        #cazacu_plunkett_barlat_value: float = -1/(unit_conversion) + (abs(p1) - k*p1)**a + (abs(p2) - k*p2)**a + (abs(p3) - k*p3)**a
        cazacu_plunkett_barlat_value: float = ((abs(p1) - k*p1)**a + (abs(p2) - k*p2)**a + (abs(p3) - k*p3)**a)**(1/a) - (yield_stress_ref/1e6)

        return cazacu_plunkett_barlat_value
    
    def number_optimization_coefficients(self) -> int:
        # number_optimization_coefficients = 10
        number_optimization_coefficients = 11
        return number_optimization_coefficients

    def penalty_sum(self) -> float:
        k = self.k
        penalty = 10000000*((min(-1, k)+1)**2 + (max(1,k)-1)**2)
        return penalty
    
    def write_to_file(self, path: str, MSE: float | None = None) -> None:
        component_names = [
            ["C_11", "C_12", "C_13", "C_14", "C_15", "C_16"],
            ["C_21", "C_22", "C_23", "C_24", "C_25", "C_26"],
            ["C_31", "C_32", "C_33", "C_34", "C_35", "C_36"],
            ["C_41", "C_42", "C_43", "C_44", "C_45", "C_46"],
            ["C_51", "C_52", "C_53", "C_54", "C_55", "C_56"],
            ["C_61", "C_62", "C_63", "C_64", "C_65", "C_66"],
        ]

        component_names_flat = [value for row in component_names for value in row]
        component_names_exponents = ["a", "k"]
        component_names_flat_all = component_names_exponents + component_names_flat

        result_dict: list[dict[str, float|str]] = [dict()]

        for i in range(6):
            for j in range(6):
                result_dict[0][component_names[i][j]] = self.c[i][j]
        
        result_dict[0]["a"] = self.a
        result_dict[0]["k"] = self.k

        component_names_flat_all = component_names_flat_all + ["unit_stress"]
        result_dict[0]["unit_stress"] = self.unit_name()

        if not MSE == None:
            result_dict[0]["MSE"] = MSE
            component_names_flat_all = component_names_flat_all + ["MSE"]
        
        for i, row in enumerate(result_dict):
            formatted_row = {}
            for key, value in row.items():
                formatted_key = f"{key:>12s}"
                if isinstance(value, float):
                    formatted_value = f"{value:12.6f}"
                elif isinstance(value, str):
                    formatted_value = f"{value:>12s}"
                else:
                    formatted_value = str(value).rjust(12)
                formatted_row[formatted_key] = formatted_value
            result_dict[i] = formatted_row
                        
        Messages.YieldSurface.writing_results(self.display_name(), path)
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=result_dict[0].keys())
            writer.writeheader()
            writer.writerows(result_dict)
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

