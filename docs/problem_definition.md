# Problem definition manual

This documents reference for all the values that in the `problem_definition.yaml` file. The sections of the not used simulation types may be removed as long as the Main sections and the section of the Simulation type are present.

The sections `General`, `Yielding condition` and `Solver` are considered the Main sections and should be present independent of the simulation type chosen. For the chosen simulation type, also the relevant section needs to be filled in. For any section present, all values should have at least a valid value. 

**Main sections**

- [General](#general)
  - [Simulation type](#simulation-type)
  - [Remove DAMASK files after job completion](#remove-damask-files-after-job-completion)
  - [Dimensions](#dimensions)
  - [Material properties](#material-properties)
  - [Grid file](#grid-file)
  - [Stress tensor type](#stress-tensor-type)
  - [Strain tensor type](#strain-tensor-type)
- [Yielding condition](#yielding-condition)
  - [Yield condition](#yield-condition)
  - [Plastic strain yield](#plastic-strain-yield)
  - [Modulus degradation percentage](#modulus-degradation-percentage)
  - [Over-estimated tensile yield](#over-estimated-tensile-yield)
  - [Over-estimated shear yield](#over-estimated-shear-yield)
- [Solver](#solver)
  - [Number of increments](#number-of-increments)
  - [CPU cores](#cpu-cores)
  - [Stop after subsequent parsing errors](#stop-after-subsequent-parsing-errors)
  - [Solver type](#solver-type)
  - [Monitor update cycle](#monitor-update-cycle)
  - [Other solver settings](#other-solver-settings)

**Simulation type specific sections**

- [Yield point](#yield-point)
  - [Load direction(s)](#load-directions)
- [Yield surface](#yield-surface)
  - [Yield criterion](#yield-criterion)
  - [Stress state generation](#stress-state-generation)
  - [Assume tensile compressive symmetry](#assume-tensile-compressive-symmetry)
  - [Load points per plane](#load-points-per-plane)
  - [Manual stress states](#manual-stress-states)
- [Elastic tensor](#elastic-tensor)
  - [Material type](#material-type)
  - [Strain step](#strain-step)
  - [Component fitting](#component-fitting)
  - [Number of load cases](#number-of-load-cases)
- [Load path](#load-path)
  - [Stress states](#stress-states)
  - [Enable yielding detection](#enable-yielding-detection)

# General

- general:

The general section define what type of analysis must be done, what files will be used for the DAMASK simulations and what definitions to use for the tensors.

### Simulation type

- simulation_type

For the simulation type, choose either `yield_point`, `yield_surface`, `elastic_tensor`, `load_path`. Beside always filling in the general sections, the section for the chosen simulation type must be setup.

### Remove DAMASK files after job completion

- remove_damask_files_after_job_completion

(`True`, `False`) The DAMASK simulations are run within folders called `damask_files`, these might include the grid files, material definitions and the simulation files created by DAMASK. Especially the DAMASK simulation files can be large (1 to 10 GB or larger). To prevent taking up too much space, the DAMASK working directory can be cleaned after a simulation is completion. 

### Dimensions

- dimensions

(`3D`, `2D`) place holder value for future use. Current only effect is on the automatic stress state generation for the `yield_surface` simulation type.

### Material properties

- material_properties

(`path`) File containing material properties. This should contain the material constants and the per grain orientation and phase in `.yaml` format. The DAMASK docs consider this the materialpoint data, [see the docs here](https://damask-multiphysics.org/documentation/file_formats/materialpoint/index.html#materialpoint-configuration). Use the `damask.ConfigMaterial()` class to setup this file, see [example application](../projects/ExampleProject/input_files/create_example_grid.py) in the provided example project.

### Grid file

- grid_file

(`path`) File containing the grid information. Recommended to supply this data in the `.vti` format. A grid file can be generated or modified using the `damask.GeomGrid()` class, [see the docs here](https://damask-multiphysics.org/documentation/processing_tools/pre-processing.html#damask.GeomGrid). For generation of a random grid, see [example application](./projects/ExampleProject/input_files/create_example_grid.py) in the provided example project.

### Stress tensor type

- stress_tensor_type

(`PK1`, `PK2`, `Cauchy`) The definition to be used for calculating the stresses in the gridpoints and for homogenization. Supports 1st Piola-Kirchoff `(PK1)`, 2nd Piola-Kirchoff `(PK2)` and `Cauchy` (recommended) stress . Homogenization of `PK1` and `PK2` stress tensors use numeric averaging, `Cauchy` utilizes volumetric averaging.

### Strain tensor type

- strain_tensor_type

(`true_strain`, `Green_Lagrange`) The definition for calculating the strain in the gridpoints and for homogenization. Supports `true strain` (recommended) and `Green Lagrange` strain tensor definitions.

# Yielding condition

- yielding_condition:

Yielding can be detected during and after simulations have been completed. This can be used to define the result of an simulation or to terminate a DAMASK simulation once yielding is encountered. Termination of DAMASK simulation can be useful as calculation time of yielding scenarios can increase significantly.

### Yield condition

- yield_condition

(`stress_strain_curve`, `modulus_degradation`) The definition to be used for yielding detection. Supports detection through percentage of permanent plastic deformation derived from stress-strain curve and through modulus degradation. Stress-strain curve condition takes the strain set in `plastic_strain_yield` as yielding threshold. It is recommend to only use this condition in uni-axial load cases. Modulus degradation is a energetic yielding condition which compares the ratio between strain and deformation energy. Degradation of this ratio indicates yielding in linear elastic materials. Factor of change in this ratio used for yielding threshold can be set in the `modulus_degradation_percentage` setting.

### Plastic strain yield

- plastic_strain_yield

(`float [-]`) Permanent strain used for yielding threshold in the stress-strain curve yielding condition. This condition is only applied in loaded direction(s).

### Modulus degradation percentage

- modulus_degradation_percentage

(`float [-]`) Degradation percentage of ratio between linear deformation energy (Hooke's law) / strain magnitude compared to fully linear case. Used as yielding threshold in the modulus degradation yielding condition. 

### Over-estimated tensile yield

- estimated_tensile_yield

(`float [Pa]`) Overestimation of yield strength strength in uni-axial tensile loading. Automatically generated load cases which aim to find yield strength use this value to setup the maximum stress to use for a simulation. Increase this stress if no yielding is found.

### Over-estimated shear yield

- estimated_shear_yield

(`float [Pa]`) Overestimation of yield strength strength in uni-axial shear loading. Automatically generated load cases which aim to find yield strength use this value to setup the maximum stress to use for a simulation. Increase this stress if no yielding is found.

# Solver

- solver:

Settings used for the DAMASK_grid solver.

### Number of increments

- N_increments

(`integer [count]`) Number of increments to use to in between initial and final stress state. Settings this lower speeds up calculation time. Higher value gives more intermediate steps and gives more accurate results for yield identifying simulations. Setting not used in `elastic_tensor` type simulations.

### CPU cores

- cpu_cores

(`integer [count]`) Number of cores to use for the DAMASK_grid process by setting the `OMP_NUM_THREADS` environment variable. if set to 0, environment variable `OMP_NUM_THREADS` is unchanged (DAMASK_grid uses a system default value instead). It is recommended to leave at least 1 core free for the monitoring and iteration analysis.

### Stop after subsequent parsing errors

- stop_after_subsequent_parsing_errors

(`integer [count]`) While monitoring the DAMASK_grid process, it might happen that the DAMASK_grid process is writing to a file while the monitoring loop is trying to read data from it. There are protections in place that should prevent this and a recoverable error is encountered when this happens. If this happens on many subsequent loops, a error has likely occurred and the process is stopped. Default values is 20.

### Solver type

- solver type

(`spectral_basic`) Placeholder value of setting the DAMASK_grid solver. 

### Monitor update cycle

- monitor_update_cycle

(`float [seconds]`) The update interval for polling the DAMASK_grid and the associated results files. Default is 5 seconds. Higher values reduces the calculational need, lower increases the likelihood that monitoring loop captures all the increments. 

### Other solver settings

For documentation on `N_staggered_iter_max`, `N_cutback_max`, `N_iter_min`, `N_iter_max`, `eps_abs_div_P`, `eps_rel_div_P`, `eps_abs_P`, `eps_rel_P, eps_abs_curl_F`, `eps_rel_curl_F`, see DAMASK documentation [here](https://damask-multiphysics.org/documentation/file_formats/numerics.html).

# Yield point

- yield_point:

The settings in this section are used for the `yield_point` simulation type. This simulation type identifies the yield stresses in uni-axial loading directions. 

Do not forget to set the `estimated_tensile_yield` and `estimated_shear_yield` in the [Yielding condition](#yielding-condition) section.

### Load direction(s)

- load_direction

(`x-x`, `x-y`, `x-z`, `y-y`, `y-z`, `z-z`, `list(...)`) Uni-axial direction(s) to identify the yield point in. 

# Yield surface

- yield_surface:

The settings in section are used for the `yield_surface` simulation type. This simulation type identifies the yield stresses in any arbitrary loading direction and fits this data to a specified yield surface.

Do not forget to set the `estimated_tensile_yield` and `estimated_shear_yield` in the [Yielding condition](#yielding-condition) section.

### Yield criterion

- yield_criterion

(`Hill` [[source](https://royalsocietypublishing.org/doi/abs/10.1098/rspa.1948.0045)], `Cazacu-Plunkett-Barlat` [[source](https://doi.org/10.1016/j.ijplas.2007.07.013)], `Cazacu-Plunkett-Barlat_extended_n` [[source](https://doi.org/10.1016/j.ijplas.2007.07.013)], `None`, `...`) The yield surface to fit the yield point data to. 

For `Cazacu-Plunkett-Barlat_extended_n` replace n by any positive integer.

Implementation of custom yield surfaces is possible. This requires the user to write some Python functions. For the steps to take to do so, review the [Advanced](users_guide.md#implementation-of-additional-yield-surface) section in the `Users guide`.

If less then expected results are shown in the resulting plot of the yield surface, or the `yield_points_yield_surface.csv` contains less then expected yielding points, check the `results_database.yaml` under the section `yield_surface` for `NO_YIELDING_FOUND`. If these are present, the applied loading was not great enough to induce yielding in the material. Either increase the `estimated_tensile_yield` and `estimated_shear_yield` values if automatic stress state generation is used or increase the magnitude given in the manual stress state if manual stress state generation is used, see [`Stress state generation`](#stress-state-generation).

### Stress state generation

- stress_state_creation

(`automatic`, `manual`) Method of creating loading directions to identify yield points in. 

For `automatic`, a distribution of loading directions is created depending on the `assume_tensile_compressive_symmetry` and `load_points_per_plane` options. For high values, the distribution approaches an even distribution in all loading direction. In this mode, some modification of the  `estimated_tensile_yield` and `estimated_shear_yield` from the [Yielding condition](#yielding-condition) section is made to take into account higher magnitude of yielding stress in combined loading directions. 

For `manual` creation, define the loading directions with loading magnitude in the `stress_` fields.

### Assume tensile compressive symmetry

- assume_tensile_compressive_symmetry

(`True`, `False`) For creating stress states, assume that yield point in tensile and compressive states are symmetric.

### Load points per plane

- load_points_per_plane

(`integer [count]`) Number of loading directions to create for yield identification. For value of `1`, only uni-axial tests are performed. 

### Manual stress states

- stress_x_x, stress_x_y, stress_x_z, stress_y_y, stress_y_z, stress_z_z

(`float [Pa]`, `list(float) [Pa]`) The loading directions with over-exaggerated stress magnitudes to identify yielding in. Can either by single value for each loading direction, or list of equal length in each direction. 

For stress states to be visible in the resulting plot, a applied load must either be uni-axial or be a combined loading in at most 2 directions. For combined loadings, only pure normal loadings or pure shear loads are shown. All data is used during the data fitting process, even when not shown in the plot. 

# Elastic tensor

- elastic_tensor:

The settings in section are used for the `yield_surface` simulation type. This simulation type identifies the components of the elastic matrix (Voigt notation).

### Material type

- material_type

(`anisotropic`,  `monoclinic`, `orthotropic`, `tetragonal`, `cubic`, `isotropic`) The type of the material to assume for fitting the components of the elastic matrix. 

### Strain step

- strain_step

(`float [-]`) Magnitude of strain step to take for linear properties identification. Default value is 1E-7.

### Component fitting

- component_fitting

(`algebraic`, `optimization`) Type of fitting to use for finding matrix components. 

In `algebraic`, algebraic relationship between stress and strain components are used for fitting. This mode uses a single stress/strain value to represent all symmetry values defined by the material type. The setting `number_of_load_cases` is always `minimum` and this mode can not be used independently.

In `optimization`, a regression approach is used to fit the components of the elastic matrix. This mode takes into account all relationships in symmetry equally and can take any number of data points.

### Number of load cases

- number_of_load_cases

(`minimum`, `all_directions`, `combined_directions`) The number of load cases to use for data fitting. For all material types, there is an absolute minimum of test that needs to be performed to acquire all the independent coefficients in the elastic matrix. 

For `all_directions`, a strain step is taken in all 6 uni-axial directions. For some material types this setting equals the `minimum` setting.

For `combined_directions`, all 21 unique combinations of uni-axial and bidirectional strain steps are used for data generation. The absolute magnitude of the strain step defined in `strain_step` option is maintained.

`Note:` The `results/results_database.yaml` file stores the results of this simulation type and holds this over multiple runs, accumulating results as long as simulation settings do not change or the user (requests to) remove these. The data fitting process always takes all the datapoints present in the `results_database.yaml` file, hence, it is possible that more datapoints are used then defined in this setting. 

# Load path

- load_path:

The settings in section are used for the `load_path` simulation type. This simulation type simulates the load path as defined in the settings and gives the homogenized stress and strains at each increment.

### Stress states

- stress_x_x, stress_x_y, stress_x_z, stress_y_y, stress_y_z, stress_z_z

(`float [Pa]`, `list(float) [Pa]`) The stress state(s) to simulate. Can either by single value for each loading direction, or list of equal length in each direction. In between each stress state, the number of increments is defined by [`N_increments`](#solver) from the solver section.

### Enable yielding detection

- enable_yield_detection

(`True`, `False`) Option to monitor for yielding conditions. If yielding conditions are met, the simulation will be terminated prematurely. `Note:` this option is best used for load paths with just one loading direction or where yielding only occurs in the first loading step as the application of yielding definitions break in changing loading directions.