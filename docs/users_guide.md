# Users guide

In this document, explanation is given for the use of this code. 

- [Users guide](#users-guide)
  - [Input](#input)
    - [The problem definition file](#the-problem-definition-file)
    - [Material properties and grid file](#material-properties-and-grid-file)
  - [Output](#output)
    - [Plots](#plots)
    - [Elastic tensor data](#elastic-tensor-data)
    - [Yield point](#yield-point)
    - [Yield surface](#yield-surface)
    - [Load path](#load-path)
- [Independent use scripts](#independent-use-scripts)
  - [Fitting of elastic tensor](#fitting-of-elastic-tensor)
  - [Fitting of yield surface](#fitting-of-yield-surface)
- [Examples](#examples)
  - [Finding (uniaxial) yield points](#finding-uniaxial-yield-points)
  - [Fitting Hill yield surface](#fitting-hill-yield-surface)
  - [Fitting isotropic elastic matrix components](#fitting-isotropic-elastic-matrix-components)
  - [Running a simple loading and unloading load case](#running-a-simple-loading-and-unloading-load-case)
- [Advanced features](#advanced-features)
  - [Implementation of an additional yield surface](#implementation-of-an-additional-yield-surface)
  - [using the optimizer for experimental data](#using-the-optimizer-for-experimental-data)

## Input

### The problem definition file

The `problem_definition.py` defines all the settings that can be changed. The folder it resides in is considered the `project folder`.

Most of the settings defined in the `problem_definition.py` will be checked for validity and for missing values. If any errors are found in the `problem_definition.py`, this will be returned to the user.

Files can be specified relative to the problem_definition.yaml or with the full path (starting with `/`).

For further support with the `problem_definition.yaml`, see the [documentation](problem_definition.md)

### Material properties and grid file

To run DAMASK simulations, material properties and the grid file needs to be supplied. For the purposes of this code, it is assumed that the user has provides the valid `material_properties.yaml` and `grid.vti`. For the `material_properties.yaml` file, see either the DAMASK docs on [Materialpoint configuration](https://damask-multiphysics.org/documentation/file_formats/materialpoint/index.html) or review an example of what steps to take in preparation files in the [ExampleProject](../projects/ExampleProject/input_files/create_example_grid.py). And for the grid, see either the DAMASK docs on [Geometry](https://damask-multiphysics.org/documentation/file_formats/grid_solver.html#geometry) or see the steps for a randomly generated in the [ExampleProject](../projects/ExampleProject/input_files/create_example_grid.py) as well.

## Output

The processing steps generate multiple outputs which will be placed in the `project folder`

During processing, the `damask_files` folder is generated with subfolder for each job to run. In this folder, all the files needed for DAMASK to run are placed and this is the working directory for DAMASK to store its results. Do not place files in this folder manually; it might get removed automatically or break the operation of the program.

The results of each simulation type gets placed in the `results` folder. The main file of storing results is the `results_database.yaml`. This file stores all the results that can be reused by new simulation requests. This file can be removed to restore the project to a clean state. 

Whenever the user enters in the prompt while running the program, or when it has been detected that compared to the previous run that important simulation settings have been changed, most relevant results will be moved to a backup folder marked with the time in the `results_backup` folder.

Beside the `results_database.yaml`, all other results are placed here as well, these are;

### Plots

For any simulation where there are more then 2 increments, a plot of the stress-strain curve is made and placed in the results folder the the substructure `simulation_type/job_name`. A plot of the modulus degradation will be included as well. For the `yield_point` and `yield_surface` simulation types the interpolated yield point will shown in the plots as well.

### Elastic tensor data

For `elastic_tensor` simulations, there will be two additional results posted. The first result is the `elastic_tensor_data.csv` file. This contains all the data points that will be used for fitting of the elastic matrix and it are all the results currently stored in the `results_database.yaml`. 

The second file is the `elastic_tensor.csv` file, which contains all the components of the elastic matrix as well as the mean square error of the fit on the normalized stress.

### Yield point

Whenever the `yield_point` simulation is completed it will write all the uni-axial yield points currently stored in the `results_database.yaml` to the `yield_points_yield_point.csv` file.

### Yield surface

Whenever the `yield_surface` simulation is completed it will write all the yield points currently stored in the `results_database.yaml` to the `yield_points_yield_surface.csv` file. If any other [`yield_criterion`](problem_definition.md#yield-criterion) then the option `None` was chosen, the fitted yield surface along with the MSE of the fit will be written to the `[yield surface name].csv` and a plot of the yield surface along with the yield data to the `[yield surface name].png`

#### Hill

The Hill yield surface [[`source`](https://royalsocietypublishing.org/doi/abs/10.1098/rspa.1948.0045)] is fitted to the following equation:

$$
F( \sigma_y - \sigma_z)^2 + G( \sigma_z - \sigma_x)^2 + H( \sigma_x - \sigma_y)^2 + 2L \tau_{yz}^2 + 2M \tau_{zx}^2 + 2N \tau_{xy}^2 - \sigma_{\textup{Y}}^2 = 0
$$

Where $F$, $G$, $H$, $L$, $M$ and $N$ are the coefficients fitted by the code, and the stress state in the unit of `MPa`

#### Cazacu-Plunkett-Barlat

The Cazacu-Plunkett-Barlat [[`source`](https://doi.org/10.1016/j.ijplas.2007.07.013)] is fitted to the following equation:

$$
\left(|\Sigma_1| - k\Sigma_1\right)^a + 
\left(|\Sigma_2| - k\Sigma_2\right)^a + 
\left(|\Sigma_3| - k\Sigma_3\right)^a - \sigma_{\textup{Y}}^a= 0
$$

Where

$$
\Sigma^{\textup{Voigt}} = C \cdot S^{\textup{Voigt}}
$$

$S$ is the deviatoric stress matrix, $\Sigma$ is a transformed stress state and $\Sigma_i$ the principle stresses. $C$, $k$ and $a$ are the fitted coefficients returned by the code and the stresses in the deviatoric stress $S$ given in `MPa`.

#### Cazacu-Plunkett-Barlat Extended n

The Cazacu-Plunkett-Barlat Extended n [[`source`](https://doi.org/10.1016/j.ijplas.2007.07.013)] is fitted to the following equation:

$$
\sum^n_{i=1} f^i(S) = 0
$$

Where

$$
f^i(S) = \left(|\Sigma^i_1| - k^i\Sigma^i_1\right)^a + 
\left(|\Sigma^i_2| - k^i\Sigma^i_2\right)^a + 
\left(|\Sigma^i_3| - k^i\Sigma^i_3\right)^a - \sigma_{\textup{Y}}^a
$$

$$
\Sigma^{i,\textup{Voigt}} = C^i \cdot S^{\textup{Voigt}}
$$

$S$ is the deviatoric stress matrix, $\Sigma^i$ is a transformed stress state and $\Sigma^i_j$ the principle stresses. $C^1, C^2, ..., C^n$, $k^1, k^2, ..., k^n$ and $a$ are the fitted coefficients returned by the code and the stresses in the deviatoric stress $S$ given in `MPa`.

### Load path

The results of a `load_path` simulation type is stored very similarly to the other simulation results in the results folder, however, all the results are concentrated within the subfolder specific to each run `load_path-[date and time]`.

The results of the load path simulation are not considered for reuse when a new simulation starts and its results are not stored in the `results_database.yaml`

# Independent use scripts

Some of the post processing can also be used Independently from the DAMASK processing steps. This is the case for the fitting of a `yield surface` and the regression based `elastic tensor` fitting. Reference on how to use these scripts will be given in this section.

## Fitting of elastic tensor

For fitting of the components of the elastic matrix, the `fit_elastic_tensor.py` script located in the root folder can be used. This script needs to be run in the following way:

```
python fit_elastic_tensor.py [material_type] [dataset_path] <output_path>

# Example using dummy values:
python fit_elastic_tensor.py isotropic elastic_data.csv fitted_result.csv
```

The script can also be called as a standalone python function:

```
# Import the script in the same folder
from fit_elastic_tensor import fit_elastic_tensor_from_dataset

elastic_matrix = fit_elastic_tensor_from_dataset(material_type, dataset_path)

# Example using dummy values:
elastic_matrix = fit_elastic_tensor_from_dataset("isotropic", "elastic_data.csv")

# Or when the result should also be witen to a file, include a 3th argument with the output path:
elastic_matrix = fit_elastic_tensor_from_dataset("isotropic", "elastic_data.csv", "fitted_result.csv")

# The function returns a 6x6 a Numpy NDArray.
```

Here, `[material_type]` must be replaced by the name of the type of material to use. See the list of supported material types in the [Problem definition guide](problem_definition.md#material-type).

Replace `[dataset_path]` with the path of a `.csv` file containing the required data points needed for finding the components of the elastic matrix. If too little data points are supplied, the function will still complete. However, some components might still be (close to) 1. Take into account that there will always be a conversion done on the stress data from `Pa` to `MPa`. The `.csv` file must contain column names on the first row with at least the fields:

 `stress_xx`, `stress_yy`, `stress_zz`, `stress_yz`, `stress_xz`, `stress_xy`

`strain_xx`, `strain_yy`, `strain_zz`, `strain_yz`, `strain_xz`, `strain_xy`

The data fitting is using a strain based approach, hence the each data point (row) should be of a uni-axial strain step with corresponding stress states. The output of a `elastic_tensor` simulation also provides this file and can be used a reference. 

The field `<output_path>` is an optional field and can be left empty. The fitted elastic matrix will always be shown in the console, but can also be written to a file. Independent of the name and extension, the output file will always be written as if it is a `.csv` file.

This function always uses the [`optimization`](problem_definition.md#component-fitting) mode for component fitting.

## Fitting of yield surface

The script `fit_yield_surface_and_plot.py` can be used in order to compare yield points and yield surfaces from different projects in one figure. This helps tracking the evolution of a yield surface or can help visualize the differences of fitted yield functions or the influence of parameter bounds. By default, it runs with the visualization settings provided in `compare_results/visualization_settings.yaml`.

# Examples

A example is given for each simulation type that can be used. The `Finding (uniaxial) yield points` is considered as an entrypoint for first time users. In this example the creation of a project, setting the basic settings, running of the code and retrieval of results is discussed. For the other examples this is considered to be understood topics.

For more extensive reference on the options, see the [`Problem definition guide`](problem_definition.md).

## Finding (uniaxial) yield points

In this example, it is shown how to find the uniaxial yield point of a material in tensile direction and in shear.

See this example [`here`](Examples/yield_point.md).

## Fitting Hill yield surface

In this example, the Hill yield surface will be fitted with yielding data in multiple loading directions. The yielding data will be acquired by running the nesscecary DAMASK simulations.

See this example [`here`](Examples/yield_surface.md).

## Fitting isotropic elastic matrix components

In this example, the components of the isotropic elastic matrix will be fitted to simulation data. The elastic data will be acquired by running the nesscecary DAMASK simulations. Two methods will be used for fitting, one with an algebraic approach and one with an regression based approach.

See this example [`here`](Examples/elastic_tensor.md).

## Running a simple loading and unloading load case

In this example, a loading and unloading case will be simulated using DAMASK. First, a load is applied in the `x-y` shear direction, then a normal `x-x` direction after which the material is unloaded. The resulting stress and strain at every increment will be the output data.

See this example [`here`](Examples/load_path.md).

# Advanced features

Beside the normal operation of this code, some additional features can be used for further research. These additional features are not as straight forwards as adjusting `problem_definition.yaml` and might require some more programming knowledge to apply as some source code might need alteration. 

The features that will be discussed are the application of additional yield surfaces and using a regression based approach to fit the constants describing the material properties and to calibrate the components of the elastic matrix to experimental data.

## Implementation of an additional yield surface

For reference on how to add a yield surface, view the tutorial [`here`](implement_yield_surface.md).
