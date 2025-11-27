# System packages
import sys
import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
from pathlib import Path
import pickle
# Local-packages
from homogenization_scripts.post_processor.fit_yield_surface import fit_yield_surface
from homogenization_scripts.post_processor.yield_surfaces.yield_surface_template import YieldSurfaces
from homogenization_scripts.post_processor.yield_surfaces.general_functions import read_yield_points
from homogenization_scripts.post_processor.yield_surfaces.plot_surface import plot_data_points,plot_surface,make_plot_yield_surface
from homogenization_scripts.common_classes.figure_style import FigureStyle

def set_xy_limits(fig,axs):
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

    fig, axs = plt.subplots(nrows=2, ncols=3) 
    fig.set_size_inches(20,(2/3)*20) 
        
    plot_data_points(axs, data_set1, yield_surface1.unit_conversion(), symmetry1, style1)
    plot_data_points(axs, data_set2, yield_surface2.unit_conversion(), symmetry2, style2)
    plot_surface(axs, yield_surface1, style1) 
    plot_surface(axs, yield_surface2, style2) 
    
    set_xy_limits(fig,axs)

    for text in fig.findobj(match=plt.Text):
        text.set_fontsize(style1.fs)
    
    fig.tight_layout()
    fig.savefig(path) # type: ignore

    return fig


def faded(color, factor=0.5):
    h, s, v = mcolors.rgb_to_hsv(mcolors.to_rgb(color))
    return mcolors.hsv_to_rgb((h, s*factor, v))

def make_evolution_plot_yield_surface(
        yield_surfaces,
        yield_points,
        path: str,
        symmetry: bool,
        style
        ):

    fig, axs = plt.subplots(nrows=2, ncols=3) 
    fig.set_size_inches(20,(2/3)*20) 
        
    for i in range(len(yield_surfaces)):
        plot_surface(axs, yield_surfaces[i], style) 
        
    for i in range(len(yield_points)):
        plot_data_points(axs, yield_points[i], yield_surfaces[i].unit_conversion(), symmetry, style)
    
    set_xy_limits(fig,axs)

    for text in fig.findobj(match=plt.Text):
        text.set_fontsize(style.fs)
    
    fig.tight_layout()
    fig.savefig(path) 

    return fig

def evolution_yield_loci(pth, config):
    parent = pth.parent

    database_pths       = [Path(a) for a in config['yield_point_databases']]
    yld_pths            = [Path(a) for a in config['yield_function_files']]

    filenames       = [p.name for p in database_pths]
    stems           = [p.stem for p in database_pths]

    output_base = "outputs_evolution/"
    output_pths = [parent / (output_base+"parameters/parameters_" + name) for name in filenames]
    plot_pths   = [parent / (output_base+"plots/plot_" + stem + ".png") for stem in stems]
  
    parameter_dir    = [p.parent for p in output_pths]
    plot_dir         = [p.parent for p in plot_pths]
    yld_dir          = [p.parent for p in yld_pths]
    
    symmetry           = config['yield_point_symmetry']

    c1 = config['colour'][0]
    c3 = config['colour'][1]
    
    style = FigureStyle(linewidth=config['style'][0], 
                        markersize=config['style'][1],
                        markeredgewidth = config['style'][2],
                        fontsize=config['style'][3],
                        pt_color=c1,
                        sym_pt_color=c1,
                        ln_color=c3)
    
    

    for p in parameter_dir:
        Path(p).mkdir(parents=True, exist_ok=True)
    for p in plot_dir:
        Path(p).mkdir(parents=True, exist_ok=True)
    for p in yld_dir:
        Path(p).mkdir(parents=True, exist_ok=True)
        
    yield_point_databases = []
    for i in range(len(database_pths)):
        database = read_yield_points(database_pths[i], symmetry)
        yield_point_databases.append(database)

    yield_surfaces = []
    if not config['plot_only']:
        for i in range(len(database_pths)):
            yield_surface_name = config['yield_surface_type']
            yield_stress_ref   = float(config['reference_yield_stress'])
            dataset_path       = str(database_pths[i])
            output_path        = output_pths[i]
            plot_path          = plot_pths[i]
            
            bounds = config.get("bounds_CPB", None)

                
            yield_surface   = fit_yield_surface(yield_surface_name, 
                                             yield_stress_ref, 
                                             dataset_path, 
                                             output_path, 
                                             plot_path, 
                                             symmetry,
                                             bounds)
            yield_surfaces.append(yield_surface)
    else:
        for i in range(len(yld_pths)):
            print("Reading yield surface from " + str(yld_pths[i]))
            with open(yld_pths[i], "rb") as f:
                yield_surface = pickle.load(f)
            yield_surfaces.append(yield_surface)
    
    evo_plot_pth = plot_dir[0] / "evolution.png"
    print("Saving yield surface evolution plot at " + str(evo_plot_pth))
    make_evolution_plot_yield_surface(
        yield_surfaces,
        yield_point_databases,
        evo_plot_pth,
        symmetry,
        style)
                
            
        
