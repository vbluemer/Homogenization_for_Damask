# System packages
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd

# Local-packages
from homogenization_scripts.post_processor.fit_yield_surface import fit_yield_surface
from homogenization_scripts.post_processor.yield_surfaces.yield_surface_template import YieldSurfaces
from homogenization_scripts.post_processor.yield_surfaces.general_functions import read_yield_points
from homogenization_scripts.post_processor.yield_surfaces.plot_surface import make_plot_yield_surface,plot_data_points,plot_surface
from homogenization_scripts.common_classes.figure_style import FigureStyle



def make_comparison_plot_yield_surface(
        yield_surface1: YieldSurfaces,
        yield_surface2: YieldSurfaces,
        data_set1,
        data_set2,
        path: str,
        symmetry1: bool,
        symmetry2: bool,
        style1,
        style2):


    
    fig, axs = plt.subplots(nrows=2, ncols=3) # type: ignore
    fig.set_size_inches(20,(2/3)*20) 
        
    #Messages.YieldSurface.creating_plot_at(yield_surface.display_name(), path)
    plot_data_points(axs, data_set1, yield_surface1.unit_conversion(), symmetry1, style1) # type: ignore
    plot_data_points(axs, data_set2, yield_surface2.unit_conversion(), symmetry2, style2) # type: ignore
    plot_surface(axs, yield_surface1, style1) # type: ignore
    plot_surface(axs, yield_surface2, style2) # type: ignore
    

    
    xlimits = np.empty([6,2])
    ylimits = np.empty([6,2])
    for e, ax in enumerate(axs.flat):
        xlimits[e,:] = ax.get_xlim()
        ylimits[e,:] = ax.get_ylim()
    
    xlimits_normal = xlimits[:3,:]
    ylimits_normal = ylimits[:3,:]
    xlimits_shear  = xlimits[3:,:]
    ylimits_shear  = ylimits[3:,:]
    
    for e, ax in enumerate(axs.flat):
        if e<3:
            ax.set_xlim(min(xlimits_normal[:,0]),max(xlimits_normal[:,1]))
            ax.set_ylim(min(ylimits_normal[:,0]),max(ylimits_normal[:,1]))
        else:
            ax.set_xlim(min(xlimits_shear[:,0]),max(xlimits_shear[:,1]))
            ax.set_ylim(min(ylimits_shear[:,0]),max(ylimits_shear[:,1]))
        ax.set_aspect('equal')
    
    for text in fig.findobj(match=plt.Text):
        text.set_fontsize(style1.fs)
    
    fig.tight_layout()
    fig.savefig(path) # type: ignore

    return fig

def faded(color, factor=0.5):
    h, s, v = mcolors.rgb_to_hsv(mcolors.to_rgb(color))
    return mcolors.hsv_to_rgb((h, s*factor, v))



blue = '#0072BD'
orange = '#D95319'
purple = '#7E2F8E'

alpha = 0.4
blue0 = faded(blue, alpha)
orange0 = faded(orange, alpha)
purple0 = faded(purple, alpha)

yield_surface_name = 'Cazacu-Plunkett-Barlat'
#yield_surface_name = 'Hill'
yield_stress_ref = 419.14e6
dataset_path1 = 'compare/yield_points_yield_surface1.csv'
dataset_path2 = 'compare/yield_points_yield_surface2.csv'
output_path1 = 'compare/results1.csv'
output_path2 = 'compare/results2.csv'
plot_path1 = 'compare/ys1.png'
plot_path2 = 'compare/ys2.png'
plot_path3 = 'compare/comparison.png'
symmetry1 = False
symmetry2 = True

data_set1 = read_yield_points(dataset_path1, symmetry1)
data_set2 = read_yield_points(dataset_path2, symmetry2)

style1 = FigureStyle(linewidth=3, 
                    markersize=12,
                    markeredgewidth = 2,
                    fontsize=20,
                    pt_color=blue,
                    sym_pt_color=blue,
                    ln_color=purple)

style2 = FigureStyle(linewidth=2, 
                    markersize=12,
                    markeredgewidth = 1,
                    fontsize=20,
                    pt_color=blue0,
                    sym_pt_color=blue0,
                    ln_color=purple0)

yield_surface1   = fit_yield_surface(yield_surface_name, yield_stress_ref, dataset_path1, output_path1, plot_path1, symmetry1)
yield_surface2   = fit_yield_surface(yield_surface_name, yield_stress_ref, dataset_path2, output_path2, plot_path2, symmetry2)
fig              = make_comparison_plot_yield_surface(yield_surface1,yield_surface2, data_set1,data_set2, plot_path3, symmetry1, symmetry2,style1,style2)

    
# if __name__ == "__main__":
#     if not len(sys.argv) == 5:
#         print("Not the right amount of arguments given!")
#         print("Use:")
#         print("python fit_yield_surface.py 'yield_surface_name' 'dataset_path' 'output_path' 'plot_path' ")
#         print("Add quotes (') if the path contains spaces.")
#         print("dataset_path must be a .csv file")
#         print("Got the following arguments:")
#         for arg in range(len(sys.argv[1:])):
#             if arg == 0:
#                 print(f"yield_surface_name = {sys.argv[arg+1]}")
#             elif arg == 1:
#                 print(f"dataset_path = {sys.argv[arg+1]}")
#             elif arg == 2:
#                 print(f"output_path = {sys.argv[arg+1]}")
#             elif arg == 3:
#                 print(f"plot_path = {sys.argv[arg+1]}")
#             else:
#                 print(f"arg_{arg} = {sys.argv[arg+1]}")
#         print("")
#         raise ValueError("Not the right number of arguments supplied! See previous output for help")

#     yield_surface_name: str = sys.argv[1]
#     dataset_path: str = sys.argv[2]
#     output_path: str = sys.argv[3]
#     plot_path: str = sys.argv[4]


    #make_plot_yield_surface(yield_surface,data_set: DataFrame,path: str,symmetry: bool)
    
    #fit_yield_surface_problem_definition(problem_definition)

    
    
    
    
    