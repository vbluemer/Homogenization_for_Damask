# System packages
import copy
import numpy as np
import re
from math import cos, sin, radians, sqrt

# Local packages
from .problem_definition import ProblemDefinition
from ..damask_monitor.common_classes_damask_monitor.stop_conditions.stop_conditions import StopCondition
from ..damask_monitor.common_classes_damask_monitor.increment_data import IncrementData

class RunTime:
    damask_files                : str
    results_folder              : str
    grid_file                   : str
    material_properties_file    : str
    loadcase_file               : str
    numerics_file               : str
    log_file                    : str
    damask_result_file          : str
    damask_temporary_result_file: str
    damask_restart_file         : str

    def set_damask_files(self, damask_files_folder_job: str) -> None:
        self.damask_files = damask_files_folder_job

    def set_results_path(self, results_folder_job: str) -> None:
        self.results_folder = results_folder_job

    def set_grid_file(self, grid_file: str) -> None:
        self.grid_file = grid_file

    def set_material_properties_file(self, material_properties_file: str) -> None:
        self.material_properties_file = material_properties_file
    
    def set_restart_file(self, restart_file: str) -> None:
        self.restart_file = restart_file
        
    def set_loadcase_file(self, loadcase_file: str) -> None:
        self.loadcase_file = loadcase_file

    def set_numerics_file(self, numerics_file: str) -> None:
        self.numerics_file = numerics_file

    def set_log_file(self, log_file: str) -> None:
        self.log_file = log_file

    def set_damask_result_file(self, damask_result_file: str) -> None:
        self.damask_result_file = damask_result_file

    def set_damask_temporary_result_file(self, damask_temporary_result_file: str) -> None:
        self.damask_temporary_result_file = damask_temporary_result_file
    
    def set_damask_restart_file(self, damask_restart_file: str) -> None:
        self.damask_restart_file = damask_restart_file

    def set_backup_folder(self, backup_folder: str) -> None:
        self.backup_folder = backup_folder

def create_stress_tensor(s_xx: float, s_xy: float, s_xz: float,
                                      s_yy: float, s_yz: float,
                                                   s_zz: float) -> list[list[float | str]]:
    
    stress_tensor: list[list[float | str]] = [
        [s_xx, s_xy, s_xz],
        ['x',  s_yy, s_yz],
        ['x', 'x',   s_zz]
        ]
    
    return stress_tensor

def create_unconstrained_tensor(number_of_tensors: int) -> list[list[list[float | str]]]:
    tensor_set:  list[list[list[float | str]]] = []
    
    for _ in range(number_of_tensors):
        tensor_set.append([
                        ['x', 'x',  'x'], 
                        [ 0,  'x',  'x'], 
                        [ 0,   0,   'x']])
    
    return tensor_set

def define_stop_condition_yielding(problem_definition: ProblemDefinition) -> StopCondition.Yielding:
    yield_condition = problem_definition.yielding_condition.yield_condition
    if yield_condition == 'stress_strain_curve':
        yield_value = problem_definition.yielding_condition.plastic_strain_yield
    elif yield_condition == 'modulus_degradation':
        yield_value = problem_definition.yielding_condition.modulus_degradation_percentage
    elif yield_condition == 'plastic_work':
        yield_value = problem_definition.yielding_condition.plastic_work_threshold
    else:
        raise Exception(f"Yield condition {yield_condition} not yet implemented for creating the stopping condition for jobs!")

    stop_condition = StopCondition.Yielding(problem_definition.yielding_condition.yield_condition, yield_value)

    return stop_condition


