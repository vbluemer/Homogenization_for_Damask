# System packages
import sys
import os
import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame

# Local-packages
from homogenization_scripts.post_processor.elastic_tensor_fitting import fit_elastic_tensor, read_elastic_tensor_data_points, write_elastic_tensor_to_file

# Get the folder (directory) containing this script
scripts_folder = os.path.dirname(os.path.abspath(__file__))

# run the project
def fit_elastic_tensor_from_dataset(material_type: str, dataset_path: str, output_path: str| None = None) -> NDArray[np.float64]:

    data_set: DataFrame = read_elastic_tensor_data_points(dataset_path)
    elastic_tensor, MSE = fit_elastic_tensor(material_type, data_set)

    if not output_path == None:
        write_elastic_tensor_to_file(elastic_tensor, output_path, MSE)

    return elastic_tensor


if __name__ == "__main__":
    if not (len(sys.argv) == 3 or len(sys.argv) == 4):
        print("Not the right amount of arguments given!")
        print("Use:")
        print("python fit_elastic_tensor.py 'material_type' 'dataset_path' ['output_path'] ")
        print("Add quotes (') if the path contains spaces.")
        print("dataset_path must be a .csv file")
        print("output_path is optional")
        print("Got the following arguments:")
        for arg in range(len(sys.argv[1:])):
            if arg == 0:
                print(f"material_type = {sys.argv[arg+1]}")
            elif arg == 1:
                print(f"dataset_path = {sys.argv[arg+1]}")
            elif arg == 2:
                print(f"output_path = {sys.argv[arg+1]}")
            else:
                print(f"arg_{arg} = {sys.argv[arg+1]}")
        print("")
        raise ValueError("Not the right number of arguments supplied! See previous output for help")

    material_type: str = sys.argv[1]
    dataset_path: str = sys.argv[2]
    if len(sys.argv) == 4:
        write_result = True
        output_path: str | None = sys.argv[3]
    else:
        write_result = False
        output_path: str| None = None

    elastic_tensor = fit_elastic_tensor_from_dataset(material_type, dataset_path,output_path)