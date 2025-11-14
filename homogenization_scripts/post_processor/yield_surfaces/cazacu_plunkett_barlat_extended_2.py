# System packages
import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame
import copy
import csv

# Local packages
from ...messages.messages import Messages
from .general_functions import calculate_MSE_stress

class CazacuPlunkettBarlatExtendedN:
    c: list[NDArray[np.float64]]
    k: list[float]
    a: int
    n: int
    mean_square_error_stress: float

    def __init__(self, n: int) -> None:
        self.n = n
        #self.a = a

    def set_yield_stress_ref(self, yield_stress_ref: float):
        self.yield_stress_ref = yield_stress_ref
        
    def set_coefficients_from_list(self, coefficients_list: list[float]) -> None:
        c: list[NDArray[np.float64]] = list()
        k: list[float] = list()
        a: list[float] = list()

        N_coeff = 11
        
        for n_i in range(self.n):
            k_i: float = coefficients_list[0 + n_i*N_coeff]
            c_i = np.zeros((6,6))
            c_i[0][0] = coefficients_list[1 + n_i*N_coeff]
            c_i[1][1] = coefficients_list[2 + n_i*N_coeff]
            c_i[2][2] = coefficients_list[3 + n_i*N_coeff]
            c_i[3][3] = coefficients_list[4 + n_i*N_coeff]
            c_i[4][4] = coefficients_list[5 + n_i*N_coeff]
            c_i[5][5] = coefficients_list[6 + n_i*N_coeff]
            c_i[1][2] = coefficients_list[7 + n_i*N_coeff]
            c_i[2][1] = c_i[1][2]
            c_i[0][2] = coefficients_list[8 + n_i*N_coeff]
            c_i[2][0] = c_i[0][2]
            c_i[0][1] = coefficients_list[9 + n_i*N_coeff]
            c_i[1][0] = c_i[0][1]

            a_i: float = coefficients_list[10 + n_i*N_coeff]

            k.append(k_i)
            c.append(c_i)
            a.append(a_i)

        self.k = k
        self.c = c
        self.a = a

        return

    def display_name(self) -> str:
        display_name= f"CPB ex. {self.n}"
        return display_name
    
    def unit_conversion(self) -> float:
        # The yield point data is in Pascal, this factor converts the stresses to another unit (adjust unit_name() as well)
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
        
        #unit_conversion = self.unit_conversion()
        #cazacu_plunkett_barlat_value = -1/(unit_conversion)
        cazacu_plunkett_barlat_value = - (self.yield_stress_ref/1e6)

        for n_i in range(self.n):
            Sigma_Voigt = np.matmul(self.c[n_i], deviatoric_stress_Voigt)
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

            k = self.k[n_i]
            a = self.a[n_i]

            cazacu_plunkett_barlat_value +=  ((abs(p1) - k*p1)**a + (abs(p2) - k*p2)**a + (abs(p3) - k*p3)**a)**(1/a)

        return cazacu_plunkett_barlat_value
    
    def number_optimization_coefficients(self) -> int:
        number_optimization_coefficients = 11 * self.n
        return number_optimization_coefficients

    def penalty_sum(self) -> float:
        penalty = 0
        for k in self.k:
            penalty_k = 1000000*((min(-1, k)+1)**2 + (max(1,k)-1)**2)
            penalty += penalty_k
        return penalty
    
    def write_to_file(self, path: str, MSE: float | None = None) -> None:
        component_names: list[str] = []

        result_dict: list[dict[str, float|str]] = [dict()]
        
        for n_i_0 in range(self.n):
            n_i = n_i_0 + 1
            
            component_names = component_names + [f"k_{n_i}"]
            result_dict[0][f"k_{n_i}"] = self.k[n_i_0]
            
            component_names = component_names + [f"a_{n_i}"]
            result_dict[0][f"a_{n_i}"] = self.a[n_i_0]          
            
            component_names_i = [
                [f"C_{n_i}_11", f"C_{n_i}_12", f"C_{n_i}_13", f"C_{n_i}_14", f"C_{n_i}_15", f"C_{n_i}_16"],
                [f"C_{n_i}_21", f"C_{n_i}_22", f"C_{n_i}_23", f"C_{n_i}_24", f"C_{n_i}_25", f"C_{n_i}_26"],
                [f"C_{n_i}_31", f"C_{n_i}_32", f"C_{n_i}_33", f"C_{n_i}_34", f"C_{n_i}_35", f"C_{n_i}_36"],
                [f"C_{n_i}_41", f"C_{n_i}_42", f"C_{n_i}_43", f"C_{n_i}_44", f"C_{n_i}_45", f"C_{n_i}_46"],
                [f"C_{n_i}_51", f"C_{n_i}_52", f"C_{n_i}_53", f"C_{n_i}_54", f"C_{n_i}_55", f"C_{n_i}_56"],
                [f"C_{n_i}_61", f"C_{n_i}_62", f"C_{n_i}_63", f"C_{n_i}_64", f"C_{n_i}_65", f"C_{n_i}_66"],
            ]

            component_names_i_flat = [value for row in component_names_i for value in row]

            component_names = component_names + component_names_i_flat
            
            for i in range(6):
                for j in range(6):
                    result_dict[0][component_names_i[i][j]] = self.c[n_i_0][i][j]
            

            
            component_names = component_names + ["unit_stress"]
            result_dict[0]["unit_stress"] = self.unit_name()
        
        if not MSE == None:
            result_dict[0]["MSE"] = MSE
            component_names = component_names + ["MSE"]

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
