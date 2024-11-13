# Users guide
In this document, explanation is given for the use of this code. 

## Input
The `problem_definition.py` defines all the settings that can be changed. The folder it resides in is considered the `project folder`.

Most of the settings defined in the `problem_definition.py` will be checked for validity and for missing values. If any errors are found in the `problem_definition.py`, this will be returned to the user.

Files can be specified relative to the problem_definition.yaml or with the full path (starting with `/`).

#### Problem definition manual
For further support with the `problem_definition.yaml`, see the [documentation](problem_definition.md)

## Output
The processing steps generate multiple outputs which will be placed in the `project folder`

During processing, the `damask_files` folder is generated with subfolder for each job to run. In this folder, all the files needed for DAMASK to run are placed and this is the working directory for DAMASK to store its results. Do not place files in this folder manually; it might get removed automatically or break the operation of the program.

The results of each simulation type gets placed in the `results` folder. The main file of storing results is the `results_database.yaml`. This file stores all the results that can be reused by new simulation requests. This file can be removed to restore the project to a clean state. 

Beside the `results_database.yaml`, all other results are placed here as well, these are;

### Plots
For any simulation where there are more then 2 increments, a plot of the stress-strain curve is made and placed in the results folder the the substructure `simulation_type/job_name`. A plot of the modulus degradation will be included as well. For the `yield_point` and `yield_surface` simulation types the interpolated yield point will shown in the plots as well.

### Elastic tensor data
For `elastic_tensor` simulations, there will be two additional results posted. The first result is the `elastic_tensor_data.csv` file. This contains all the data points that will be used for fitting of the elastic matrix and it are all the results currently stored in the `results_database.yaml`. 

The second file is the `elastic_tensor.csv` file, which contains all the components of the elastic matrix as well as the mean square error of the fit on the normalized stress.

### Yield point
Whenever the `yield_point` simulation is completed it will write all the uni-axial yield points currently stored in the `results_database.yaml` to the `yield_points_yield_point.csv` file.

### Yield surface
Whenever the `yield_surface` simulation is completed it will write all the yield points currently stored in the `results_database.yaml` to the `yield_points_yield_surface.csv` file. If not the option `None` was chosen, the fitted yield surface along with the MSE of the fit will be written to the `[yield surface name].csv` and a plot of the yield surface along with the yield data to the `[yield surface name].png`