class       DamaskJob:
    # Each type of DamaskJob should have the following fields:
    # The following is for python editors to understand the structure of the class
   

    def __init__(self):
        self.runtime = RunTime()
        self.runtime_main = RunTime()

    class ElasticTensor:
        runtime             : RunTime
        runtime_main        : RunTime
        stress_tensor       : list[list[list[float| str]]]
        target_stress       : list[list[list[float| str]]]
        loaded_directions   : list[list[list[bool]]]
        target_stress     : list[list[list[float| str]]]
        deformation_gradient_tensor  : list[list[list[float | str]]]
        N_increments        : int
        stop_condition      : StopCondition.NoConditions 
        simulation_type     : str
        field_name          : str
        load_steps          : int
        reduce_parasitic_stresses: bool
        use_restart_file: bool
        use_restart_number: int
        increment_data: IncrementData
        job_number: int
        total_jobs: int

        def __init__(self, problem_definition: ProblemDefinition, direction: str):
            # This function creates the elastic_tensor DamaskJob type from a direction.
            # This can be a uniaxial direction or combined direction.

            self.runtime = RunTime()
            self.runtime_main = RunTime()

            N_increments = 1
            
            target_stress: list[list[list[float | str]]] = [[
                ['x', 'x', 'x'],
                ['x', 'x', 'x'],
                ['x', 'x', 'x']]]
            
            deformation_gradient_tensor: list[list[list[float| str]]] = [[
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]]]
            
            loaded_directions: list[list[list[bool]]] = [[
                [False, False, False],
                [False, False, False],
                [False, False, False]
            ]]

            strain_step = problem_definition.elastic_tensor.strain_step

            match direction:
                # If the load step is uniaxial, take the full strain step.
                case 'strain_xx':
                    deformation_gradient_tensor[0][0][0] += strain_step # type: ignore
                    loaded_directions[0][0][0] = True
                case 'strain_yy':
                    deformation_gradient_tensor[0][1][1] += strain_step # type: ignore
                    loaded_directions[0][1][1] = True
                case 'strain_zz':
                    deformation_gradient_tensor[0][2][2] += strain_step # type: ignore
                    loaded_directions[0][2][2] = True
                case 'strain_xy':
                    deformation_gradient_tensor[0][0][1] += strain_step # type: ignore
                    deformation_gradient_tensor[0][1][0] += strain_step # type: ignore
                    loaded_directions[0][0][1] = True
                case 'strain_xz':
                    deformation_gradient_tensor[0][0][2] += strain_step # type: ignore
                    deformation_gradient_tensor[0][2][0] += strain_step # type: ignore
                    loaded_directions[0][2][1] = True
                case 'strain_yz':
                    deformation_gradient_tensor[0][1][2] += strain_step # type: ignore
                    deformation_gradient_tensor[0][2][1] += strain_step # type: ignore
                    loaded_directions[0][1][2] = True
                case _:
                    # If the load step is bi-directional, make sure the total magnitude equals the intended strain step
                    if "_xx" in direction:
                        deformation_gradient_tensor[0][0][0] += 1/2*sqrt(2)*strain_step # type: ignore
                        loaded_directions[0][0][0] = True
                    if "_yy" in direction:
                        deformation_gradient_tensor[0][1][1] += 1/2*sqrt(2)*strain_step # type: ignore
                        loaded_directions[0][1][1] = True    
                    if "_zz" in direction:
                        deformation_gradient_tensor[0][2][2] += 1/2*sqrt(2)*strain_step # type: ignore
                        loaded_directions[0][2][2] = True    
                    if "_xy" in direction:
                        deformation_gradient_tensor[0][0][1] += 1/2*sqrt(2)*strain_step # type: ignore
                        deformation_gradient_tensor[0][1][0] += 1/2*sqrt(2)*strain_step # type: ignore
                        loaded_directions[0][0][1] = True    
                    if "_xz" in direction:
                        deformation_gradient_tensor[0][0][2] += 1/2*sqrt(2)*strain_step # type: ignore
                        deformation_gradient_tensor[0][2][0] += 1/2*sqrt(2)*strain_step # type: ignore
                        loaded_directions[0][0][2] = True    
                    if "_yz" in direction:
                        deformation_gradient_tensor[0][1][2] += 1/2*sqrt(2)*strain_step # type: ignore
                        deformation_gradient_tensor[0][2][1] += 1/2*sqrt(2)*strain_step # type: ignore
                        loaded_directions[0][1][2] = True 

            # Setup all the variables that are needed during the simulation.
            self.target_stress = target_stress
            self.loaded_directions = loaded_directions
            self.N_increments = N_increments

            self.stop_condition = StopCondition.NoConditions()

            self.simulation_type = 'elastic_tensor'
            self.field_name = direction
            self.reduce_parasitic_stresses = False
            self.use_restart_number = 0
            self.stress_tensor = copy.deepcopy(target_stress)
            self.deformation_gradient_tensor  : list[list[list[float | str]]] = copy.deepcopy(deformation_gradient_tensor)
            self.use_restart_file = False


    # This class is not used any more, kept here for now just in case.
    # class YieldPoint:
    #     runtime             : RunTime
    #     runtime_main   : RunTime
    #     stress_tensor       : list[list[list[float| str]]]
    #     target_stress       : list[list[list[float| str]]]
    #     load_steps          : int
    #     loaded_directions   : list[list[list[bool]]]
    #     deformation_gradient_tensor  : list[list[list[float | str]]]
    #     target_stress     : list[list[list[float| str]]]
    #     N_increments        : int
    #     stop_condition      : StopCondition.Yielding 
    #     simulation_type     : str
    #     field_name          : str
    #     general_yield_value_modulus_degradation: float
    #     general_yield_value_plastic_strain: float
    #     reduce_parasitic_stresses: bool
    #     use_restart_file: bool
    #     use_restart_number: int
    #     increment_data: IncrementData
    #     job_number: int
    #     total_jobs: int

    #     def __init__(self, problem_definition: ProblemDefinition, direction: str):
    #         self.runtime = RunTime()
    #         self.runtime_main = RunTime()
            
    #         N_increments = problem_definition.solver.N_increments

            
            
    #         target_stress: list[list[list[float | str]]] = []
            
    #         loaded_directions: list[list[list[bool]]] = []

    #         estimation_yield_tensile = problem_definition.yielding_condition.estimated_tensile_yield
    #         estimation_yield_shear = problem_definition.yielding_condition.estimated_shear_yield

    #         load_step_fractions = np.linspace(0, 1, N_increments+1)[1:]

    #         for fraction in load_step_fractions:
                
    #             target_stress_load_step : list[list[str|float]] = [
    #                 [ 0,   0,  0],
    #                 ['x',  0,  0],
    #                 ['x', 'x', 0]
    #             ]

    #             loaded_directions_step: list[list[bool]] = [
    #                 [False, False, False],
    #                 [False, False, False],
    #                 [False, False, False]
    #             ]

    #             match direction:
    #                 case 'x-x':
    #                     target_stress_load_step[0][0] = fraction*estimation_yield_tensile
    #                     loaded_directions_step[0][0] = True
    #                 case 'y-y':
    #                     target_stress_load_step[1][1] = fraction*estimation_yield_tensile
    #                     loaded_directions_step[1][1] = True
    #                 case 'z-z':
    #                     target_stress_load_step[2][2] = fraction*estimation_yield_tensile
    #                     loaded_directions_step[2][2] = True
    #                 case 'x-y':
    #                     target_stress_load_step[0][1] = fraction*estimation_yield_shear
    #                     loaded_directions_step[0][1] = True
    #                 case 'x-z':
    #                     target_stress_load_step[0][2] = fraction*estimation_yield_shear
    #                     loaded_directions_step[2][1] = True
    #                 case 'y-z':
    #                     target_stress_load_step[1][2] = fraction*estimation_yield_shear
    #                     loaded_directions_step[1][2] = True
    #                 case _:
    #                     # The input file Reader should already have dealt with an invalid direction, hence, this path should never be actually used.
    #                     raise Exception(f"Invalid load direction defined: {direction}, This should have been dealth with by the YAML reader...")
                
    #             target_stress.append(copy.deepcopy(target_stress_load_step))
    #             loaded_directions.append(copy.deepcopy(loaded_directions_step))
            
    #         self.target_stress = target_stress
    #         self.loaded_directions = loaded_directions
    #         self.N_increments = problem_definition.solver.N_increments
    #         self.load_steps = self.N_increments

    #         self.stop_condition = define_stop_condition_yielding(problem_definition)

    #         self.simulation_type = 'yield_point'
    #         self.field_name = direction

    #         self.general_yield_value_modulus_degradation = problem_definition.yielding_condition.modulus_degradation_percentage
    #         self.general_yield_value_plastic_strain = problem_definition.yielding_condition.plastic_strain_yield

    #         self.reduce_parasitic_stresses = problem_definition.general.reduce_parasitic_stresses
    #         self.use_restart_number = 0
    #         if not self.reduce_parasitic_stresses:
    #             self.stress_tensor = copy.deepcopy(self.target_stress)
    #             self.deformation_gradient_tensor  : list[list[list[float | str]]] = create_unconstrained_tensor(N_increments)
    #             self.use_restart_file = False
    #         else:
    #             self.stress_tensor = []
    #             self.deformation_gradient_tensor = []
    #             self.use_restart_file = True

    class LoadPath:
        runtime             : RunTime
        runtime_main        : RunTime
        stress_tensor       : list[list[list[float | str]]]
        loaded_directions   : list[list[list[bool]]]
        target_stress       : list[list[list[float| str]]]
        deformation_gradient_tensor  : list[list[list[float | str]]]
        N_increments        : int
        stop_condition      : StopCondition.Yielding | StopCondition.NoConditions
        simulation_type     : str
        field_name          : str
        general_yield_value_modulus_degradation: float
        general_yield_value_plastic_strain: float
        general_yield_value_plastic_work: float
        load_steps: int
        reduce_parasitic_stresses: bool
        use_restart_file: bool
        use_restart_number: int
        increment_data: IncrementData
        job_number: int
        total_jobs: int

        def __init__(self, problem_definition: ProblemDefinition):
            # This function makes the load_path DamaskJob directly from the problem_definition

            # Create an object to store the runtime variables.
            self.runtime = RunTime()
            self.runtime_main = RunTime()

            load_path_settings = problem_definition.load_path

            target_stress: list[list[list[float | str]]] = list()
            target_F:      list[list[list[float | str]]] = list()
            loaded_directions: list[list[list[bool]]] = list()
            
            if hasattr(load_path_settings,'stress_x_x'):   
                number_states: int = len(load_path_settings.stress_x_x)
                N_increments = problem_definition.solver.N_increments
    
                self.load_steps = number_states * N_increments
                self.prescribed_stress = True
                target_F = create_unconstrained_tensor(number_states*N_increments)
    
                # Instead of letting Damask create in the in-between stress states, create the
                # stress states in advance. (used for iterative mode)
                for stress_state_number in range(number_states):
    
                    if stress_state_number == 0:
                        d_s_xx = load_path_settings.stress_x_x[stress_state_number]
                        d_s_xy = load_path_settings.stress_x_y[stress_state_number]
                        d_s_xz = load_path_settings.stress_x_z[stress_state_number]
                        d_s_yy = load_path_settings.stress_y_y[stress_state_number]
                        d_s_yz = load_path_settings.stress_y_z[stress_state_number]
                        d_s_zz = load_path_settings.stress_z_z[stress_state_number]
                    else:
                        d_s_xx = load_path_settings.stress_x_x[stress_state_number] - load_path_settings.stress_x_x[stress_state_number-1]
                        d_s_xy = load_path_settings.stress_x_y[stress_state_number] - load_path_settings.stress_x_y[stress_state_number-1]
                        d_s_xz = load_path_settings.stress_x_z[stress_state_number] - load_path_settings.stress_x_z[stress_state_number-1] 
                        d_s_yy = load_path_settings.stress_y_y[stress_state_number] - load_path_settings.stress_y_y[stress_state_number-1]
                        d_s_yz = load_path_settings.stress_y_z[stress_state_number] - load_path_settings.stress_y_z[stress_state_number-1]
                        d_s_zz = load_path_settings.stress_z_z[stress_state_number] - load_path_settings.stress_z_z[stress_state_number-1]
                    
    
                    load_step_fractions = np.linspace(0, 1, N_increments+1)[1:]
    
                    for fraction in load_step_fractions:
                        s_xx = load_path_settings.stress_x_x[stress_state_number] - d_s_xx *(1-fraction)
                        s_xy = load_path_settings.stress_x_y[stress_state_number] - d_s_xy *(1-fraction)
                        s_xz = load_path_settings.stress_x_z[stress_state_number] - d_s_xz *(1-fraction)
                        s_yy = load_path_settings.stress_y_y[stress_state_number] - d_s_yy *(1-fraction)
                        s_yz = load_path_settings.stress_y_z[stress_state_number] - d_s_yz *(1-fraction)
                        s_zz = load_path_settings.stress_z_z[stress_state_number] - d_s_zz *(1-fraction)
    
                        target_stress_increment: list[list[float | str]] = create_stress_tensor(s_xx, s_xy, s_xz,
                                                                                                        s_yy, s_yz,
                                                                                                            s_zz)
                        target_stress.append(copy.deepcopy(target_stress_increment))
                        loaded_directions_step: list[list[bool]] = [
                            [False, False, False],
                            [False, False, False],
                            [False, False, False]
                        ]
    
                        for i in range(3):
                            for j in range(3):
                                if isinstance(target_stress_increment[i][j], (int, float)):
                                    numerical_value: float = float(target_stress_increment[i][j])
                                    if abs(numerical_value) > 0:
                                        loaded_directions_step[i][j] = True
                    
                        loaded_directions.append(copy.deepcopy(loaded_directions_step))

                        
            elif(hasattr(load_path_settings,'F_x_x')):

    
                number_states: int = len(load_path_settings.F_x_x)
                N_increments = problem_definition.solver.N_increments
    
                self.load_steps = number_states * N_increments
                self.prescribed_stress = False

                target_stress = create_unconstrained_tensor(number_states*N_increments)

                # Instead of letting Damask create in the in-between F states, create the
                # F states in advance. (used for iterative mode)
                for F_state_number in range(number_states):
    
                    if F_state_number == 0:
                        d_F_xx = load_path_settings.F_x_x[F_state_number] -1 
                        d_F_xy = load_path_settings.F_x_y[F_state_number]
                        d_F_xz = load_path_settings.F_x_z[F_state_number]
                        d_F_yy = load_path_settings.F_y_y[F_state_number] -1 
                        d_F_yz = load_path_settings.F_y_z[F_state_number]
                        d_F_zz = load_path_settings.F_z_z[F_state_number] -1
                    else:
                        d_F_xx = load_path_settings.F_x_x[F_state_number] - load_path_settings.F_x_x[F_state_number-1]
                        d_F_xy = load_path_settings.F_x_y[F_state_number] - load_path_settings.F_x_y[F_state_number-1]
                        d_F_xz = load_path_settings.F_x_z[F_state_number] - load_path_settings.F_x_z[F_state_number-1] 
                        d_F_yy = load_path_settings.F_y_y[F_state_number] - load_path_settings.F_y_y[F_state_number-1]
                        d_F_yz = load_path_settings.F_y_z[F_state_number] - load_path_settings.F_y_z[F_state_number-1]
                        d_F_zz = load_path_settings.F_z_z[F_state_number] - load_path_settings.F_z_z[F_state_number-1]
                    
    
                    load_step_fractions = np.linspace(0, 1, N_increments+1)[1:]
    
                    for fraction in load_step_fractions:
                        F_xx = load_path_settings.F_x_x[F_state_number] - d_F_xx *(1-fraction)
                        F_xy = load_path_settings.F_x_y[F_state_number] - d_F_xy *(1-fraction)
                        F_xz = load_path_settings.F_x_z[F_state_number] - d_F_xz *(1-fraction)
                        F_yy = load_path_settings.F_y_y[F_state_number] - d_F_yy *(1-fraction)
                        F_yz = load_path_settings.F_y_z[F_state_number] - d_F_yz *(1-fraction)
                        F_zz = load_path_settings.F_z_z[F_state_number] - d_F_zz *(1-fraction)
    
                        target_F_increment: list[list[float | str]] = create_stress_tensor(F_xx, F_xy, F_xz,
                                                                                                 F_yy, F_yz,
                                                                                                       F_zz)
                        target_F.append(copy.deepcopy(target_F_increment))
                        loaded_directions_step: list[list[bool]] = [
                            [False, False, False],
                            [False, False, False],
                            [False, False, False]
                        ]
    
                        for i in range(3):
                            for j in range(3):
                                if isinstance(target_F_increment[i][j], (int, float)):
                                    numerical_value: float = float(target_F_increment[i][j])
                                    if abs(numerical_value) > 0:
                                        loaded_directions_step[i][j] = True
                    
                        loaded_directions.append(copy.deepcopy(loaded_directions_step))
                        
            breakpoint()
            self.target_stress = target_stress
            self.target_F      = target_F
            
            self.stress_tensor = copy.deepcopy(self.target_stress)
            #self.deformation_gradient_tensor = create_unconstrained_tensor(number_states*N_increments)
            self.deformation_gradient_tensor = copy.deepcopy(self.target_F)
            
            self.loaded_directions = loaded_directions
            self.N_increments = problem_definition.solver.N_increments

            # Define if yielding detection will be used.
            match load_path_settings.enable_yield_detection:
                case True:
                    self.stop_condition = define_stop_condition_yielding(problem_definition)
                case False:
                    self.stop_condition = StopCondition.NoConditions()

            # Setup all the variables that are used during the simulation
            self.simulation_type = problem_definition.general.simulation_type
            self.field_name = 'load_path'
            self.general_yield_value_modulus_degradation = problem_definition.yielding_condition.modulus_degradation_percentage
            self.general_yield_value_plastic_strain = problem_definition.yielding_condition.plastic_strain_yield
            self.general_yield_value_plastic_work = problem_definition.yielding_condition.plastic_work_threshold
            self.reduce_parasitic_stresses = problem_definition.general.reduce_parasitic_stresses
            self.use_restart_number = 0
            self.use_restart_file = False

            #if not self.reduce_parasitic_stresses:
            # else:
            #     self.stress_tensor = []
            #     self.deformation_gradient_tensor = []
            #     self.use_restart_file = True
            breakpoint()


    class YieldPointMultiaxial:
        runtime             : RunTime
        runtime_main        : RunTime
        stress_tensor       : list[list[list[float| str]]]
        target_stress       : list[list[list[float| str]]]
        loaded_directions   : list[list[list[bool]]]
        deformation_gradient_tensor  : list[list[list[float | str]]]
        target_stress     : list[list[list[float| str]]]
        load_steps          : int
        N_increments        : int
        stop_condition      : StopCondition.Yielding 
        simulation_type     : str
        field_name          : str
        general_yield_value_modulus_degradation: float
        general_yield_value_plastic_work: float
        general_yield_value_plastic_strain: float
        reduce_parasitic_stresses: bool
        use_restart_file: bool
        increment_data: IncrementData
        job_number: int
        total_jobs: int
        angle_in_plane: float

        def __init__(self, problem_definition: ProblemDefinition, target_stress_input: list[list[float | str]], field_name: str):
            # From the settings recieved, complete the DamaskJob
            
            # Initiate objects to keep values used during running the job.
            self.runtime = RunTime()
            self.runtime_main = RunTime()

            N_increments = problem_definition.solver.N_increments
            self.N_increments = N_increments

            # Define the load steps in between the initial and final loadcase
            load_step_fractions = np.linspace(0, 1, N_increments+1)[1:]

            target_stess: list[list[list[float | str]]] = []

            loaded_directions_increment = [
                [False, False, False],
                [False, False, False],
                [False, False, False]
            ]

            loaded_directions: list[list[list[bool]]] = []

            for i in range(3):
                for j in range(3):
                    if isinstance(target_stress_input[i][j],(float, int)):
                        loaded_directions_increment[i][j] = abs(target_stress_input[i][j]) > 0 # type: ignore
                    
            for fraction in load_step_fractions:
                target_stess_increment: list[list[float | str]] = [
                    [ 0,   0,  0],
                    ['x',  0,  0],
                    ['x', 'x', 0]
                ]
                for i in range(3):
                    for j in range(3):
                        if isinstance(target_stress_input[i][j],(float, int)):
                            target_stess_increment[i][j] = fraction*target_stress_input[i][j]

                target_stess.append(copy.deepcopy(target_stess_increment))
                loaded_directions.append(copy.deepcopy(loaded_directions_increment))


            self.target_stress = target_stess
            self.loaded_directions = loaded_directions

            # setup what yielding definition to use.
            match problem_definition.yielding_condition.yield_condition:
                case 'modulus_degradation':
                    yield_value = problem_definition.yielding_condition.modulus_degradation_percentage
                    stop_condition = StopCondition.Yielding('modulus_degradation', yield_value)
                case 'stress_strain_curve':
                    yield_value = problem_definition.yielding_condition.plastic_strain_yield #???
                    stop_condition = StopCondition.Yielding('stress_strain_curve', yield_value)
                case 'plastic_work':
                    yield_value = problem_definition.yielding_condition.plastic_work_threshold
                    stop_condition = StopCondition.Yielding('plastic_work', yield_value)
                    # raise Exception("The stress-strain curve plastic deformation condition is not useable in yield_surface simulation types")
                case _: # type: ignore
                    raise Exception(f"The yield condition {problem_definition.yielding_condition.yield_condition} is not yet implememted for yield_surface simulation job creations")

            # setup other variables
            self.stop_condition = stop_condition
            self.simulation_type = problem_definition.general.simulation_type
            self.field_name = field_name
            self.load_steps = N_increments
            self.general_yield_value_modulus_degradation = problem_definition.yielding_condition.modulus_degradation_percentage
            self.general_yield_value_plastic_work = problem_definition.yielding_condition.plastic_work_threshold
            self.general_yield_value_plastic_strain = problem_definition.yielding_condition.plastic_strain_yield
            self.reduce_parasitic_stresses = problem_definition.general.reduce_parasitic_stresses
            self.use_restart_number = 0
            if not self.reduce_parasitic_stresses: 
                # For non-iterative approach the input stress (PK1) is the same as the target stress (PK1)
                self.stress_tensor = copy.deepcopy(self.target_stress)
                self.deformation_gradient_tensor = create_unconstrained_tensor(N_increments)
                self.use_restart_file = False
            else:
                # For an iterative approach the input stress (PK1) is different form target (Cauchy/PK2).
                self.stress_tensor = []
                self.deformation_gradient_tensor = []
                self.use_restart_file = True
                
