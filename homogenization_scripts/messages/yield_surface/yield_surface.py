# System packages
import numpy as np

# Local packages
# from ...post_processor.yield_surfaces.cazacu_plunkett_barlat import Barlatcazacu
# from ...post_processor.yield_surfaces.hill48 import Hill

class YieldSurface:

    def writing_dataset_to(self, dataset_path: str) -> None:
        print(f"Writing dataset to .csv file: {dataset_path}")

    def writing_no_yield_dataset_to(self, no_yield_dataset_path: str, number_no_yield: int) -> None:
        print("")
        print(f"For {number_no_yield} simulations, the applied load was not sufficient to induce yielding.")
        print(f"Writing no yielding dataset to .csv file: {no_yield_dataset_path}")

    def reading_dataset_from(self, dataset_path: str) -> None:
        print(f"Reading dataset from .csv file: {dataset_path}")

    def creating_plot_at(self, display_name: str, plot_path: str) -> None:
        print(f"Creating a plot of {display_name} fit at {plot_path}")

    def writing_results(self, display_name: str, path:str) -> None:
        print("")
        print(f"Writing {display_name} fit to .csv file: {path}")

    def fitting_yield_surface(self, display_name:str) -> None:
        print(f"")
        print(f"Fitting {display_name} yield surface to yield point data...")

    def show_cazacu_plunkett_barlat_fit(self, cazacu_plunkett_barlat) -> None: # type: ignore
        print(f"")
        print(f"Fitted Barlat-cazacu with MSE (stress) of: {cazacu_plunkett_barlat.mean_square_error_stress}") # type: ignore
        print(f"Unit stress: {cazacu_plunkett_barlat.unit_name()}") # type: ignore
        print(f"Coefficients of the Barlat-Plunkett-Cazacu function are:")
        print(f"k = {cazacu_plunkett_barlat.k}") # type: ignore
        print(f"a = {cazacu_plunkett_barlat.a}") # type: ignore
        print(f"C = ")
        np.set_printoptions(linewidth=1000)
        print(cazacu_plunkett_barlat.c) # type: ignore
        np.set_printoptions()

    def show_hill_fit(self, hill) -> None: # type: ignore
        print(f"Fitted Hill with MSE (stress) of: {hill.mean_square_error_stress}") # type: ignore
        print(f"Coefficients of Hill are:")
        print(f"F = {hill.f}, G = {hill.g}, H = {hill.h}") # type: ignore
        print(f"L = {hill.l}, M = {hill.m}, N = {hill.n}") # type: ignore