# System packages
import sys
import os

# Local-packages
from homogenization_scripts.main_script import main_loop
from homogenization_scripts.common_classes.problem_definition import ProblemDefinition

# Get the folder (directory) containing this script
scripts_folder = os.path.dirname(os.path.abspath(__file__))

def run_project(project_name: str, skip_checks: bool = False) -> ProblemDefinition:

    problem_definition = main_loop(project_name, scripts_folder, skip_checks)

    return problem_definition

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("Not the right amount of arguments given!")
        print("Use:")
        print("python run_project.py 'project' ")
        print("project is either the name of a folder in the 'projects' folder, or...")
        print("a full path to a project folder (any folder containing a problem_definition.yaml file)")
        print("Add quotes (') if the path contains spaces.")
        print("Got the following arguments:")
        for arg in range(len(sys.argv[1:])):
            if arg == 0:
                print(f"project = {sys.argv[arg+1]}")
            else:
                print(f"arg_{arg} = {sys.argv[arg+1]}")
        print("")
        raise ValueError("Not the right number of arguments supplied! See previous output for help")
    
    # get name of the project to run
    project_name: str = sys.argv[1]
    # run the project
    problem_definition = main_loop(project_name, scripts_folder)

