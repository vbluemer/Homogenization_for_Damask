# System packages
# import numpy as np
# from numpy.typing import NDArray
# import matplotlib.pyplot as plt
import scipy # type: ignore
from pandas import DataFrame
import csv

# Local packages
from ...messages.messages import Messages
from .general_functions import calculate_MSE_stress

class Hill:
    f: float
    g: float
    h: float
    l: float
    m: float
    n: float
    mean_square_error_stress: float

    def __init__(self) -> None:
        pass

    def set_yield_stress_ref(self, yield_stress_ref: float):
        self.yield_stress_ref = yield_stress_ref
        
    def set_coefficients_from_list(self, coefficients_list: list[float]) -> None:
        self.f = coefficients_list[0]
        self.g = coefficients_list[1]
        self.h = coefficients_list[2]
        self.l = coefficients_list[3]
        self.m = coefficients_list[4]
        self.n = coefficients_list[5]
        return
    
    def unit_conversion(self) -> float:
        # The yield point data is in Pascal, this translates the stresses to another unit
        Pa_to_MPa = 1E-6
        return Pa_to_MPa
    
    def unit_name(self) -> str:
        unit_name = "MPa"
        return unit_name

    def number_optimization_coefficients(self) -> int:
        optimization_variables = 6
        return optimization_variables

    def display_name(self) -> str:
        display_name = "Hill"
        return display_name

    def evaluate(self, stress_Voigt: list[float]) -> float:
        f = self.f
        g = self.g
        h = self.h
        l = self.l
        m = self.m
        n = self.n

        s_xx = stress_Voigt[0]
        s_yy = stress_Voigt[1]
        s_zz = stress_Voigt[2]
        s_yz = stress_Voigt[3]
        s_xz = stress_Voigt[4]
        s_xy = stress_Voigt[5]
        
        #unit_conversion = self.unit_conversion()

        #hill_value = -1/(unit_conversion) + f*(s_yy-s_zz)**2 + g*(s_zz-s_xx)**2 + h*(s_xx-s_yy)**2 + 2*l*(s_yz)**2 + 2*m*(s_xz)**2 + 2*n*(s_xy)**2
        hill_value = f*(s_yy-s_zz)**2 + g*(s_zz-s_xx)**2 + h*(s_xx-s_yy)**2 + 2*l*(s_yz)**2 + 2*m*(s_xz)**2 + 2*n*(s_xy)**2 - (self.yield_stress_ref/1e6) **2
        
        return hill_value 

    def penalty_sum(self) -> float:
        f = self.f
        g = self.g
        h = self.h

        # Constraint such that hill fit has right shape ():
        constraint_1 = (f+g) / (g*h+f*g+f*h)
        constraint_2 = (f+h) / (g*h + g*f + f*h)
        penalty_1 = 1000* max(0, -constraint_1)**2
        penalty_2 = 1000* max(0, -constraint_2)**2

        penalty = penalty_1 + penalty_2
        return penalty

    def write_to_file(self, path:str, MSE: float | None = None) -> None:
        
        coefficient_names: list[str] = [
            "F", "G", "H", "L", "M", "N","unit_stress"]

        result_vals: list[float] = [
            self.f, self.g, self.h, self.l, self.m, self.n, self.unit_name()]
        
        if not MSE == None:
            coefficient_names = coefficient_names + ["MSE"]
            result_vals = result_vals + [MSE]

        coefficient_names = [f"{item:>12}" for item in coefficient_names]
        result_vals = [
            f"{item:12.6f}" if isinstance(item, float) else f"{item:>12s}"
            for item in result_vals
            ]

        result_dict: list[dict[str, float|str]] = [dict()]

        for name, value in zip(coefficient_names, result_vals):
            result_dict[0][name] = value


        Messages.YieldSurface.writing_results(self.display_name(), path)
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=coefficient_names)
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
