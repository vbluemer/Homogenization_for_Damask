# Elastic matrix of isotropic material

In this example, the components of the homogenized elastic tensor will be identified from a series of numerical experiments. Two methods will be used for fitting, one with an algebraic approach and one with an regression based approach.

It will be assumed that the user provides a ready-to-use grid file (`Polycrystal_25_5x5x5.vti`) and material properties file (`titanium_zero_rotation_assigned.yaml`).

The overall steps will be:

- Creating a project and adding the settings
- Running the simulation for algebraic fitting
- Running the simulation for regression fitting
- Finding the results

## Creating the project

In this example, the project name is assumed to be `template_elastic_tensor`, the grid file to be located in the project folder as `input_files/Polycrystal_25_5x5x5.vti` and the material properties file in the project folder as `input_files/titanium_zero_rotation_assigned.yaml`. In this example, all material points are unrotated with respect to the referece orientation, meaning they posses Euler angles of `[0,0,0]`. This allows a quick sanity check of results, as the components of the input material should be recovered in the homogenized result.

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

    simulation_time : 1000         
    monitor_update_cycle: 5 

elastic_tensor:
    material_type: anisotropic
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

## Results

After all required simulations are concluded and postprocessing is done, two files can be found in the project directory. These are:

1. `elastic_tensor_data.csv`: this file contains the elastic response to the applied strain in `xx`,`yy`, an all other directions. Because we used the setting `anisotropic`, no assumption of symmetry was done and the full set of 6 loadcases was performed to characterize the homogenized elastic response.
   
   ```
   field_name,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz,strain_xx,strain_yy,strain_zz,strain_xy,strain_xz,strain_yz
   strain_xx,16250.002446338549,9179.999545993098,6889.999659247517,0.0,0.0,0.0,9.999999505439053e-08,0.0,0.0,0.0,0.0,0.0
   strain_xy,0.002684483718229847,0.002684483718229847,0.0006884492975700667,7070.000000000414,0.0,0.0,-5.003996372522174e-15,-5.003996372522174e-15,0.0,1.9999999989472907e-07,0.0,0.0
   strain_xz,0.0030280752355422097,0.0008028577802576903,0.0031185029008979287,0.0,9360.00000000043,0.0,-4.999064490099561e-15,-1.1102230246251568e-16,-5.119950550789857e-15,2.662166329353621e-23,1.999999997837068e-07,-2.2204459489174614e-16
   strain_yy,9179.999545993098,16250.002446338549,6889.999659247517,0.0,0.0,0.0,0.0,9.999999505439053e-08,0.0,0.0,0.0,0.0
   strain_yz,0.0008028577802576903,0.0030280752355422097,0.0031185029008979287,0.0,0.0,9360.00000000043,0.0,-5.003996372522174e-15,-5.003996372522174e-15,0.0,0.0,1.9999999989472907e-07
   strain_zz,6889.999659247517,6889.999659247517,18060.002718823012,0.0,0.0,0.0,0.0,0.0,9.999999505439053e-08,0.0,0.0,0.0
   
   ```

2. `elastic_tensor.csv`: this file contains the computed elastic tensor in Voigt matrix form, the unit, and the mean squared error when compared to datapoints.
   
   ```
      162500.03,     91800.00,     68900.00,         0.00,         0.00,         0.00
       91800.00,    162500.03,     68900.00,         0.00,         0.00,         0.00
       68900.00,     68900.00,    180600.04,         0.00,         0.00,         0.00
           0.00,         0.00,         0.00,     46800.00,         0.00,         0.00
           0.00,         0.00,         0.00,         0.00,     46800.00,         0.00
           0.00,         0.00,         0.00,         0.00,         0.00,     35350.00
   unit,MPa
   MSE,0.00
   
   ```

## Using the regression based fitting

By changing the setting 

- `component_fitting: optimization` 

the macroscopic elastic tensor can be computed using an optimization approach, which fits the components to numerical datapoints. As for the example at hand, the change of results is negligible.

```
   162500.06,     91799.95,     68900.04,        -0.03,        -0.05,         0.04
    91799.95,    162500.12,     68900.04,        -0.04,         0.00,        -0.02
    68900.04,     68900.04,    180599.94,        -0.19,        -0.02,         0.02
       -0.03,        -0.04,        -0.19,     46799.98,         0.01,         0.00
       -0.05,         0.00,        -0.02,         0.01,     46799.94,         0.01
        0.04,        -0.02,         0.02,         0.00,         0.01,     35350.11
unit,MPa
MSE,0.00


```