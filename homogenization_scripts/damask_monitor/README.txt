The damask monitor module contains a pre-processor, simulation and post-processor module.
The pre-processor handles finalizing the preperation process for each damask_job:
    Create a specific folder for damask to work in.
    create a specific folder to place the results artifacts in.
    Set all "runtime" specific paths for the damask_job

The simulation module handles starting, monitoring and stopping (if needed) the damask process. This results in a {project_name}.hdf5 result.

The post-processor handles reading the result file, gather the needed data specified in the damask_job and store the results in both the results folder and the results_database