def create_uniaxial_yield_point(problem_definition: ProblemDefinition, plane: str) -> DamaskJob.YieldPointMultiaxial:
    # This function sets up the simple uni-axial yield point test.
    
    target_stress: list[list[float | str]] = [
        [0, 0, 0],
        ['x', 0, 0],
        ['x', 'x', 0]]
    
    estimated_tensile_yield = problem_definition.yielding_condition.estimated_tensile_yield
    estimated_shear_yield = problem_definition.yielding_condition.estimated_shear_yield

    match plane:
        case "x-x":
            target_stress[0][0] = estimated_tensile_yield
        case "y-y":
            target_stress[1][1] = estimated_tensile_yield
        case "z-z":
            target_stress[2][2] = estimated_tensile_yield
        case "x-y":
            target_stress[0][1] = estimated_shear_yield
        case "x-z":
            target_stress[0][2] = estimated_shear_yield
        case "y-z":
            target_stress[1][2] = estimated_shear_yield
        case _:
            raise ValueError(f"Uniaxial loading direction {plane} not recognized. This should be impossible.")

    job = DamaskJob.YieldPointMultiaxial(problem_definition, target_stress, plane)

    return job

def create_multiaxial_yield_points_set_names(problem_definition: ProblemDefinition, plane: str) -> list[str]:
    # This function defines the names of the simulations needed for the yield_surface simulation type
    # if an automatic stress_state_generation is automatic
    
    field_names: list[str] = []
    
    points_per_quadrant  = problem_definition.yield_surface.load_points_per_quadrant
    compressive_symmetry = problem_definition.yield_surface.assume_tensile_compressive_symmetry
    
    if compressive_symmetry:
        number_of_quadrants = 2
        # redundant_xz = [0*points_per_quadrant]
        # redundant_yz = [0*points_per_quadrant,1*points_per_quadrant]
    else:
        number_of_quadrants = 4
        # redundant_xz = [0*points_per_quadrant,2*points_per_quadrant]
        # redundant_yz = [0*points_per_quadrant,1*points_per_quadrant,2*points_per_quadrant,3*points_per_quadrant]
    
    for quadrant_number in range(number_of_quadrants):
        for point_number in range(points_per_quadrant):
            #if plane == 'x_z' and quadrant_number in [0,2] and point_number==0:
            if plane == 'x_z' and quadrant_number in [1,3] and point_number==0:
                continue
            if plane == 'y_z' and quadrant_number in [0,1,2,3] and point_number==0:
                continue
            field_name_tension = f"tensile_{plane}_q{quadrant_number}_{point_number}"
            field_names.append(field_name_tension)

    for quadrant_number in range(number_of_quadrants):
        for point_number in range(points_per_quadrant):
            match plane:
                case 'x_y':
                    shear_name = "xy_xz"
                case 'x_z':
                    #if quadrant_number in [0,2] and point_number==0:
                    if quadrant_number in [1,3] and point_number==0:
                        continue
                    shear_name = "xy_yz"
                case 'y_z':
                    if quadrant_number in [0,1,2,3] and point_number==0:
                        continue
                    shear_name = "xz_yz"
                case _:
                    raise Exception(f"Plane {plane} not yet implemented for multiaxial yield point job creation.")
                
            field_name_shear = f"shear_{shear_name}_q{quadrant_number}_{point_number}"
            field_names.append(field_name_shear)
    return field_names

