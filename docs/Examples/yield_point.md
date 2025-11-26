# Example: Finding uniaxial yield points

In this example, it is shown how to find the uniaxial yield point of a material in tensile direction and in shear. The steps in this example are more elaborate then the other examples as this example is considered the 'starting point' to show all the features and functionality of the code.

Intentionally, the estimated yield stresses are set too low at first to show the importance of these setting and the need for identifying the values.

- [Example: Finding uniaxial yield points](#example-finding-uniaxial-yield-points)
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

For this example, it is assumed that the user provides a grid and a material properties file. This example uses a copy of the grid file `Polycrystal_25_5x5x5.vti` and material properties in `titanium_assigned.yaml`.

In this example, it is assumed that the most basic `GNU/Linux` console is used, so for creating a directory the command `mkdir` is used and for editing text `nano` is used. However, any other way of doing these tasks like using a graphical interface in equally valid.

The `root folder` is the folder the `Homogenization_for_DAMASK` folder.

## Create a new project and add nesscecary files

Creating a project can be done by creating a new folder inside of the projects folder (found in the root folder).

```
cd projects # Go into the projects folder

mkdir template_yield_point # Make a project folder

cd template_yield_point # Go into the project folder
```

For a clean working environment, the grid and material properties files will be placed in a separate folder, this is not strictly nesscecary. 

```
mkdir input_files # Create a folder for the input files

## Add the grid.vti and material_properties.yaml to this folder.
```

## Setup the relevant settings in the `problem_definition.yaml`

With the project folder created, the problem definition can be defined. This file always needs to contain the sections `general`, `yielding_condition` and `solver`. As we are in this case going to run a `yield_point` simulation, the `yield_point` needs to be added as well. 

How each section needs to be formatted and what values can be entered is documented in the [`Problem definition manual`](../problem_definition.md). For this example, a pre-configured `problem_definition.yaml` will be used:

```
general: 

    simulation_type     : yield_point
    remove_damask_files_after_job_completion: True
    dimensions          : 3D
    material_properties : "input_files/titanium_assigned.yaml"
    grid_file           : "input_files/Polycrystal_25_5x5x5.vti"
    stress_tensor_type: "Cauchy"
    strain_tensor_type: "true_strain"

yielding_condition:
    yield_condition: stress_strain_curve
    plastic_strain_yield: 0.002
    modulus_degradation_percentage: 0.15
    plastic_work_threshold: 889649
    estimated_tensile_yield: 400e6
    estimated_shear_yield: 250e6

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
# If not already in the root folder (currently in 'template_yield_point'):
cd ../..
```

To run the project, run the following command. It might be needed to activate the a Conda environment first:

```
# If a Conda environment is used, activate this first:
conda activate [environment_name]

# If you have used a different name then 'template_yield_point', adjust the last value!
python run_project.py template_yield_point
```

At this point a summary of the simulation tasks (2 jobs) should be given. To confirm the tasks, press `y`/`yes` or leave it `empty` and press `Enter`.

`Error?` If the first Python command does not work, make sure the problem_defintion is at the right location and spelled correct (`projects/template_yield_point/problem_definition.yaml`). Also check the error message itself, it might give a hint on what is wrong.

## Wait for completion of the simulation

The simulations should now be running. The progress is regularly posted to the screen. 

Not only is the progress posted to the screen, in the background stress/strain curves are being made which show the progress. These are located in the project folder. While DAMASK is running, we will inspect the progress in these diagrams.

`Note:` To continue while the simulation is still running, you need to open another console tab. You can also wait until the process is completed, the steps remain the same.

Navigate to the project folder:

```
cd projects/template_yield_point
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
![Stress-strain curve of x-x simulation](figures/stress_strain_curve_x-x_00.png)
**The stress strain curve of: `x-y`**
![Stress-strain curve of x-y simulation](figures/stress_strain_curve_x-y_00.png)

### No yielding found

As we can see in the stress-strain curve for x-x case, the load that was applied was too low to find yielding. Note that always all loading directions are shown even if a load was only applied in one direction. Also, the unloaded directions do not all show 0 stresses. This discrepancy arises because the stress is imposed in terms of 1st Piola Kirchhoff stress (PK1) but observed/plotted in terms of Cauchy stress.

In case that no yielding is detected in one of the scheduled jobs, there will be a statement as such in the console output. At the end of the script, the following line should be present:

```
Writing dataset to .csv file: /home/username/local_Homogenization_for_Damask/projects/template_yield_point/results/yield_points_yield_point.csv

For 1 simulations, the applied load was not sufficient to induce yielding.
Writing no yielding dataset to .csv file: /home/username/local_Homogenization_for_Damask/projects/template_yield_point/results/yield_points_yield_point_NO_YIELD.csv
```

If we go back to the results folder we can inspect the contents of this file:

Doing so, we see the jobs that did not find yielding:

```
field_name,unit,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz
x-x,Pa,NO_YIELD_DETECTED,NO_YIELD_DETECTED,NO_YIELD_DETECTED,NO_YIELD_DETECTED,NO_YIELD_DETECTED,NO_YIELD_DETECTED
```

Here we see that indeed the yield point tests in `x-x` did not detect any yielding. 

```
      increment, stress_xx[MPa], stress_yy[MPa], stress_zz[MPa], stress_yz[MPa], stress_xz[MPa], stress_xy[MPa],      strain_xx,      strain_yy,      strain_zz,      strain_yz,      strain_xz,      strain_xy,       Wp[J/m3]
              0,           0.00,           0.00,           0.00,          -0.00,           0.00,           0.00,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,         0.0000
              1,          26.67,          -0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.000237,      -0.000082,      -0.000072,      -0.000003,      -0.000001,      -0.000001,         0.0000
              2,          53.35,          -0.00,          -0.00,          -0.00,          -0.00,          -0.00,       0.000473,      -0.000164,      -0.000144,      -0.000007,      -0.000001,      -0.000002,         0.0000
              3,          80.04,           0.00,           0.00,           0.00,           0.00,           0.00,       0.000709,      -0.000246,      -0.000216,      -0.000010,      -0.000002,      -0.000004,         0.0000
              4,         106.74,          -0.00,          -0.00,          -0.00,           0.00,           0.00,       0.000945,      -0.000328,      -0.000288,      -0.000014,      -0.000002,      -0.000005,         0.0004
              5,         133.43,           0.00,          -0.00,          -0.00,          -0.00,          -0.00,       0.001181,      -0.000410,      -0.000360,      -0.000017,      -0.000003,      -0.000006,         0.0313
              6,         160.15,           0.00,           0.00,           0.00,           0.00,           0.00,       0.001416,      -0.000492,      -0.000432,      -0.000021,      -0.000003,      -0.000007,         1.2119
              7,         186.87,           0.00,          -0.00,           0.00,           0.00,           0.00,       0.001652,      -0.000573,      -0.000504,      -0.000024,      -0.000004,      -0.000008,        26.7211
              8,         213.59,          -0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.001888,      -0.000656,      -0.000576,      -0.000028,      -0.000005,      -0.000009,       376.7499
              9,         240.34,          -0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.002131,      -0.000744,      -0.000651,      -0.000035,      -0.000004,      -0.000011,      3235.0207
             10,         267.09,           0.00,           0.00,          -0.00,          -0.00,           0.00,       0.002403,      -0.000852,      -0.000733,      -0.000047,      -0.000004,      -0.000012,     15901.2025
             11,         293.87,           0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.002735,      -0.001000,      -0.000836,      -0.000069,      -0.000005,      -0.000013,     50021.4611
             12,         320.70,           0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.003148,      -0.001200,      -0.000969,      -0.000108,      -0.000011,      -0.000015,    115005.6724
             13,         347.57,           0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.003646,      -0.001452,      -0.001135,      -0.000166,      -0.000022,      -0.000011,    213164.8873
             14,         374.49,           0.00,          -0.00,           0.00,          -0.00,          -0.00,       0.004210,      -0.001745,      -0.001325,      -0.000240,      -0.000037,      -0.000000,    338608.1229
             15,         401.45,           0.00,          -0.00,          -0.00,          -0.00,          -0.00,       0.004832,      -0.002074,      -0.001538,      -0.000330,      -0.000060,       0.000014,    490341.5810
```

The above output is located in the file `yield_point_results_x-x.csv`. Here, the homogenized stresses and strains of all increments and the yield point, if it exists, are tabulated.

If we observe the two corresponding files for the x-y case, we observe the following: 

```
field_name,unit,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz
x-y,Pa,2481481.5131067894,-1739.9948845542785,-1787.925334942243,249415106.5839264,1029.9181893487976,-96.80606503039405
```

and in `yield_point_results_x-x.csv`:

```
      increment, stress_xx[MPa], stress_yy[MPa], stress_zz[MPa], stress_yz[MPa], stress_xz[MPa], stress_xy[MPa],      strain_xx,      strain_yy,      strain_zz,      strain_yz,      strain_xz,      strain_xy,       Wp[J/m3]
              0,           0.00,           0.00,           0.00,          -0.00,           0.00,           0.00,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,         0.0000
              1,           0.01,          -0.00,           0.00,          -0.00,           0.00,          16.67,      -0.000001,       0.000001,      -0.000000,      -0.000001,       0.000002,       0.000397,         0.0000
              2,           0.03,          -0.00,           0.00,          -0.00,           0.00,          33.33,      -0.000002,       0.000001,      -0.000000,      -0.000002,       0.000004,       0.000793,         0.0000
              3,           0.06,          -0.00,          -0.00,           0.00,          -0.00,          50.00,      -0.000002,       0.000002,      -0.000000,      -0.000003,       0.000006,       0.001190,         0.0000
              4,           0.11,           0.00,           0.00,          -0.00,          -0.00,          66.67,      -0.000003,       0.000002,      -0.000000,      -0.000004,       0.000009,       0.001586,         0.0051
              5,           0.17,           0.00,           0.00,          -0.00,           0.00,          83.33,      -0.000004,       0.000002,      -0.000000,      -0.000005,       0.000011,       0.001983,         0.4489
              6,           0.24,           0.00,          -0.00,           0.00,          -0.00,         100.00,      -0.000005,       0.000002,       0.000000,      -0.000006,       0.000013,       0.002379,        17.4300
              7,           0.32,          -0.00,          -0.00,          -0.00,          -0.00,         116.67,      -0.000006,       0.000001,       0.000000,      -0.000007,       0.000015,       0.002778,       374.9391
              8,           0.43,           0.00,           0.00,          -0.00,           0.00,         133.33,      -0.000006,      -0.000000,       0.000000,      -0.000008,       0.000019,       0.003196,      4269.5190
              9,           0.55,          -0.00,           0.00,           0.00,           0.00,         150.00,      -0.000005,      -0.000003,      -0.000000,      -0.000012,       0.000028,       0.003687,     21869.9429
             10,           0.72,           0.00,          -0.00,           0.00,          -0.00,         166.67,      -0.000007,      -0.000007,       0.000004,      -0.000017,       0.000048,       0.004301,     63676.5862
             11,           0.93,           0.00,          -0.00,           0.00,          -0.00,         183.33,      -0.000019,      -0.000013,       0.000021,      -0.000021,       0.000086,       0.005056,    135176.8428
             12,           1.19,          -0.00,          -0.00,           0.00,           0.00,         200.00,      -0.000040,      -0.000024,       0.000051,      -0.000035,       0.000143,       0.005953,    238965.2464
             13,           1.52,          -0.00,           0.00,           0.00,           0.00,         216.67,      -0.000069,      -0.000039,       0.000092,      -0.000074,       0.000228,       0.007027,    388476.5358
             14,           1.95,           0.00,           0.00,          -0.00,           0.00,         233.33,      -0.000103,      -0.000055,       0.000139,      -0.000141,       0.000349,       0.008349,    605856.8459
             15,           2.50,          -0.00,          -0.00,          -0.00,           0.00,         249.99,      -0.000136,      -0.000073,       0.000186,      -0.000229,       0.000505,       0.009992,    916620.9246
     yieldpoint,           2.48,          -0.00,          -0.00,          -0.00,           0.00,         249.42,      -0.000134,      -0.000072,       0.000185,      -0.000226,       0.000500,       0.009934,    905813.9392
```

### Increasing the estimated yield strength

In order to provoke a yield point in the x-x case, we need to adjust the `problem_definition.yaml`, so we will go back to root of the project folder:

```
# Assuming we are currently in the projects/template_yield_point/results folder:
cd ..
```

We need to adjust the settings `estimated_tensile_yield` and `estimated_shear_yield`. Based on what we observe in the stress-strain curves, a choice of `550e6` for the normal case and `300e6` for the shear case seem like robust choices:

```
nano problem_definition.yaml

# Look for the lines with estimated_tensile_yield and estimated_shear_yield under the section yielding_condition. Adjust these line so it is similar to:

yielding_condition:
    ...
    estimated_tensile_yield: 550e6
    estimated_shear_yield: 300e6

# Press `ctrl+x`, then `y` to save the file and finally `enter` to confirm the filename
```

Now we can re-run the simulation and likely we will find yielding in this case:

```
cd ../..

python run_project.py template_yield_point

# Confirm the prompts
```

When running this command, the previous results were still loaded. However, the code automatically detected that the estimated yield strengths have been altered and moved the old results to the `projects/template_yield_point/results_backup` folder for later reference.

**Wait for the simulations to be completed**

After the simulations have been completed, we can inspect the stress-strain curves again. These are once again located in `projects/template_yield_point/results/yield_point/...`:

These should now look something similar to:

**The stress strain curve of: `x-x`**
![Stress-strain curve of x-x simulation](figures/stress_strain_curve_x-x_01.png)
**The stress strain curve of: `x-y`**
![Stress-strain curve of x-y simulation](figures/stress_strain_curve_x-y_01.png)

Now, the intersection of the stress strain curve with the line parallel to the elastic slope, offset by 0.2% strain, is well within the observed range. The slope of this line is based on the proportionality observed in the first increment, which is assumed to be always be completely elastic.

Also, the green dot for the interpolated yield point is shown. This is the linear interpolation of where yielding occurs in between the data point before and after the yielding conditions has been met.

Note that several datapoints are visible even after yielding is detected. This is because the microstructure grid that was solved is so small (5x5x5), that a solution of all steps was found before the monitoring loop, which is set to reaccur every 5 seconds in this case, detected yielding. For grids of larger size, the increment directly after the yield point is the last one that is solved for.

The numerical values of the yield stress can be found in the generated `.csv` file. The output of the script should have already mentioned the location of this file:

```
-> Writing dataset to .csv file: /your/path/projects/template_yield_point/results/yield_points_yield_point.csv
```

Whe can inspect this file directly with `nano` (however viewing this in a more dedicated program like Excel would work as well):

```
nano /your/path/projects/template_yield_point/results/yield_points_yield_point.csv
```

This should show a output similar to the following:

```
field_name,unit,stress_xx,stress_yy,stress_zz,stress_xy,stress_xz,stress_yz
x-x,Pa,446401469.46813315,648.770083031525,-677.2888678599168,-4348.011170683678,-922.4410282257295,1755.757920212019
x-y,Pa,2499900.6914927796,-488.3589603409457,-102.3988556494387,250093621.21288902,922.2082782821932,739.3939213871301

```

The output files `yield_point_results_x-x.csv` and `yield_point_results_x-y.csv` read:

```
      increment, stress_xx[MPa], stress_yy[MPa], stress_zz[MPa], stress_yz[MPa], stress_xz[MPa], stress_xy[MPa],      strain_xx,      strain_yy,      strain_zz,      strain_yz,      strain_xz,      strain_xy,       Wp[J/m3]
              0,           0.00,           0.00,           0.00,          -0.00,           0.00,           0.00,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,         0.0000
              1,          36.67,          -0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.000325,      -0.000113,      -0.000099,      -0.000005,      -0.000001,      -0.000002,         0.0000
              2,          73.36,          -0.00,          -0.00,          -0.00,          -0.00,          -0.00,       0.000650,      -0.000225,      -0.000198,      -0.000010,      -0.000002,      -0.000003,         0.0000
              3,         110.07,           0.00,           0.00,           0.00,           0.00,           0.00,       0.000975,      -0.000338,      -0.000297,      -0.000014,      -0.000002,      -0.000005,         0.0007
              4,         146.81,          -0.00,          -0.00,          -0.00,           0.00,           0.00,       0.001299,      -0.000451,      -0.000396,      -0.000019,      -0.000003,      -0.000007,         0.2096
              5,         183.53,           0.00,           0.00,          -0.00,          -0.00,          -0.00,       0.001622,      -0.000563,      -0.000495,      -0.000024,      -0.000004,      -0.000008,        18.0436
              6,         220.26,          -0.00,           0.00,           0.00,           0.00,          -0.00,       0.001947,      -0.000677,      -0.000595,      -0.000029,      -0.000005,      -0.000010,       643.9209
              7,         257.05,           0.00,           0.00,          -0.00,          -0.00,           0.00,       0.002294,      -0.000807,      -0.000700,      -0.000041,      -0.000004,      -0.000011,      8677.8331
              8,         293.87,           0.00,          -0.00,          -0.00,           0.00,          -0.00,       0.002724,      -0.000993,      -0.000833,      -0.000067,      -0.000005,      -0.000013,     46346.7286
              9,         330.76,           0.00,          -0.00,          -0.00,           0.00,           0.00,       0.003297,      -0.001270,      -0.001018,      -0.000122,      -0.000014,      -0.000014,    137794.2516
             10,         367.73,           0.00,          -0.00,          -0.00,           0.00,           0.00,       0.004015,      -0.001637,      -0.001258,      -0.000210,      -0.000030,      -0.000005,    286350.8217
             11,         404.79,          -0.00,           0.00,          -0.01,           0.00,           0.00,       0.004845,      -0.002074,      -0.001542,      -0.000327,      -0.000059,       0.000014,    484457.9388
             12,         441.97,           0.00,          -0.00,           0.00,          -0.00,          -0.00,       0.005815,      -0.002597,      -0.001879,      -0.000469,      -0.000114,       0.000037,    752573.4347
             13,         479.34,           0.00,          -0.01,           0.00,           0.00,          -0.00,       0.007038,      -0.003278,      -0.002312,      -0.000652,      -0.000206,       0.000062,   1163849.9528
             14,         517.04,           0.00,           0.01,          -0.01,          -0.00,           0.00,       0.008749,      -0.004267,      -0.002925,      -0.000935,      -0.000346,       0.000071,   1864360.6798
             15,         555.28,           0.00,          -0.00,          -0.00,          -0.00,          -0.00,       0.011218,      -0.005738,      -0.003813,      -0.001359,      -0.000573,      -0.000002,   3033230.5373
     yieldpoint,         446.40,           0.00,          -0.00,           0.00,          -0.00,          -0.00,       0.005960,      -0.002678,      -0.001930,      -0.000491,      -0.000125,       0.000040,    801324.3822

```

and 

```
      increment, stress_xx[MPa], stress_yy[MPa], stress_zz[MPa], stress_yz[MPa], stress_xz[MPa], stress_xy[MPa],      strain_xx,      strain_yy,      strain_zz,      strain_yz,      strain_xz,      strain_xy,       Wp[J/m3]
              0,           0.00,           0.00,           0.00,          -0.00,           0.00,           0.00,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,       0.000000,         0.0000
              1,           0.01,          -0.00,           0.00,          -0.00,           0.00,          20.00,      -0.000001,       0.000001,      -0.000000,      -0.000001,       0.000003,       0.000476,         0.0000
              2,           0.04,          -0.00,           0.00,          -0.00,           0.00,          40.00,      -0.000002,       0.000001,      -0.000000,      -0.000002,       0.000005,       0.000952,         0.0000
              3,           0.09,          -0.00,          -0.00,           0.00,          -0.00,          60.00,      -0.000003,       0.000002,      -0.000000,      -0.000003,       0.000008,       0.001428,         0.0006
              4,           0.15,           0.00,           0.00,          -0.00,          -0.00,          80.00,      -0.000004,       0.000002,      -0.000000,      -0.000005,       0.000010,       0.001904,         0.1969
              5,           0.24,           0.00,           0.00,          -0.00,           0.00,         100.00,      -0.000005,       0.000002,       0.000000,      -0.000006,       0.000013,       0.002379,        17.1784
              6,           0.34,          -0.00,          -0.00,          -0.00,          -0.00,         120.00,      -0.000006,       0.000001,       0.000000,      -0.000007,       0.000016,       0.002859,       632.0516
              7,           0.47,           0.00,           0.00,          -0.00,           0.00,         140.00,      -0.000006,      -0.000001,      -0.000000,      -0.000010,       0.000022,       0.003378,      8675.6458
              8,           0.64,          -0.00,          -0.00,           0.00,          -0.00,         160.00,      -0.000005,      -0.000005,       0.000001,      -0.000015,       0.000037,       0.004029,     41857.8943
              9,           0.88,           0.00,          -0.00,           0.00,           0.00,         180.00,      -0.000015,      -0.000011,       0.000015,      -0.000019,       0.000075,       0.004871,    113969.1998
             10,           1.18,          -0.00,          -0.00,           0.00,           0.00,         200.00,      -0.000039,      -0.000024,       0.000048,      -0.000034,       0.000139,       0.005913,    230778.7731
             11,           1.59,           0.00,           0.00,          -0.00,          -0.00,         220.00,      -0.000073,      -0.000041,       0.000097,      -0.000081,       0.000242,       0.007208,    411676.2255
             12,           2.13,          -0.00,          -0.00,           0.00,           0.00,         240.00,      -0.000113,      -0.000061,       0.000154,      -0.000167,       0.000395,       0.008865,    693074.4671
             13,           2.86,           0.00,           0.00,           0.00,           0.00,         259.99,      -0.000149,      -0.000083,       0.000208,      -0.000278,       0.000599,       0.011015,   1121508.8341
             14,           3.90,          -0.00,          -0.00,          -0.00,          -0.00,         280.00,      -0.000172,      -0.000097,       0.000241,      -0.000404,       0.000877,       0.013904,   1789806.5166
             15,           5.44,           0.00,          -0.00,           0.00,          -0.00,         300.02,      -0.000193,      -0.000060,       0.000223,      -0.000519,       0.001289,       0.018139,   2929233.4643
     yieldpoint,           2.50,          -0.00,          -0.00,           0.00,           0.00,         250.09,      -0.000131,      -0.000072,       0.000181,      -0.000223,       0.000498,       0.009951,    909415.3981

```



From this, we can find that the tensile yield stress in `x-x` direction is `446.40 MPa` and the shear yield in the `x-y` direction is `250.09 MPa`. Also, we can extract the accumulated plastic work density at yielding in `x-x` and `x-y` are `801324 J/m3` and `909415 J/m3` respectively. Observing a difference in these values is expected for anisotropic materials. The plastic work density at yielding in the `x-x` case can be used as a threshold for yielding in multiaxial cases, where the linear offset criterion is not suited anymore.

When choosing the estimated yield strengths, it is important to take the following into account:

1. Making sure the estimated yield strengths will be an overestimation such that always yield will be found (also in other directions where the yield strength might be higher).
2. Not setting the estimated yield strength too high as this effectively reduces the resolution of the result, or could lead to non-convergence if even the imposed stress in the first increment cannot be accomodated by the elastic response + hardening of the observed material.