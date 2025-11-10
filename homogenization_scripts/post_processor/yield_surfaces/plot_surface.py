# System packages
import numpy as np
from pandas import DataFrame
from math import sin, cos, radians
import scipy # type: ignore
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from ...common_classes.figure_style import FigureStyle


# Local packages
from .general_functions import YieldSurfaces, get_yield_points_form_data_set
from ...messages.messages import Messages

def make_plot_yield_surface(
        yield_surface: YieldSurfaces,
        data_set: DataFrame,
        path: str,
        symmetry: bool) -> Figure:

    style = FigureStyle(linewidth=3, 
                        markersize=12,
                        markeredgewidth = 2,
                        fontsize=20)
    
    fig, axs = plt.subplots(nrows=2, ncols=3) # type: ignore
    fig.set_size_inches(20,(2/3)*20) 
        
    Messages.YieldSurface.creating_plot_at(yield_surface.display_name(), path)
    plot_data_points(axs, data_set, yield_surface.unit_conversion(), symmetry, style) # type: ignore
    plot_surface(axs, yield_surface, style) # type: ignore
    

    
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
        text.set_fontsize(style.fs)
    
    fig.tight_layout()
    fig.savefig(path) # type: ignore

    return fig

def calculate_value_plot(yield_surface: YieldSurfaces, stress_1: float, stress_2: float, index_1: list[int], index_2: list[int]) -> float:
    stress = np.zeros((3,3))

    stress[index_1[0]][index_1[1]] = stress_1
    stress[index_2[0]][index_2[1]] = stress_2

    stress_Voigt = [stress[0][0], stress[1][1], stress[2][2], stress[1][2], stress[0][2], stress[0][1]]

    yield_surface_value = yield_surface.evaluate(stress_Voigt)

    return yield_surface_value


def plot_data_points(axs, yield_points_pandas: DataFrame, unit_conversion: float, symmetry: bool, style: FigureStyle | None = None)-> None: # type: ignore
    yield_points = get_yield_points_form_data_set(yield_points_pandas, unit_conversion)

    number_data_points = np.shape(yield_points)[0]
    max_stress = yield_points.max()

    for data_point in range(number_data_points):
        s_xx = yield_points[data_point][0]
        s_yy = yield_points[data_point][1]
        s_zz = yield_points[data_point][2]
        s_yz = yield_points[data_point][3]
        s_xz = yield_points[data_point][4]
        s_xy = yield_points[data_point][5]

        # axs.plot(s_xx, s_yy, marker='x', color='r')
        filter_value = 0.01

        s_xx_active = abs(s_xx) > filter_value*max_stress
        s_yy_active = abs(s_yy) > filter_value*max_stress
        s_zz_active = abs(s_zz) > filter_value*max_stress
        s_xy_active = abs(s_xy) > filter_value*max_stress
        s_xz_active = abs(s_xz) > filter_value*max_stress
        s_yz_active = abs(s_yz) > filter_value*max_stress

        xx_yy_plot = (s_xx_active or s_yy_active) and (not s_zz_active and not s_xy_active and not s_xz_active)
        xx_zz_plot = (s_xx_active or s_zz_active) and not s_yy_active
        yy_zz_plot = (s_yy_active or s_zz_active) and (not s_xx_active and not s_xz_active)
        xy_xz_plot = (s_xy_active or s_xz_active) and not s_yz_active
        xy_yz_plot = (s_xy_active or s_yz_active) and not s_xz_active
        xz_yz_plot = (s_xz_active or s_yz_active) and not s_xy_active

        if symmetry:
            cl  = style.pt_color if data_point < number_data_points/2 else style.sym_pt_color
        else:
            cl  = style.pt_color

        if xx_yy_plot:
            axs[0][0].plot(s_xx, s_yy, marker='x', markersize=style.ms, mew=style.mew, color=cl, zorder=3) # type: ignore
        
        if xx_zz_plot:
            axs[0][1].plot(s_xx, s_zz, marker='x', markersize=style.ms, mew=style.mew, color=cl, zorder=3) # type: ignore
        
        if yy_zz_plot:
            axs[0][2].plot(s_yy, s_zz, marker='x', markersize=style.ms, mew=style.mew, color=cl, zorder=3) # type: ignore
    
        if xy_xz_plot:
            axs[1][0].plot(s_xy, s_xz, marker='x', markersize=style.ms, mew=style.mew, color=cl, zorder=3) # type: ignore
        
        if xy_yz_plot:
            axs[1][1].plot(s_xy, s_yz, marker='x', markersize=style.ms, mew=style.mew, color=cl, zorder=3) # type: ignore

        if xz_yz_plot: 
            axs[1][2].plot(s_xz, s_yz, marker='x', markersize=style.ms, mew=style.mew, color=cl, zorder=3) # type: ignore


