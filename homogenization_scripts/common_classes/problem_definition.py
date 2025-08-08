# System packages
from typing import Literal

# Local packages 
from ..pre_processor.common_classes_pre_processor.reused_results import ReusedResults


# This file exists to help Python editors understand the structure 
# of the ProblemDefinition class

class Tensor:
    class Stress:
        class PK1:
            def __str__(self):
                return f"first Piola-Kirchoff"
            def str(self) -> str:
                return "PK1"
            
        class PK2:
            def __str__(self):
                return f"second Piola-Kirchoff"
            def str(self) -> str:
                return "PK2"
            
        class Cauchy:
            def __str__(self):
                return f"Cauchy (true) stress"
            def str(self) -> str:
                return "Cauchy"

    class Strain:
        class TrueStrain:
            def __str__(self):
                return f"true strain"
            def str(self) -> str:
                return "true_strain"
            
        class GreenLagrange:
            def __str__(self):
                return f"Green Lagrange strain"
            def str(self) -> str:
                return "Green_Lagrange"

StressTensors = Tensor.Stress.PK1 | Tensor.Stress.PK2 | Tensor.Stress.Cauchy
StrainTensors = Tensor.Strain.TrueStrain | Tensor.Strain.GreenLagrange

class Path:
    dimensions_file                         : str
    project_path                            : str
    material_properties                     : str
    grain_orientation                       : str
    grid_file                               : str
    results_database_file                   : str
    results_folder                          : str
    backup_results_folder                   : str
    problem_definition_file                 : str
    damask_files_folder                     : str
    elastic_tensor_data_csv                 : str
    elastic_tensor_csv                      : str
    yield_points_csv                        : str
    load_path_csv                           : str
    restart_file_path                       : str



class General:
    simulation_type                         : Literal["yield_point", "yield_surface", "elastic_tensor", "load_path"]
    automatic_reevaluate                    : bool
    remove_damask_files_after_job_completion: bool
    reduce_parasitic_stresses               : bool
    dimensions                              : Literal["2D", "3D"]
    project_name                            : str
    path                                    : Path
    stress_tensor_type                      : StressTensors
    strain_tensor_type                      : StrainTensors

class YieldingCondition:
    yield_condition                         : Literal["stress_strain_curve", "modulus_degradation", "plastic_work"]
    plastic_strain_yield                    : float
    modulus_degradation_percentage          : float
    plastic_work_threshold                  : float
    estimated_tensile_yield                 : float
    estimated_shear_yield                   : float

class Solver:
    N_increments                            : int
    cpu_cores                               : int
    stop_after_subsequent_parsing_errors    : int
    solver_type                             : str
    N_staggered_iter_max                    : int
    N_cutback_max                           : int
    N_iter_min                              : int
    N_iter_max                              : int
    eps_abs_div_P                           : float          
    eps_rel_div_P                           : float         
    eps_abs_P                               : float                  
    eps_rel_P                               : float                 
    eps_abs_curl_F                          : float          
    eps_rel_curl_F                          : float          
    simulation_time                         : float
    monitor_update_cycle                    : float

class YieldPoint:
    load_direction                          : Literal[ "x-x", "x-y", "x-z", "y-y", "y-z", "z-z"] | list[Literal[ "x-x", "x-y", "x-z", "y-y", "y-z", "z-z"]]

class YieldSurface:
    yield_criterion                         : str
    yield_stress_ref                        : float
    load_points_per_quadrant                : int
    assume_tensile_compressive_symmetry     : bool
    stress_state_creation                   : Literal["manual", "automatic"]
    stress_x_x                              : list[float]
    stress_x_y                              : list[float]
    stress_x_z                              : list[float]
    stress_y_y                              : list[float]
    stress_y_z                              : list[float]
    stress_z_z                              : list[float]

class ElasticTensor:
    material_type                           : Literal["anisotropic",  "monoclinic", "orthotropic", "tetragonal", "cubic", "isotropic"]
    strain_step                             : float
    number_of_load_cases                    : Literal["minimum", "all_directions", "combined_directions"]
    component_fitting                       : Literal["algebraic", "optimization"]

class LoadPath:
    stress_x_x                              : list[float]
    stress_x_y                              : list[float]
    stress_x_z                              : list[float]
    stress_y_y                              : list[float]
    stress_y_z                              : list[float]
    stress_z_z                              : list[float]
    enable_yield_detection                  : bool

class ProblemDefinition:
    # This portion explains to Python editors the structure of the class ProblemDefinition
    general                                 : General
    yielding_condition                      : YieldingCondition
    solver                                  : Solver
    yield_point                             : YieldPoint
    yield_surface                           : YieldSurface
    elastic_tensor                          : ElasticTensor
    load_path                               : LoadPath
    reused_results                          : ReusedResults
    _fields                                 : list[str]


    def __init__(self, dictionary: dict[str, str | float | dict[str,str | float]]):
        self._fields = dictionary.keys() # type: ignore
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = ProblemDefinition(value) # type: ignore 
            setattr(self, key, value)

    def __bool__(self):
        return False
            
    def keys(self) -> list[str]:
        return self._fields  # Return the top-level fields
    
    def add_reused_results_information(self, reused_results: ReusedResults) -> None:
        self.reused_results = reused_results