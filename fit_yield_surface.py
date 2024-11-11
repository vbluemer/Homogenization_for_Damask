# System packages
import sys
import os

# Local-packages
from homogenization_scripts.post_processor.fit_yield_surface import fit_yield_surface
from homogenization_scripts.post_processor.yield_surfaces.yield_surface_template import YieldSurfaces
# get name of the project to run

# Get the folder (directory) containing this script
scripts_folder = os.path.dirname(os.path.abspath(__file__))

# run the project
def fit_yield_surface_from_dataset(yield_surface_name: str, dataset_path: str, output_path: str, plot_path: str) -> YieldSurfaces:

    yield_surface: YieldSurfaces = fit_yield_surface(yield_surface_name, dataset_path, output_path, plot_path)

    return yield_surface


if __name__ == "__main__":
    if not len(sys.argv) == 5:
        print("Not the right amount of arguments given!")
        print("Use:")
        print("python fit_yield_surface.py 'yield_surface_name' 'dataset_path' 'output_path' 'plot_path' ")
        print("Add quotes (') if the path contains spaces.")
        print("dataset_path must be a .csv file")
        print("Got the following arguments:")
        for arg in range(len(sys.argv[1:])):
            if arg == 0:
                print(f"yield_surface_name = {sys.argv[arg+1]}")
            elif arg == 1:
                print(f"dataset_path = {sys.argv[arg+1]}")
            elif arg == 2:
                print(f"output_path = {sys.argv[arg+1]}")
            elif arg == 3:
                print(f"plot_path = {sys.argv[arg+1]}")
            else:
                print(f"arg_{arg} = {sys.argv[arg+1]}")
        print("")
        raise ValueError("Not the right number of arguments supplied! See previous output for help")

    yield_surface_name: str = sys.argv[1]
    dataset_path: str = sys.argv[2]
    output_path: str = sys.argv[3]
    plot_path: str = sys.argv[4]

    yield_surface = fit_yield_surface(yield_surface_name, dataset_path, output_path, plot_path)