def create_multiaxial_yield_point_manual_values(problem_definition: ProblemDefinition, job_name: str, required_results: list[str]) -> list[DamaskJob.YieldPointMultiaxial]:
    # This function reads the name of a manual stress state for the yield_surface simulation type and 
    # makes a DamaskJob with the intented stress values.

    # Read stresses from jobname
    job_name_split = job_name.split("_")

    target_stress: list[list[float | str]] = [
        [0, 0, 0],
        ['x', 0, 0],
        ['x', 'x', 0]]

    for component in job_name_split:
        if component == "stress":
            continue

        component_split = component.split("=")
        direction = component_split[0]
        value = float(component_split[1].replace("-", "."))

        match direction:
            case "xx":
                target_stress[0][0] = value
            case "yy":
                target_stress[1][1] = value
            case "zz":
                target_stress[2][2] = value
            case "xy":
                target_stress[0][1] = value
            case "xz": 
                target_stress[0][2] = value
            case "yz":
                target_stress[1][2] = value
            case _:
                raise ValueError(f"Creating job from required job name failed, unrecognized load direction: {direction}")

    job_list: list[DamaskJob.YieldPointMultiaxial] = []
    job = DamaskJob.YieldPointMultiaxial(problem_definition, target_stress, field_name=job_name)
    job_list.append(job)

    return job_list


