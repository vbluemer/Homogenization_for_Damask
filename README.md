# Homogenization for Damask - Enyxe

This project is an unaffiliated python-interface for [DAMASK](https://github.com/damask-multiphysics/damask) and aims to streamline typical workflows in computational mechanics, especially related to the identification of yield surfaces and their evolution. Functionalities include, among others, a comprehensive and modular pipeline to calibrate a yield function to the plastic onset observed in a microstructure, consisting of:

- design of experiments to acquire datapoints (yield points) along multi-axial stress trajectories

- execution, monitoring, and interpretation of numerical experiments: optional termination of a job once yielding is reached; interpolation of the stress state where yielding occured according to a choice of criteria with user-defined threshold

<img title="" src="docs/Examples/figures/stress_strain_curve_x-x_01.png" alt="" width="293">  <img title="" src="docs/Examples/figures/stress_strain_curve_x-y_01.png" alt="" width="295"> 

- automated fitting of a choice of yield functions to datapoints

<img title="" src="docs/Examples/figures/evolution.png" alt="" width="297">  <img title="" src="docs/Examples/figures/comparison.png" alt="" width="308"> 

- automated visualization of macroscopic stress strain curves and yield surfaces

- re-evaluation of existing result files with a changed criterion or new threshold for yielding 

- imposition of a pre-deformation history on the microstructure prior to yield surface identification

Additional functionalities include the analysis of arbitrary, user-specified load paths and homogenization of the elastic tensor of the microstructure. All analyses conducted with Enyxe benefit from effective file management and storage of post-processed results, as well as centralized access to DAMASK-internal settings through the problem definition file.

## Installation

It is highly recommended to run this project inside of a Conda (or similar) environment. Use `python 3.12` to run this project. This code is only verified to work on `Linux` with `DAMASK_grid` and `DAMASK Python` versions `v3.0.1`.

### With Conda (Python 3.12):

```
git clone https://github.com/vbluemer/Homogenization_for_Damask.git

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

### Template projects

Included in the default installation are a number of template projects that demonstrate the functionalities:

- uniaxial test

- pre-loading (with an arbitrary load history)

- performing a uniaxial test from a restart file that contains a load history

- identifying a yield surface from a series of multi-axial tests under the assumtion of tensile-compressive symmetry

- identifying a yield surface from a restart file containing a load history

- identifying a yield surface from existing result files with a changed criterion for the onset of macroscopic yielding

- identifying the homogenized elastic tensor of the material

These projects are located in the projects folder and work on a randomly generated, very small grid with material properties taken from DAMASKs [examples](https://damask-multiphysics.org/documentation/examples/index.html). The elastic tensor template project investigates a grid where all material points have identical orientation.

```
# Activate the conda environment if not already active
conda activate [environment_name]

python run_project template_yield_surface
```

The scope of the projects can be changed by adjusting the `problem_definition.yaml` located in their project folders.

### Stand-alone visualization and fitting of yield surfaces

The stand-alone script `fit_yield_surface_and_plot.py` allows fitting yield functions to two sets of data points extracted from existing projects, and visual comparison of the results. This enables tracking of yield surface evolution. Alternatively, identical datapoints can be fitted using different yield functions or varying parameter bounds to observe the influence of choice of yield function. This configuration, as well as a number of visual settings can be accessed through `compare_results/visualization_settings.yaml`. The directory contains the template datapoints `yield_points_undeformed.csv` and `yield_points_predeformed`.

### Users guide

For further guidance, review the [`Users guide`](docs/users_guide.md)

## Context

This project has been developed by Joppe Kleinhout in the context of pursuing a Msc degree in Mechanical Engineering at the University of Twente, specifically as an internship at the Research chair of Nonlinear Solid Mechanics, and later extended by Vincent Blümer. 
