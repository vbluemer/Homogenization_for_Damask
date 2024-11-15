# Fitting Hill yield surface
In this example, the Hill yield surface will be fitted with yielding data in multiple loading directions. The yielding data will be acquired by running the nesscecary DAMASK simulations. Two yield surfaces will be fitted, one with only uniaxial load tests and one with bidirectional yield tests included.

It will be assumed that the user provides a ready-to-use grid file (`grid.vti`), material properties file (`material_properties.yaml`) and has a reasonable estimate for the yield strengths, see the example on [`uniaxial yield points`](yield_point.md) how to find this last requirement.

The overall steps will be:
- Creating a project and adding the settings
- Running the simulation
- Finding the results

## Creating the project

In this example, the project name is assumed to be `fit_hill`, the grid file to be located in the project folder as `input_files/grid.vti` and the material properties file in the project folder as `input_files/material_properties.yaml`. In this example the randomly grid and material properties files are used from the ExampleProject, with the estimated yield strengths found in the [`uniaxial yield points`](yield_point.md) example.

Within the project folder, create the `problem_definition.yaml`. Add the following configuration:

```
general: 
    simulation_type     : yield_surface
    remove_damask_files_after_job_completion: True
    dimensions          : 3D
    material_properties : "input_files/material_properties.yaml"
    grid_file           : "input_files/grid.vti"
    stress_tensor_type: "Cauchy"
    strain_tensor_type: "true_strain"
    reduce_parasitic_stresses : False

yielding_condition:
    yield_condition: stress_strain_curve
    plastic_strain_yield: 0.002
    modulus_degradation_percentage: 0.15
    estimated_tensile_yield: 650e6
    estimated_shear_yield: 350e6

solver:
    N_increments: 15
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

yield_surface:
    yield_criterion: Hill
    stress_state_creation: manual

    # Automatic generation settings: 
    assume_tensile_compressive_symmetry: True
    load_points_per_plane: 1

    # Manual creation settings:
    stress_x_x: [ 650e6,      0,      0,     0,     0,     0]
    stress_x_y: [     0,      0,      0, 350e6,     0,     0]
    stress_x_z: [     0,      0,      0,     0, 350e6,     0]
    stress_y_y: [     0,  650e6,      0,     0,     0,     0]
    stress_y_z: [     0,      0,      0,     0,     0, 350e6]
    stress_z_z: [     0,      0,  650e6,     0,     0,     0]
```

In this configuration the following important settings for this simulation are found:

The simulation type is set for the yield surface:
- `simulation_type`     : yield_surface
  
The yielding condition is set to be 0.2% of plastic strain. This is a suitable definition because only uniaxial loading will be applied in this run.
- `yield_condition`: stress_strain_curve
- `plastic_strain_yield`: 0.002

The yield surface to be fitted is Hill:
- `yield_criterion`: Hill
    
The loading directions to test yielding in will be defined by the user:
- `stress_state_creation`: manual

The loading direction and magnitude are setup for uniaxial yielding:
- `stress_x_x`: [ 650e6,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `stress_x_y`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0, 350e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `stress_x_z`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0, 350e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `stress_y_y`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  650e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `stress_y_z`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0, 350e6]
- `stress_z_z`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  650e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]