def compare_yield_loci(pth, config):
    database_pths_str   = config['yield_point_databases']
    database_pths       = [Path(a) for a in database_pths_str]
    yld_pths_str        = config['yield_function_files']
    yld_pths            = [Path(a) for a in yld_pths_str]


    parent = pth.parent
    filenames       = [p.name for p in database_pths]
    stems           = [p.stem for p in database_pths]
        
    output_base = "outputs_comparison/"
    output_pths = [parent / (output_base+"parameters/parameters_" + name) for name in filenames]
    plot_pths   = [parent / (output_base+"plots/plot_" + stem + ".png") for stem in stems]
    #yld_pths    = [parent / (output_base+"yield_surfaces/ys_" + stem + ".pkl") for stem in stems]
    #yld_pths    = [p.with_suffix(".pkl") for p in output_pths]

    parameter_dir    = [p.parent for p in output_pths]
    plot_dir         = [p.parent for p in plot_pths]
    yld_dir          = [p.parent for p in yld_pths]
        
    for p in parameter_dir:
        Path(p).mkdir(parents=True, exist_ok=True)
    for p in plot_dir:
        Path(p).mkdir(parents=True, exist_ok=True)
    for p in yld_dir:
        Path(p).mkdir(parents=True, exist_ok=True)

    c1 = config['colour'][0]
    c2 = config['colour'][1]
    c3 = config['colour'][2]
    
    alpha = config['alpha']
    c1b = faded(c1, alpha)
    c2b = faded(c2, alpha)
    c3b = faded(c3, alpha)
    
    yield_surface_name = config['yield_surface_type']
    #yield_surface_name = 'Hill'
    yield_stress_ref1 = float(config['reference_yield_stress'][0])
    dataset_path1 = str(database_pths[0])
    
    output_path1 = output_pths[0]
    
    plot_path1 = plot_pths[0]
    
    symmetry1 = config['yield_point_symmetry'][0]
    
    bounds = config.get("bounds_CPB", None)
    if bounds is None:
        bounds1 = None
        bounds2 = None
    else:
        bounds1 = bounds[0]
        bounds2 = bounds[1]
            
    data_set1 = read_yield_points(dataset_path1, symmetry1)
    
    style1 = FigureStyle(linewidth=config['style'][0][0], 
                        markersize=config['style'][0][1],
                        markeredgewidth = config['style'][0][2],
                        fontsize=config['style'][0][3],
                        pt_color=c1,
                        sym_pt_color=c1,
                        ln_color=c3)
        
    if not config['plot_only']:
        yield_surface1   = fit_yield_surface(yield_surface_name, 
                                         yield_stress_ref1, 
                                         dataset_path1, 
                                         output_path1, 
                                         plot_path1, 
                                         symmetry1,
                                         bounds1)
        # with open(yld_pths[0], "wb") as f:
        #     pickle.dump(yield_surface1, f)
    else:
        print('Plot_only mode active. Skip yield surface fitting. Load yield surface 1 from file...')
        with open(yld_pths[0], "rb") as f:   # open in *binary read* mode
            yield_surface1 = pickle.load(f)
                
        

    #if len(config['yield_point_databases'])==1:
    fig              = make_plot_yield_surface(yield_surface1, data_set1, plot_path1, symmetry1, style1)

    if len(config['yield_point_databases'])==2:
        dataset_path2       = str(database_pths[1])
        yield_stress_ref2   = float(config['reference_yield_stress'][1])
        output_path2        = output_pths[1]
        plot_path2          = plot_pths[1]
        plot_path3          = plot_dir[0] / 'comparison.png'
        symmetry2           = config['yield_point_symmetry'][1]
        data_set2           = read_yield_points(dataset_path2, symmetry2)
        style2              = FigureStyle(linewidth=config['style'][1][0], 
                                          markersize=config['style'][1][1],
                                          markeredgewidth = config['style'][1][2],
                                          fontsize=config['style'][1][3],
                                          pt_color=c1b,
                                          sym_pt_color=c1b,
                                          ln_color=c3b)
        
        if not config['plot_only']:
            yield_surface2      = fit_yield_surface(yield_surface_name, 
                                                    yield_stress_ref2, 
                                                    dataset_path2, 
                                                    output_path2, 
                                                    plot_path2, 
                                                    symmetry2, 
                                                    bounds2)
            # with open(yld_pths[1], "wb") as f:
            #     pickle.dump(yield_surface2, f)
        else:
            print('Plot_only mode active. Skip yield surface fitting. Load yield surface 2 from file...')
            with open(yld_pths[1], "rb") as f:   
                yield_surface2 = pickle.load(f)
        fig              = make_plot_yield_surface(yield_surface2, data_set2, plot_path2, symmetry2, style1)

        fig = make_comparison_plot_yield_surface(yield_surface1,yield_surface2, 
                                                 data_set1,data_set2, plot_path3, 
                                                 symmetry1, symmetry2,
                                                 style1,style2)


def main():
    if len(sys.argv) == 1:
        pth = Path("compare_results/visualization_settings.yaml")
    elif len(sys.argv) == 2:        
        pth = Path(sys.argv[1])
    else:
        sys.exit('Invalid number of arguments. Specify path to visualization config or leave empty to run with default config.')
    # pth = "compare_results/visualization_settings.yaml"
    with open(pth, "r") as f:
        config = yaml.safe_load(f)
    
    
    if config['mode'] == 'comparison':
        config = config['comparison']
        compare_yield_loci(pth, config)
        
    elif config['mode'] == 'evolution':
        config = config['evolution']
        evolution_yield_loci(pth, config)
    
if __name__ == "__main__":
    main() 
        