def create_multiaxial_yield_point_for_yield_locus(problem_definition: ProblemDefinition, job_name: str, required_results: list[str]) -> list[DamaskJob.YieldPointMultiaxial]:
    # This function creates the DamaskJobs needed for the yield_surface simulation type where
    # automatic stress state generation is used. 
    # First, the number of stress states in a plane (i.e. xx-yy) is devided over 
    # the quadrants (i.e.positive xx and yy, positive xx and negative yy, etc). Then, the 
    # job is given a certain position within the quadrant.
    job_is_required = job_name in required_results
    if not job_is_required:
        return []

    # If manual stress_state_creation is used, refer to that function
    if problem_definition.yield_surface.stress_state_creation == "manual":
        job_list = create_multiaxial_yield_point_manual_values(problem_definition, job_name, required_results)
        return job_list

    # compressive_symmetry = problem_definition.yield_surface.assume_tensile_compressive_symmetry
    # points_per_plane = problem_definition.yield_surface.load_points_per_quadrant

    # first_points_ordering: list[int]

    # # The ordering of the first few stress states have a defined order to prevent 
    # # redundant stress states.
    # if compressive_symmetry:
    #     if problem_definition.general.dimensions == '3D':
    #         first_points_ordering = [1,1,2,2]
    #     else:
    #         first_points_ordering = []
    # else:
    #     if problem_definition.general.dimensions == '3D':
    #         first_points_ordering = [1, 3, 1, 3, 2, 4, 2, 4]
    #     else:
    #         first_points_ordering = []
    # first_points_length = len(first_points_ordering)

    # # Define if half the plane or the entire plane must be used.
    # if compressive_symmetry:
    #     number_of_points_is_even = points_per_plane % 2 == 0
    #     number_of_points_is_two = points_per_plane == 2
    #     if number_of_points_is_two:
    #         points_per_quadrant = [2,0,0,0]
    #     elif number_of_points_is_even:
    #         points_per_quadrant: list[int] = [int(points_per_plane/2),int(points_per_plane/2),0,0]
    #     else:
    #         points_per_quadrant: list[int] = [int((points_per_plane-1)/2+1),int((points_per_plane-1)/2),0,0]
    # else:
    #     number_of_points_is_even = points_per_plane % 2 == 0
    #     points_per_plane = np.max([points_per_plane,4])
    #     if number_of_points_is_even:
    #         points_per_quadrant: list[int] = [int(points_per_plane/4),int(points_per_plane/4),int(points_per_plane/4),int(points_per_plane/4)]
    #     else:
    #         points_per_quadrant: list[int] = [int((points_per_plane-1)/4+1),int((points_per_plane-1)/4),int((points_per_plane-1)/4),int((points_per_plane-1)/4)]
    #     # if points_per_plane < first_points_length:
    #     #     points_per_quadrant = [0, 0, 0, 0]
    #     #     for point in range(points_per_plane):
    #     #         point_index = first_points_ordering[point]
    #     #         points_per_quadrant[point_index] += 1
    #     # else:
    #     #     points_per_quadrant_first = [0, 0, 0, 0]
    #     #     for point in range(first_points_length):
    #     #         point_index = first_points_ordering[point]
    #     #         points_per_quadrant_first[point_index] += 1

    #     #     full_sets_of_points = int((points_per_plane-first_points_length - (points_per_plane-first_points_length) % 4)/4)

    #     #     points_per_quadrant: list[int] = [
    #     #         full_sets_of_points+points_per_quadrant_first[0],
    #     #         full_sets_of_points+points_per_quadrant_first[1],
    #     #         full_sets_of_points+points_per_quadrant_first[2],
    #     #         full_sets_of_points+points_per_quadrant_first[3],
    #     #     ]
    #     #     for remaining_points in range((points_per_plane-first_points_length) % 4):
    #     #         points_per_quadrant[remaining_points] += 1

    # points_already_in_quadrant = [0,0,0,0]
    
    # # Further logic to prevent redundant stress states
    # problem_definition.yield_surface.assume_tensile_compressive_symmetry
    # if problem_definition.general.dimensions == '3D':
    #     quadrant_use_0_axis = [True, False, True, False]
    # else:
    #     quadrant_use_0_axis = [True, True, True, True]

    # # Function that tracks the already existing stress states and what angle the next
    # # stress state should be placed within the plane.
    # def get_load_angle_in_plane(point_number: int) -> float:
    #     if point_number < first_points_length:
    #         quadrant = first_points_ordering[point_number]
    #     else:
    #         if compressive_symmetry:
    #             match point_number % 2: # type: ignore
    #                 case 0:
    #                     quadrant = 1
    #                 case 1:
    #                     quadrant = 2
    #                 case _:
    #                     raise Exception("Logical error! Remainder after division by 2 larger then 2!")
    #         else:
    #             match (point_number-first_points_length) % 4: # type: ignore
    #                 case 0:
    #                     quadrant = 1
    #                 case 1:
    #                     quadrant = 2     
    #                 case 2:
    #                     quadrant = 3
    #                 case 3:
    #                     quadrant = 4
    #                 case _:
    #                     raise Exception("Logical error! Remainder after division by 4 larger then 4!")
        
    #     already_in_quadrant = points_already_in_quadrant[quadrant-1]
    #     points_this_quadrant = points_per_quadrant[quadrant-1]
    #     use_0_axis = quadrant_use_0_axis[quadrant-1]

    #     if use_0_axis:
    #         arc_per_point = 90 / points_this_quadrant
    #         angle = arc_per_point * already_in_quadrant
    #     else:
    #         arc_per_point = 90 / (points_this_quadrant +1)
    #         angle = arc_per_point * (already_in_quadrant+1)
        
    #     angle_in_plane = angle + 90*(quadrant-1)

    #     points_already_in_quadrant[quadrant-1] += 1
    #     return angle_in_plane

    job_is_tensile = 'tensile' in job_name
    if job_is_tensile:
        esitmated_yield = problem_definition.yielding_condition.estimated_tensile_yield
        type_name = "tensile"
    else:
        esitmated_yield = problem_definition.yielding_condition.estimated_shear_yield
        type_name = "shear"

    # In combined load cases, the total magnitude of the yield stress can be higher then in 
    # a uniaxial load case. Compensate by increasing the maximum applied stress when 
    # both stresses are positive or negative.
    def amplification_factor(angle: float) -> float:
        amplification_factor = 1 + max([0, 0.25*sin(radians(angle*2))])
        return amplification_factor
    
    # Set the plane of the job
    is_in_x_y_plane = 'tensile_x_y' in job_name or 'xy_xz' in job_name
    is_in_x_z_plane = 'tensile_x_z' in job_name or 'xy_yz' in job_name
    is_in_y_z_plane = 'tensile_y_z' in job_name or 'xz_yz' in job_name

    if is_in_x_y_plane:
        if job_is_tensile:
            index_1 = [0,0]
            index_2 = [1,1]
            load_name = "x_y"
        else:
            index_1 = [0,1]
            index_2 = [0,2]
            load_name = "xy_xz"
    elif is_in_x_z_plane:
        if job_is_tensile:
            index_1 = [2,2]
            index_2 = [0,0]
            load_name = 'x_z'
        else:
            index_1 = [1,2]
            index_2 = [0,1]
            load_name = "xy_yz"
    elif is_in_y_z_plane:
        if job_is_tensile:
            index_1 = [1,1]
            index_2 = [2,2]
            load_name = 'y_z'
        else:
            index_1 = [0,2]
            index_2 = [1,2]
            load_name = "xz_yz"
    else:
        raise Exception(f"Could not detect what plane job is in (name = {job_name})")

    #point_number = int(re.findall(r'\d+', job_name)[0])
    quadrant_number = int(re.search(r'q(\d+)', job_name).group(1))
    point_number = int(re.search(r'_(\d+)', job_name).group(1))
    
    points_per_quadrant = problem_definition.yield_surface.load_points_per_quadrant

    #angle_point = point_number * 90/points_per_quadrant + 90*quadrant_number
    # Run get_load_angle_in_plane enough times to get the right angle:
    # for point_number_dummy in range(point_number):
    #     _ = get_load_angle_in_plane(point_number_dummy)
    def angle_in_quadrant(P, i):
        # reverse bits
        bits = P.bit_length() - 1
        rev = int(f"{i:0{bits}b}"[::-1], 2)
        return rev * 90 / P

    angle_point = angle_in_quadrant(points_per_quadrant, point_number) + 90*quadrant_number
    
    target_stress: list[list[float | str]] = [
        [0, 0, 0],
        ['x', 0, 0],
        ['x', 'x', 0]]

    field_name = f"{type_name}_{load_name}_q{quadrant_number}_{point_number}"
    # Finally calculate the stresses
    #angle_point = get_load_angle_in_plane(point_number)
    amplification = amplification_factor(angle_point) if type_name=="tensile" else 1
    stress_1 = cos(radians(angle_point))*esitmated_yield * amplification
    stress_2 = sin(radians(angle_point))*esitmated_yield * amplification
    
    target_stress[index_1[0]][index_1[1]] = stress_1
    target_stress[index_2[0]][index_2[1]] = stress_2

    job_is_required = job_name in required_results

    job_list: list[DamaskJob.YieldPointMultiaxial] = []
    job = DamaskJob.YieldPointMultiaxial(problem_definition, target_stress, field_name=field_name)
    job.angle_in_plane = angle_point
    job_list.append(job)
    return job_list

    

# DamaskJobTypes = DamaskJob.YieldPoint | DamaskJob.LoadPath | DamaskJob.YieldPointMultiaxial | DamaskJob.ElasticTensor
DamaskJobTypes =  DamaskJob.LoadPath | DamaskJob.YieldPointMultiaxial | DamaskJob.ElasticTensor