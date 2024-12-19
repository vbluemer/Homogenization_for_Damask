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

    simulation_time : 10e6         
    monitor_update_cycle: 5    

yield_surface:
    yield_criterion: Hill
    stress_state_creation: manual

    # Automatic generation settings: 
    assume_tensile_compressive_symmetry: True
    load_points_per_plane: 1

    # Manual creation settings:
    manual_stress_x_x: [ 650e6,      0,      0,     0,     0,     0]
    manual_stress_x_y: [     0,      0,      0, 350e6,     0,     0]
    manual_stress_x_z: [     0,      0,      0,     0, 350e6,     0]
    manual_stress_y_y: [     0,  650e6,      0,     0,     0,     0]
    manual_stress_y_z: [     0,      0,      0,     0,     0, 350e6]
    manual_stress_z_z: [     0,      0,  650e6,     0,     0,     0]
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
- `manual_stress_x_x`: [ 650e6,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `manual_stress_x_y`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0, 350e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `manual_stress_x_z`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0, 350e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `manual_stress_y_y`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  650e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]
- `manual_stress_y_z`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0, 350e6]
- `manual_stress_z_z`: [ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,  650e6,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0]

This concludes setting up the simulation details.

## Running the simulations
With the project folder created, the grid and materials added and problem definition defined, the project can be run. Go to installation root and run the project. Do not forget to activate a Conda environment if needed.
```
# Activate Conda environment if needed:
conda activate [environment_name]

# Run the project
python run_project.py fit_hill
```
This should end up in a summary of the simulations to run. 

Check if the settings match what was expected and confirm.

## The simulations are completed
When the simulations are completed, the results will be stored in the results folder inside of the project folder.

Directly in the results folder, three files can be found, these are:

1. `yield_points_yield_surface.csv`: This file contains the yield points that have been found found.
   ```
   field_name,unit,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz
    stress_xx=0_yy=0_zz=0_xy=0_xz=0_yz=350000000-0,Pa,-414.12442246457266,2063308.2347022966,-88.18719174432681,326.6733914353258,-361.6648476862681,220511071.9005208
    stress_xx=0_yy=0_zz=0_xy=0_xz=350000000-0_yz=0,Pa,3023133.684340043,-222.03878300775446,-78.52769201105238,174647.82286968385,288406382.90091133,-194.19379140429533
    stress_xx=0_yy=0_zz=0_xy=350000000-0_xz=0_yz=0,Pa,2659354.027203298,-573.4357862756814,318.11305747897217,263461906.74636516,378.3795240305898,-30.433705820888946
    stress_xx=0_yy=0_zz=650000000-0_xy=0_xz=0_yz=0,Pa,1254.128768166286,527.7854602454739,424530822.6395018,-209.77376066556897,96.11620153879807,445.1151705029939
    stress_xx=0_yy=650000000-0_zz=0_xy=0_xz=0_yz=0,Pa,1113.0095386840167,398853651.75510514,-567.8334646442477,13.074524390932282,-235.25191206748934,-440.68624875677307
    stress_xx=650000000-0_yy=0_zz=0_xy=0_xz=0_yz=0,Pa,492694368.35456675,359.2731477615205,880.5424790918764,-149.12313108569276,-170.0804035486115,-528.4448882835304

   ```
   If some loading directions did not result in the detection of yielding, these will be located in a file called `yield_points_yield_surface_NO_YIELD.csv`

2. `Hill.csv`: This contains the the coefficients of the Hill yield surface and the mean square error of the fit. See [`Users guide`](../users_guide.md#hill) to see the formulation used for the Hill fit.
   ```
    F,G,H,L,M,N,unit_stress,MSE
    3.857531901670379,1.6910637586328663,2.428448634138371,10.28247302204908,6.01095842899721,7.20313721713033,MPa,0.0
   ```
3. `Hill.png`: This contains the plot of the yield surface along with the simulated yielding data:
    ![Fit of Hill surface](Hill.png)
   
Also the folder `yield_surface` is created, in this, the the individual stress-strain curves and modulus degradation diagrams are shown. These have been created during each run and can be used to monitor the progress of the individual simulations.

The `results_database.yaml` is considered an internal document, however, it can be reviewed for the data it is containing. If this file is deleted, the code forgets the results it has stored. 

## Using automatic generated states
Included is an algorithm that can create n number of load points along each loading plane (see the `Hill.png` for the loading directions). In the following example, this setting will be used to created combined loading directions.

The following changes need to made to the previous `problem_definition.yaml`:
```
### Settings not mentioned here remain unchanged (and still have to be present)
general: 
    ...

yielding_condition:
    yield_condition: modulus_degradation
    modulus_degradation_percentage: 0.15
    ...

solver:
    ...

yield_surface:
    ...
    stress_state_creation: automatic

    # Automatic generation settings: 
    assume_tensile_compressive_symmetry: True
    load_points_per_plane: 3
    ...
```

Here, the following changes have been made:

The automatic stress state generation mode is enabled:
- `stress_state_creation`: automatic
  
Symmetry is assumed in tensile and compressive yield strength:
- `assume_tensile_compressive_symmetry`: True

Three loading directions will be tested per plane. As there are 6 planes this results in 3x6=18 simulations:
- `load_points_per_plane`: 3

**Change in yielding condition**

Bidirectional loading directions will be used for this simulation. The definition of 0.2% strain for yielding based on the stress-strain curve does not work for these load cases. Therefore the the energetic yielding condition `modulus_degradation` will be used for this simulation:
- `yield_condition`: modulus_degradation

This condition also needs a threshold to define when yielding has occurred. This threshold is applied to the modulus (ratio between linear deformation energy and strain squared). Here, a 15% degradation of the linear modulus is chosen to approach (but not exactly match) the 0.2% plastic strain condition:
- `modulus_degradation_percentage`: 0.15

## Run the updated project
Run the updated project. The very first messages of the script will mention that a change in settings is detected and some results are moved to a backup folder. Note however, the already existing Hill fit still exists until it is overwritten! Running the rest of the code should function as it had before.

Take into account that this set will take 3 times as long to run.

## Fitting Plunkett-Cazacu-Barlat
Wait for all the simulations to complete successfully. This will give an updated fit and plots of the Hill yield surface. If this yield surface is to be compared to the `Plunkett-Cazacu-Barlat` surface, this can be achieved by adjusting only the yield `yield_criterion` in the problem definition:
```
### Settings not mentioned here remain unchanged (and still have to be present)
general: 
    ...

yielding_condition:
    ...

solver:
    ...

yield_surface:
    yield_criterion: Cazacu-Plunkett-Barlat
    ...
```
If the project is run in this way without any other setting changing, the code will ask to reuse the existing yielding data. Confirm by pressing `Enter`. This will take the user to the summary mentioning that all results are reused and no jobs need to run. Confirming again will directly take the execution to the fitting of the `Plunkett-Cazacu-Barlat` yield surface, saving the time of having to redo all simulations.