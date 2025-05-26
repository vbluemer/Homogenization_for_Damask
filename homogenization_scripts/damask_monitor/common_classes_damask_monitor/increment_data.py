# System packages
import numpy as np
from numpy.typing import NDArray

# Local packages 
from ...common_classes.problem_definition import ProblemDefinition, StressTensors, StrainTensors

class IncrementData:
    subsequent_parsing_errors    : int
    increment_last_update       : int
    tracked_increments          : list[int]
    last_file_timestamp         : float
    sleep_time                  : float
    stress_averaged_per_increment        : NDArray[np.float64]
    strain_averaged_per_increment        : NDArray[np.float64]
    plastic_strain_averaged_per_increment: NDArray[np.float64]
    Wp_per_increment            : NDArray[np.float64]
    # gamma_per_increment         : NDArray[np.float64]
    stop_condition_reached      : bool
    run_ended_succesfully       : bool
    stress_tensor_type         : StressTensors
    strain_tensor_type         : StrainTensors

    def __init__(self, problem_definition: ProblemDefinition):
        self.subsequent_parsing_errors = 0
        self.increment_last_update = -1
        self.tracked_increments = []
        self.last_file_timestamp = 0
        self.sleep_time = problem_definition.solver.monitor_update_cycle
        self.stress_averaged_per_increment = np.zeros((1,3,3))
        self.strain_averaged_per_increment = np.zeros((1,3,3))
        self.plastic_strain_averaged_per_increment = np.zeros((1,3,3))
        self.Wp_per_increment  = np.zeros((1))
        #self.gamma_per_increment
        self.stop_condition_reached = False
        self.run_ended_succesfully = True
        self.stress_tensor_type = problem_definition.general.stress_tensor_type
        self.strain_tensor_type = problem_definition.general.strain_tensor_type

    def add_increment_stress_tensor(self, stress_tensor: NDArray[np.float64]) -> None:
        self.stress_averaged_per_increment = np.append(self.stress_averaged_per_increment, [stress_tensor], axis=0)

    def add_increment_strain_tensor(self, strain_tensor: NDArray[np.float64]) -> None:
        self.strain_averaged_per_increment = np.append(self.strain_averaged_per_increment, [strain_tensor], axis=0)
        
    def add_increment_plastic_strain_tensor(self, plastic_strain_tensor: NDArray[np.float64]) -> None:
        self.plastic_strain_averaged_per_increment = np.append(self.plastic_strain_averaged_per_increment, [plastic_strain_tensor], axis=0)

    def add_increment_Wp(self, Wp: NDArray[np.float64]) -> None:
        self.Wp_per_increment = np.append(self.Wp_per_increment, [Wp], axis=0)

    # def add_increment_gamma(self, plastic_strain_tensor: NDArray[np.float64]) -> None:
    #     self.gamma_per_increment = np.append(self.gamma_per_increment, [plastic_strain_tensor], axis=0)
