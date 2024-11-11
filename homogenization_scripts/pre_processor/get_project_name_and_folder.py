# System packages
import os


def get_project_name_and_folder(project_name_input: str, scripts_folder: str):
    # This function figures out where to find the project specified when starting the script

    # If project name is given, project is found in projects/
    # Otherwise absolute path should be given.
    if project_name_input[0] == "\\" or project_name_input[0] == "/":
        project_path = project_name_input
    else:
        path_to_projects_folder = os.path.join(scripts_folder, 'projects')
        project_path = os.path.join(path_to_projects_folder, project_name_input)
    
    project_path = os.path.normpath(project_path)

    project_name = os.path.basename(project_path)

    return (project_name, project_path)