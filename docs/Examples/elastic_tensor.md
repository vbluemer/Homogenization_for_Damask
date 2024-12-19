# Elastic matrix of isotropic material
In this example, the components of the isotropic elastic matrix will be fitted to simulation data. The elastic data will be acquired by running the nesscecary DAMASK simulations. Two methods will be used for fitting, one with an algebraic approach and one with an regression based approach.

It will be assumed that the user provides a ready-to-use grid file (`grid.vti`) and material properties file (`material_properties.yaml`).

The overall steps will be:
- Creating a project and adding the settings
- Running the simulation for algebraic fitting
- Running the simulation for regression fitting
- Finding the results

## Creating the project

In this example, the project name is assumed to be `fit_elastic`, the grid file to be located in the project folder as `input_files/grid.vti` and the material properties file in the project folder as `input_files/material_properties.yaml`. In this example the randomly grid and material properties files are used from the ExampleProject, with the estimated yield strengths found in the [`uniaxial yield points`](yield_point.md) example.

Within the project folder, create the `problem_definition.yaml`. Add the following configuration:
```
general: 
    simulation_type     : elastic_tensor
    remove_damask_files_after_job_completion: True
    dimensions          : 3D
    material_properties : "input_files/material_properties.yaml"
    grid_file           : "input_files/grid.vti"
    stress_tensor_type: "Cauchy"
    strain_tensor_type: "true_strain"
    reduce_parasitic_stresses : False

yielding_condition:
    # These are not relevant for this simulation but have to be present
    yield_condition: stress_strain_curve
    plastic_strain_yield: 0.002
    modulus_degradation_percentage: 0.15
    estimated_tensile_yield: 650e6
    estimated_shear_yield: 350e6

solver:
    N_increments: 15 # This setting is ignored for 'elastic tensor'
    cpu_cores: 0
    # The following settings are technical DAMASK settings
    stop_after_subsequent_parsing_errors: 20
    solver_type: "spectral_basic"
    N_staggered_iter_max: 10      
    N_cutback_max: 3        
    N_iter_min: 1            
    N_iter_max: 100         
    eps_abs_div_P: 1.0e-4            
    eps_rel_div_P: 5.0e-4            
    eps_abs_P: 1.0e3                  
    eps_rel_P: 1.0e-3                 
    eps_abs_curl_F: 1.0e-10          
    eps_rel_curl_F: 5.0e-4           

    simulation_time : 10e6         
    monitor_update_cycle: 5 

elastic_tensor:
    material_type: isotropic
    strain_step: 1e-7
    component_fitting: algebraic
    number_of_load_cases: minimum
```
In this configuration the following important settings for this simulation are found:

The simulation type is set for the elasticity properties:
- `simulation_type`     : elastic_tensor
  
The elastic components of a isotropic material is used:
- `material_type`: isotropic
    
The finite strain step to take is `1e-7`:
- `strain_step`: 1e-7

For the first test algebraic fitting of the components is used:
- `component_fitting`: algebraic

This concludes setting up the simulation details.

## Running the simulations
With the project folder created, the grid and materials added and problem definition defined, the project can be run. Go to installation root and run the project. Do not forget to activate a Conda environment if needed.
```
# Activate Conda environment if needed:
conda activate [environment_name]

# Run the project
python run_project.py fit_elastic
```
This should end up in a summary of the simulations to run. 

Check if the settings match what was expected and confirm.

## The simulation is completed
When the simulations are completed, the results will be stored in the results folder inside of the project folder.

Directly in the results folder, two files can be found, these are:

1. `elastic_tensor_data.csv`: this is the file containing the data extracted form the simulations. In this case that is only 1 simulation that needed to be performed:
    ```
    field_name,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz,strain_xx,strain_yy,strain_zz,strain_xy,strain_xz,strain_yz
    strain_xx,16731.53427299464,7783.933026998837,7591.270663524702,-38.27332233825143,-24.32190042691757,91.53982146555383,9.999999568245186e-08,-4.893594794577097e-17,-4.3894712420253994e-17,3.9329340499548915e-18,-1.1548470058196328e-19,7.687243060060078e-19
    ```
2. `elastic_tensor.csv`: The components of fitted elastic matrix, included with the unit associated stress unit and mean square of the fit. 
   ```
    unit_stress,MSE,C_11,C_12,C_13,C_14,C_15,C_16,C_21,C_22,C_23,C_24,C_25,C_26,C_31,C_32,C_33,C_34,C_35,C_36,C_41,C_42,C_43,C_44,C_45,C_46,C_51,C_52,C_53,C_54,C_55,C_56,C_61,C_62,C_63,C_64,C_65,C_66
    MPa,4.718670157102958e-06,167315.34995386715,77839.33363073906,77839.33363073906,0.0,0.0,0.0,77839.33363073906,167315.34995386715,77839.33363073906,0.0,0.0,0.0,77839.33363073906,77839.33363073906,167315.34995386715,0.0,0.0,0.0,0.0,0.0,0.0,44738.008161564045,0.0,0.0,0.0,0.0,0.0,0.0,44738.008161564045,0.0,0.0,0.0,0.0,0.0,0.0,44738.008161564045
   ```
## Using the regression based fitting
The only change in the problem definition is the `component_fitting` setting in the `problem_definition.yaml`. This change in setting does not require the simulation results to be reevaluated, hence, the result will be found quickly:
```
### Settings not mentioned here remain unchanged (and still have to be present)

general: 
    ....

yielding_condition:
    # These are not relevant for this simulation but have to be present
    ...

solver:
    ... 

elastic_tensor:
    ...
    component_fitting: optimization
    number_of_load_cases: minimum
```

With these adjustments made, run the project again. Make sure to reuse the already stored simulation results when prompted.

## The updated simulation is completed
With the simulation completed, the contents of the `elastic_tensor_data.csv` remain unchanged, however, the `elastic_tensor.csv` contains different values:
```
unit_stress,MSE,C_11,C_12,C_13,C_14,C_15,C_16,C_21,C_22,C_23,C_24,C_25,C_26,C_31,C_32,C_33,C_34,C_35,C_36,C_41,C_42,C_43,C_44,C_45,C_46,C_51,C_52,C_53,C_54,C_55,C_56,C_61,C_62,C_63,C_64,C_65,C_66
MPa,1.726256527249081e-05,167315.35383055027,76876.03147814867,76876.03147814867,0.0,0.0,0.0,76876.03147814867,167315.35383055027,76876.03147814867,0.0,0.0,0.0,76876.03147814867,76876.03147814867,167315.35383055027,0.0,0.0,0.0,0.0,0.0,0.0,45219.6611762008,0.0,0.0,0.0,0.0,0.0,0.0,45219.6611762008,0.0,0.0,0.0,0.0,0.0,0.0,45219.6611762008
```
These values are ever so slightly different then with algebraic fitted results. This is because of the assumption made for the `isotropic` material properties. The algebraic fitting process assumes that the elastic response matches the assumed material type. Hence, for the strain step in the `x-x` direction this requires the same response in `y-y` direction and the `z-z` directions. Therefore, the algebraic fit just takes the response in `y-y` direction to represent the `z-z` direction as well.

However, from the data in `elastic_tensor_data.csv` it can be seen that this is not the case. The regression approach takes into account all values, and therefore gets to different results.