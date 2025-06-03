# System packages
import os
import textwrap

# Local packages
from .yield_surfaces.cazacu_plunkett_barlat import *
from .yield_surfaces.cazacu_plunkett_barlat_extended_2 import *
from .yield_surfaces.hill48 import *
from .yield_surfaces.example_yield_surface import ExampleYieldSurface
from ..messages.messages import Messages
from .yield_surfaces.general_functions import fit_surface, write_dataset
from ..common_classes.problem_definition import ProblemDefinition
from .yield_surfaces.general_functions import read_yield_points
from .yield_surfaces.plot_surface import make_plot_yield_surface
from .yield_surfaces.yield_surface_template import YieldSurfaces

def fit_yield_surface_problem_definition(problem_definition: ProblemDefinition) -> None:

    problem_definition = write_dataset(problem_definition)

    dataset_path = problem_definition.general.path.yield_points_csv

    yield_criterion = problem_definition.yield_surface.yield_criterion
    symmetry = problem_definition.yield_surface.assume_tensile_compressive_symmetry

    output_path = os.path.join(problem_definition.general.path.results_folder, f"{yield_criterion}.csv")
    plot_path = os.path.join(problem_definition.general.path.results_folder, f"{yield_criterion}.png")
    
    #breakpoint()
    fit_yield_surface(yield_criterion, dataset_path, output_path, plot_path, symmetry)

def fit_yield_surface(yield_surface_name: str, dataset_path: str, output_path: str, plot_path: str, symmetry: bool) -> YieldSurfaces:
    # This function takes the name of a yield surface and the yield points it should be fitted to.
    # The coefficients are stored to a file and plots of the fit are shown.
    
    if "Cazacu-Plunkett-Barlat_extended_" in yield_surface_name:
        n = int(yield_surface_name.split("Cazacu-Plunkett-Barlat_extended_")[1])
        yield_surface_name = "Cazacu-Plunkett-Barlat_extended"
    
    # To add a yield surface, add a "case" block. The same name used in the problem_definition is used to 
    # match the name with here. An example for a yield surface called "example_yield_surface" is added here.
    # Also, add a function that takes the fitting steps, an example for this is added as well.
    match yield_surface_name:
        case "None":
            return None # type: ignore
        case 'Hill':
            return fit_hill(dataset_path, output_path, plot_path, symmetry)
        case "Cazacu-Plunkett-Barlat":
            return fit_cazacu_plunkett_barlat(dataset_path, output_path, plot_path, symmetry, use_extended=False)
        case "Cazacu-Plunkett-Barlat_extended":
            return fit_cazacu_plunkett_barlat(dataset_path, output_path, plot_path, symmetry, use_extended=n) # type: ignore
        case "example_yield_surface":
            return fit_example_yield_surface(dataset_path, output_path, plot_path, symmetry)
        case _:
            raise Exception(textwrap.fill(f"Yield surface fitting/plotting for {yield_surface_name} is not implemented yet. Did you spell it correctly?", width=80))


# This is an example yield surface
def fit_example_yield_surface(dataset_path: str, output_path: str, plot_path: str, symmetry: bool) -> ExampleYieldSurface:

    # Provide some feedback to the user.
    print("Running example_yield_surface, this does not do much rather then act as a simple example")

    data_set = read_yield_points(dataset_path, symmetry)
    
    yield_surface_to_fit = ExampleYieldSurface(some_constant = 5)
    example_yield_surface: ExampleYieldSurface = fit_surface(yield_surface_to_fit, data_set) # type: ignore

    print(f"Example yield surface was fitted. some_coefficient = {example_yield_surface.coefficient_1}")

    example_yield_surface.write_to_file(output_path, example_yield_surface.mean_square_error_stress)

    make_plot_yield_surface(example_yield_surface, data_set, plot_path, symmetry)

    return example_yield_surface


def fit_hill(dataset_path: str, output_path: str, plot_path: str, symmetry: bool) -> Hill:

    data_set = read_yield_points(dataset_path, symmetry)
    
    hill: Hill = fit_surface(Hill(), data_set) # type: ignore

    Messages.YieldSurface.show_hill_fit(hill) # type: ignore

    hill.write_to_file(output_path, hill.mean_square_error_stress)

    make_plot_yield_surface(hill, data_set, plot_path, symmetry)

    return hill


def fit_cazacu_plunkett_barlat(dataset_path: str, output_path: str, plot_path: str, symmetry: bool, use_extended: bool | int) -> CazacuPlunkettBarlat:

    data_set = read_yield_points(dataset_path, symmetry)

    a_coeff_test_values: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    fitted_cazacu_plunkett_barlat_list: list[CazacuPlunkettBarlat] = list()

    # The Cazacu-Plunkett-Barlat yield surface has both continues (C_ij, k) as integer (a) coefficients.
    # This is difficult to combine in a single optimization scheme. Hence, a list of "a" values 
    # are used and for each the "C_ij" and "k" coefficients are fitted. 
    # In the end the Cazacu-Plunkett-Barlat surface is taken with the lowest MSE.
    
    lowest_MSE: float = None # type: ignore
    index_lowest_MSE = 0
    for index in range(len(a_coeff_test_values)):

        if use_extended == False:
            cazacu_plunkett_barlat_fit = fit_surface(CazacuPlunkettBarlat(a = a_coeff_test_values[index]), data_set)
        else:
            cazacu_plunkett_barlat_fit = fit_surface(CazacuPlunkettBarlatExtendedN(a = a_coeff_test_values[index], n=use_extended), data_set)

        fitted_cazacu_plunkett_barlat_list.append(cazacu_plunkett_barlat_fit) # type: ignore
        MSE = cazacu_plunkett_barlat_fit.get_and_set_MSE(data_set)

        if lowest_MSE == None: # type: ignore
            lowest_MSE = MSE
            index_lowest_MSE = index
            continue
        
        if lowest_MSE > MSE:
            lowest_MSE = MSE
            index_lowest_MSE = index

    cazacu_plunkett_barlat = fitted_cazacu_plunkett_barlat_list[index_lowest_MSE]

    Messages.YieldSurface.show_cazacu_plunkett_barlat_fit(cazacu_plunkett_barlat) # type: ignore

    cazacu_plunkett_barlat.write_to_file(output_path, cazacu_plunkett_barlat.mean_square_error_stress)

    make_plot_yield_surface(cazacu_plunkett_barlat, data_set, plot_path, symmetry)

    return cazacu_plunkett_barlat


