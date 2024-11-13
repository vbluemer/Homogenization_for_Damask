# Homogenization for Damask

This project is an unaffiliated extension to [DAMASK](https://github.com/damask-multiphysics/damask) and aims to homogenize DAMASK results and extract useful information for engineers. In particular, the [DAMASK_grid](https://damask-multiphysics.org/support/FAQ/grid_solver.html) solver and the [Python package](https://pypi.org/project/damask/) are used to find the homogenized stress and strain state used for identifying the components of the elastic matrix, yield surface and general loading response. 

To achieve these results, this extension provides:
- Generation of DAMASK simulation files.
- Running and monitoring of DAMASK_grid simulations, including condition based termination of simulations.
- Post-processing of DAMASK simulation results extending to:
    - Homogenization of simulation domain for stress and strain
    - Fitting the results to the components of the elastic matrix
    - Finding of yield stresses for arbitrary loading directions
    - Fitting and plotting of yield surfaces
    - Plotting of stress-strain curves

## Installation
It is highly recommended to run this project inside of a Conda (or similar) environment. Use `python 3.12` to run this project. Testing of this code is only verified to work on `Linux` and `DAMASK v3.0.1`.
### With Conda (Python 3.12): 
``` 
git clone https://github.com/JoppeKleinhout/Homogenization_for_Damask.git

cd Homogenization_for_Damask

conda create -n [environment_name] python=3.12

conda activate [environment_name]

pip install -r requirements.txt # Install the required packages
```
If a system-wide installation of DAMASK does not exist yet, it can be installed into the conda environment. 
```
# NOTE: Only use this when DAMASK is not yet
# installed to prevent compatibility issues
conda activate [environment_name]

conda config --add channels conda-forge # Add the conda-forge channel

conda install conda-forge::damask 
```
## Usage 
To run a project, a project folder needs to  be created. A project folder is any folder that contains a `problem_definition.yaml` file. This project can be placed in the projects folder but can also be anywhere on the system. If the project is placed in the projects folder, the full path does not need to be specified.

The `project name` is the name of the folder where the `problem_definition.yaml` is located in.
```
# Activate the conda environment if not already active
conda activate [environment_name]

# If the project is in projects/:
python run_project [project name]

# If the project somewhere else on the system:
python run_project /path/to/[project name]
```
### Example project
Included in the default installation is a simple ready-to-run example project. This project is located in the projects folder and works on a randomly generated grid with material properties taken from DAMASKs [examples](https://damask-multiphysics.org/documentation/examples/index.html).
```
# Activate the conda environment if not already active
conda activate [environment_name]
python run_project ExampleProject
```
By default this project is setup to find the elastic matrix components of an isotropic material. This can be changed by adjusting the `problem_definition.yaml` located in [`projects/ExampleProject`](projects/ExampleProject/problem_definition.yaml).

### Users guide
For further guidance, review the [`users guide`](docs/users_guide.md)
## Context
This project has been developed by Joppe Kleinhout in the context of pursuing a Msc degree in Mechanical Engineering at the University of Twente. Specifically as an internship at the Research chair of Nonlinear Solid Mechanics.

## Acknowledgements