def plot_surface(
        axs, # type: ignore
        yield_surface: YieldSurfaces,
        style: FigureStyle | None = None):
    
    plot_contour_resolution = 200

    plot_combinations = [
        [[[0,0], [1,1]], [[0,0], [2,2]], [[1,1], [2,2]]],
        [[[0,1], [0,2]], [[0,1], [1,2]], [[0,2], [1,2]]]
        ]
    
    plot_labels = [
        [["stress xx", "stress yy"], ["stress xx", "stress zz"], ["stress yy", "stress zz"]],
        [["stress xy", "stress xz"], ["stress xy", "stress yz"], ["stress xz", "stress yz"]]
        ]

    n = yield_surface.display_name()
    plot_titles: list[list[str]] = [
        [f"{n} xx-yy plane", f"{n} xx-zz plane", f"{n} yy-zz plane"],
        [f"{n} xy-xz plane", f"{n} xy-yz plane", f"{n} xz-yz plane"]
        ]

    for plot_x in range(3):
        for plot_y in range(2):
            legends = [] # type: ignore

            if plot_y == 0:
                if plot_x == 0:
                    x_index = 0
                    y_index = 1
                elif plot_x == 1:
                    x_index = 0
                    y_index = 2
                else:
                    x_index = 1
                    y_index = 2
            else:
                if plot_x == 0:
                    x_index = 5
                    y_index = 4
                elif plot_x == 1:
                    x_index = 5
                    y_index = 3
                else:
                    x_index = 4
                    y_index = 3

            extend_factor = 1.25

            magnitude_max_x: float = 0.
            magnitude_max_y: float = 0.

            magnitude_min_x: float = 0.
            magnitude_min_y: float = 0.

            for angle in np.linspace(0, 360, 20):
                stress_search_direction = [0., 0., 0., 0., 0., 0.]

                stress_x = 100 * cos(radians(angle))
                stress_y = 100 * sin(radians(angle))
                
                stress_search_direction[x_index] = stress_x
                stress_search_direction[y_index] = stress_y

                def objective(x: float) -> float:
                    yield_surface_value = yield_surface.evaluate((np.array(stress_search_direction)*x).tolist()) # type: ignore
                    yield_surface_error = (yield_surface_value - 1)**2
                    return yield_surface_error 

                result = scipy.optimize.minimize_scalar(objective, options={'disp': False}, method="Golden") # type: ignore
                # print(result)
                magnitude = abs(result.x) # type: ignore

                magnitude_x = stress_x*magnitude
                magnitude_y = stress_y*magnitude

                if magnitude_x > magnitude_max_x:
                    magnitude_max_x = magnitude_x
                if magnitude_x < magnitude_min_x:
                    magnitude_min_x = magnitude_x
                
                if magnitude_y > magnitude_max_y:
                    magnitude_max_y = magnitude_y
                if magnitude_y < magnitude_min_y:
                    magnitude_min_y = magnitude_y


            x_max = extend_factor*magnitude_max_x
            x_min = extend_factor*magnitude_min_x
            y_max = extend_factor*magnitude_max_y
            y_min = extend_factor*magnitude_min_y

            x = np.linspace(x_min, x_max, plot_contour_resolution) # type: ignore
            y = np.linspace(y_min, y_max, plot_contour_resolution) # type: ignore
            X, Y = np.meshgrid(x, y)  # type: ignore

            Z = np.zeros((plot_contour_resolution, plot_contour_resolution))
            for x_index in range(plot_contour_resolution):
                for y_index in range(plot_contour_resolution):
                    index_1 = plot_combinations[plot_y][plot_x][0]
                    index_2 = plot_combinations[plot_y][plot_x][1]
                    
                    Z[y_index][x_index] = calculate_value_plot(yield_surface,x[x_index], y[y_index], index_1, index_2)  # type: ignore
            
            contour = axs[plot_y][plot_x].contour(X, Y, Z, levels=[1], linestyles='dashed', linewidths=style.lw, colors=[style.ln_color]) # type: ignore

            axs[plot_y][plot_x].clabel(contour, fmt={1:""})  # type: ignore

            axs[plot_y][plot_x].grid(which="both", visible=True)  # type: ignore
            axs[plot_y][plot_x].set_title(plot_titles[plot_y][plot_x]) # type: ignore
            axs[plot_y][plot_x].set_xlabel(f"{plot_labels[plot_y][plot_x][0]} [{yield_surface.unit_name()}]") # type: ignore
            axs[plot_y][plot_x].set_ylabel(f"{plot_labels[plot_y][plot_x][1]} [{yield_surface.unit_name()}]") # type: ignore
