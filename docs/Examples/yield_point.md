# Example: Finding uniaxial yield points
In this example, it is shown how to find the uniaxial yield point of a material in tensile direction and in shear. The steps in this example are more elaborate then the other examples as this example is considered the 'starting point' to show all the features and functionality of the code.

Intentionally, the estimated yield stresses are set too low at first to show the importance of these setting and the need for identifying the values.

- [Example: Finding uniaxial yield points](#example-finding-uniaxial-yield-points)
  - [](#)- [Example: Finding uniaxial yield points](#example-finding-uniaxial-yield-points)
  - [Create a new project and add nesscecary files](#create-a-new-project-and-add-nesscecary-files)
  - [Setup the relevant settings in the `problem_definition.yaml`](#setup-the-relevant-settings-in-the-problem_definitionyaml)
  - [Run the simulation](#run-the-simulation)
  - [Wait for completion of the simulation](#wait-for-completion-of-the-simulation)
  - [The simulation is finished](#the-simulation-is-finished)
    - [No yielding found](#no-yielding-found)
    - [Increasing the estimated yield strength](#increasing-the-estimated-yield-strength)



The overall steps will be:

1. Create a new project and add nesscecary files
2. Setup the relevant settings in the `problem_definition.yaml`
3. Run the simulation
4. Find the results and adjust settings

For this example, it is assumed that the user provides a grid file named `grid.vti` and a material properties file named `material_properties.yaml`. For this example, a copy of the grid and material properties of the `ExampleProject` will be used.

In this example, it is assumed that the most basic `GNU/Linux` console is used, so for creating a directory the command `mkdir` is used and for editing text `nano` is used. However, any other way of doing these tasks like using a graphical interface in equally valid.

The `root folder` is the folder the `Homogenization_for_DAMASK` folder.

## Create a new project and add nesscecary files
Creating a project can be done by creating a new folder inside of the projects folder (found in the root folder).
```
cd projects # Go into the projects folder

mkdir yield_point_test # Make a project folder

cd yield_point_test # Go into the project folder
```

For a clean working environment, the grid and material properties files will be placed in a separate folder, this is not strictly nesscecary. 
```
mkdir input_files # Create a folder for the input files

## Add the grid.vti and material_properties.yaml to this folder.
```
## Setup the relevant settings in the `problem_definition.yaml`
With the project folder created, the problem definition can be defined. This file always needs to contain the sections `general`, `yielding_condition` and `solver`. As we are in this case going to run a `yield_point` simulation, the `yield_point` needs to be added as well. 

How each section needs to be formatted and what values can be entered is documented in the [`Problem definition manual`](../problem_definition.md). For this example, a pre-configured `problem_definition.yaml` will be used from the `ExampleProject` where most of the comments have been removed for clarity.

**Make the problem_definition.yaml**
```
# Make sure you are in the yield_point_test folder.

nano problem_definition.yaml

# 1. Paste the contents of the problem_definition given below (to paste inside of a console use 'ctrl+shift+v').
# 2. press `ctrl+x`, then `y` to save the file and finally `enter` to confirm the filename
```
Contents of the problem_definition.yaml to copy:
```
general: 

    simulation_type     : yield_point
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
    estimated_tensile_yield: 65e6
    estimated_shear_yield: 35e6

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


yield_point:
    load_direction: ['x-x', 'x-y']
```
If another name or folder for the `grid` or `material properties` is used, be sure to adjust these in the `material_properties` and `grid_file` entries.

These are some important settings that have been put into the `problem_definition.yaml`:

The simulation type is setup to be a uniaxial yield point test:

1. `simulation_type`     : yield_point 

For the definition of yielding, the plastic deformation of 0.2% is used:

2. `yield_condition` : stress_strain_curve
3. `plastic_strain_yield`: 0.002

The number of increments that are taken towards the final stress state is 15:

4. `N_increments`: 15

The DAMASK default number of CPU cores is used (set to this to 4 if DAMASK is giving errors):

5. `cpu_cores`: 0

The yield point will be identified in the normal `x-x` direction and the shear `x-y` direction:

6. `load_direction`: ['x-x', 'x-y']

The last important settings are `estimated_tensile_yield` and `estimated_shear_yield`. These are now intentionally set too low (65 MPa and 35 MPa respectively). This is to show what the effect is when these are set too low and adjusting these will be part of the example.

## Run the simulation
Now the grid, material properties and problem definition are setup, the simulation can be run. Go back to the `root folder` if not already there:
```
# If not already in the root folder (currently in 'yield_point_test'):
cd ../..
```
To run the project, run the following command. It might be needed to activate the a Conda environment first:
```
# If a Conda environment is used, activate this first:
conda activate [environment_name]

# If you have used a different name then 'yield_point_test', adjust the last value!
python run_project.py yield_point_test
```
At this point a summary of the simulation tasks (2 jobs) should be given. To confirm the tasks, press `y`/`yes` or leave it `empty` and press `Enter`.

`Error?` If the first Python command does not work, make sure the problem_defintion is at the right location and spelled correct (`projects/yield_point_test/problem_definition.yaml`). Also check the error message itself, it might give a hint on what is wrong.

## Wait for completion of the simulation

The simulations should now be running. The progress is regularly posted to the screen. 

Not only is the progress posted to the screen, in the background stress/strain curves are being made which show the progress. These are located in the project folder. While DAMASK is running, we will inspect the progress in these diagrams.

`Note:` To continue while the simulation is still running, you need to open another console tab. You can also wait until the process is completed, the steps remain the same.

Navigate to the project folder:
```
cd projects/yield_point_test
```
Notice that new folders have been created in the project folder (i.e. use the command `ls` to show these). One is the `damask_files`. This is the folder where DAMASK is working in and is not the one we are interested in. There should also be a folder called `results`, this is the folder we are interested in. Enter the folder:
```
cd results
```
Depending on how far the simulation has gotten at this point, there will be a folder and maybe some files. For now go into the folder, which should be called `yield_point`:
```
cd yield_point
```
In here, you will find the folders `x-x` and maybe already `x-y`. These are corresponding to the simulations we have queued and contain the plots of the respective simulations. Go into `x-x`:
```
cd x-x
```
You will see that there are 2 pictures in this folder: `stress_strain_curve.png` and `modulus_degradation.png` (use the command `ls`). 

These plots are generated while the simulation is running to show the progress and finalized when the simulation is finished. 

## The simulation is finished
Wait until the simulation is finished to inspect the stress-strain curves. 

Find a way to open the `stress_strain_curve.png` located in the `results/yield_point/x-x` and `results/yield_point/x-y` folders. If the grid and material properties of the ExampleProject is used, the results should look similar to the following:

**The stress strain curve of: `x-x`**
![Stress-strain curve of x-x simulation](stress_strain_curve_x-x.png)
**The stress strain curve of: `x-y`**
![Stress-strain curve of x-y simulation](stress_strain_curve_x-y.png)

### No yielding found

As we can see in the stress-strain curves, the load that was applied was too low to find yielding in either simulation. Note that always all loading directions are shown even if a load was only applied in one direction. Also, the unloaded directions do not all show 0 stresses. This is expected behavior due to a different stress definition used by DAMASK. Because of this, parasitic stresses of the magnitude of 1% to 2% of an applied shear load can be expected in the tensile directions, see the `x-x` curve for the stress-curve of the `x-y` test case. For most cases, this small error should not be a significant problem.

Back to the problem of no yielding: another hint have gotten that the applied load was too low is the hint given in the output of the script. At the end of the script, the following line should be present:
```
-> For 2 simulations, the applied load was not sufficient to induce yielding.
-> Writing no yielding dataset to .csv file: /your/path/.../yield_point_test/results/yield_points_yield_point_NO_YIELD.csv
```
If we go back to the results folder we can inspect the contents of this file:
```
# Assuming currently in projects/yield_point_test/results/yield_point/x-x
cd ../..

nano yield_points_yield_point_NO_YIELD.csv
```
Doing so, we see the jobs that did not find yielding:
```
-> field_name,unit,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz
-> x-x, Pa, NO_YIELD_DETECTED, NO_YIELD_DETECTED, ...
-> x-y, Pa, NO_YIELD_DETECTED, NO_YIELD_DETECTED, ...
```
Here we see that indeed the yield point tests in `x-x` and `x-y` did not detect any yielding. We will need to increase the yield strength estimation given in the `problem_definition.yaml`.

### Increasing the estimated yield strength

We need to adjust the `problem_definition.yaml`, so we will go back to root of the project folder:

```
# Assuming we are currently in the projects/yield_point_test/results folder:
cd ..
```
We need to adjust the settings `estimated_tensile_yield` and `estimated_shear_yield`. A safe assumption is that both will be yielding at a applied load of `1000 MPa`:

```
nano problem_definition.yaml

# Look for the lines with estimated_tensile_yield and estimated_shear_yield under the section yielding_condition. Adjust these line so it is similar to:

yielding_condition:
    ...
    estimated_tensile_yield: 1000e6
    estimated_shear_yield: 1000e6

# Press `ctrl+x`, then `y` to save the file and finally `enter` to confirm the filename
```
Now we can re-run the simulation and likely we will find yielding in this case:
```
cd ../..

python run_project.py yield_point_test

# Confirm the prompts
```
When running this command, the previous results were still loaded. However, the code automatically detected that the estimated yield strengths have been altered and moved the old results to the `projects/yield_point_test/results_backup` folder for later reference.

**Wait for the simulations to be completed**

After the simulations have been completed, we can inspect the stress-strain curves again. These are once again located in `projects/yield_point_test/results/yield_point/...`:

These should now look something similar to:

**The stress strain curve of: `x-x`**
![Stress-strain curve of x-x simulation](stress_strain_curve_x-x_yielding.png)
**The stress strain curve of: `x-y`**
![Stress-strain curve of x-y simulation](stress_strain_curve_x-y_yielding.png)

In this case, we indeed see clear yielding behavior. Other then in the previous stress-strain curves, we see two new additions. There are red lines showing the yielding threshold set at 0.2% of plastic strain. The slope of this line is based on the first iteration, which is assumed to be always be fully linear.

Also, the green dot for the interpolated yield point is shown. This is the linear interpolation of where yielding occurs in between the data point before and after the yielding conditions has been met.

Finally, it can be noted that less data points have shown up compared to the previous stress-strain curves. In the previous, `15` data points are visible which corresponds to the `N_increments` setting provided in the `problem_definition.yaml`. In the updated stress-strain curves, only `8` are visible. This is because the monitoring loop detected that yielding had occurred and terminated the simulation prematurely to save time.

The numerical values of the yield stress can be found in the generated `.csv` file. The output of the script should have already mentioned the location of this file:
```
-> Writing dataset to .csv file: /your/path/projects/yield_point_test/results/yield_points_yield_point.csv
```
Whe can inspect this file directly with `nano` (however viewing this in a more dedicated program like Excel would work as well):
```
nano /your/path/projects/yield_point_test/results/yield_points_yield_point.csv
```
This should show a output similar to the following:
```
field_name,unit,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz
x-x, Pa, 494049892.81288314, 509.5155726552522, 277.9729182444896, 462.0312202509435, 377.57650202766547, -102.04590777101937
x-y, Pa, 2749628.1370206294, 109.66823277912755, -437.09224045146306, 268407366.9545309, 194.50825956790385, -124.82580955193718
```
From this, we can find that the tensile yield stress in `x-x` direction is `494 MPa` and the shear yield in the `x-y` direction is approximately `268 MPa`. 

Knowing this, we can improve the estimated yielding values given in the `problem_definition.py`. When updating the estimated yield strengths, it is important to take the following into account:

1. Making sure the estimated yield strengths will be an overestimation such that always yield will be found (also in other directions where the yield strength might be higher).
2. Not setting the estimated yield strength too high as this effectively reduces the resolution of the result.

For these simulation results, a good middle ground for setting the estimated yield strengths could be `650 MPa` for `estimated_tensile_yield` and `350 MPA` for estimated_shear_yield. This would lead to the following settings in the `problem_definition.yaml`:
```
yielding_condition:
    ...
    estimated_tensile_yield: 650e6
    estimated_shear_yield: 350e6
```

Updating these values can be of value for later simulations.