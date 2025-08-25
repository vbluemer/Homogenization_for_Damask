# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 15:53:55 2025

@author: BlumerVM
"""
#import os
#import pickle
import matplotlib.pyplot as plt
import numpy as np

# from homogenization_scripts.post_processor.yield_surfaces.plot_surface import plot_surface
# from homogenization_scripts.common_classes.figure_style import FigureStyle


def vec_to_tens_stress(vector):
    tensor = np.empty((3,3))
    tensor[0][0] = vector[0][0] 
    tensor[1][1] = vector[1][0]
    tensor[2][2] = vector[2][0] 
    tensor[1][2] = vector[3][0]
    tensor[0][2] = vector[4][0]
    tensor[0][1] = vector[5][0]
    return tensor

def compute_f(sigma, params):
    k,a,C,sigma_yield_ref = params
        
    sigma_m = np.sum(sigma[:3])/3
    sigma_hydro = np.array([sigma_m,sigma_m,sigma_m,0,0,0]).reshape(-1, 1)
    sigma_dev = sigma - sigma_hydro

    Sigma_0 = np.matmul(C[0],sigma_dev)
    Sigma_1 = np.matmul(C[1],sigma_dev)

    Sigma_0_tensor = vec_to_tens_stress(Sigma_0)
    Sigma_1_tensor = vec_to_tens_stress(Sigma_1)

    Sigma_eigen_0 = np.linalg.eig(Sigma_0_tensor)[0]
    Sigma_eigen_1 = np.linalg.eig(Sigma_1_tensor)[0]


    sigma_equiv = ((abs(Sigma_eigen_0[0]) - k[0]*Sigma_eigen_0[0])**a +
         (abs(Sigma_eigen_0[1]) - k[0]*Sigma_eigen_0[1])**a +
         (abs(Sigma_eigen_0[2]) - k[0]*Sigma_eigen_0[2])**a +
         (abs(Sigma_eigen_1[0]) - k[1]*Sigma_eigen_1[0])**a +
         (abs(Sigma_eigen_1[1]) - k[1]*Sigma_eigen_1[1])**a +
         (abs(Sigma_eigen_1[2]) - k[1]*Sigma_eigen_1[2])**a)
    
    
    f = sigma_equiv - sigma_yield_ref**a
    return f

def plot_yld(data,params):
    k,a,C,sigma_yield_ref = params

    v_absmax = np.max(np.abs(data))  # Find the largest absolute value
    
    x = np.arange(data.shape[1])
    y = np.arange(data.shape[0])
    X, Y = np.meshgrid(x, y)
    
    x_flat = X.ravel()
    y_flat = Y.ravel()
    values = data.ravel()  
    
    plt.figure(figsize=(6, 6))
    sc = plt.scatter(x_flat, y_flat, c=values, cmap='seismic', vmin=-v_absmax, vmax=v_absmax)
    plt.colorbar(sc, label='Value')
    plt.title(f"k0 = {k[0]:.4f} and k1 = {k[1]:.4f}")
    plt.axis('equal')
    ax = plt.gca()
    indices = list(range(num_points))
    spaced = indices[::5]
    xtick_labels = [f'{x_grid[i]:.0f}' for i in spaced]
    ytick_labels = [f'{y_grid[i]:.0f}' for i in spaced]
    ax.set_xticks(spaced)
    ax.set_yticks(spaced)
    
    ax.set_xticklabels(xtick_labels)
    ax.set_yticklabels(ytick_labels)
    
    plt.show()
    



    
k = [np.float64(-7.495616832859287e-08), np.float64(7.205866505220338e-08)]
a = 2
C = [np.array([[0.81798149, 1.43734195, 0.47608124, 0.        , 0.        , 0.        ],
               [1.43734195, 0.67132493, 0.94487546, 0.        , 0.        , 0.        ],
               [0.47608124, 0.94487546, 1.65375627, 0.        , 0.        , 0.        ],
               [0.        , 0.        , 0.        , 0.84305171, 0.        , 0.        ],
               [0.        , 0.        , 0.        , 0.        , 0.92645652, 0.        ],
               [0.        , 0.        , 0.        , 0.        , 0.        , 0.74501454]]), 
     np.array([[0.81797973, 1.43734182, 0.47608234, 0.        , 0.        , 0.        ],
               [1.43734182, 0.67132552, 0.94487597, 0.        , 0.        , 0.        ],
               [0.47608234, 0.94487597, 1.65375612, 0.        , 0.        , 0.        ],
               [0.        , 0.        , 0.        , 0.84305139, 0.        , 0.        ],
               [0.        , 0.        , 0.        , 0.        , 0.92645637, 0.        ],
               [0.        , 0.        , 0.        , 0.        , 0.        , 0.7450146 ]])]
sigma_yield_ref = 420
params_0 = [k,a,C,sigma_yield_ref]


k = [np.float64(0.8454618175445321), np.float64(0.8337964289980367)]
a = 2
C = [np.array([[ 1.05856698,  1.62119945,  1.46839695,  0.        ,  0.        ,  0.        ],
               [ 1.62119945,  1.921244  , -0.25644777,  0.        ,  0.        ,  0.        ],
               [ 1.46839695, -0.25644777,  0.16593796,  0.        ,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  1.88389123,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  0.        ,  2.26826276,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,  0.74385392]]), 
     np.array([[-0.46644409,  1.42347179,  0.98279486,  0.        ,  0.        ,  0.        ],
               [ 1.42347179,  0.48732292,  0.68088438,  0.        ,  0.        ,  0.        ],
               [ 0.98279486,  0.68088438,  2.87375777,  0.        ,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  1.07866334,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  0.        , -0.73231245,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,  1.7755354 ]])]
sigma_yield_ref = 1e3
params_1 = [k,a,C,sigma_yield_ref]



num_points = 26
max_stress = 600
x_grid = np.linspace(-max_stress, max_stress, num_points)
y_grid = np.linspace(-max_stress, max_stress, num_points)
tickfactor = max_stress/num_points

f0_grid = np.empty([num_points,num_points])
for e1,x in enumerate(x_grid):
    for e2,y in enumerate(y_grid):
        sigma = np.array([x,y,0,0,0,0]).reshape(-1, 1)
        f = compute_f(sigma, params_0)
        f0_grid[e1,e2] = f
        
f1_grid = np.empty([num_points,num_points])
for e1,x in enumerate(x_grid):
    for e2,y in enumerate(y_grid):
        sigma = np.array([x,y,0,0,0,0]).reshape(-1, 1)
        f = compute_f(sigma, params_1)
        f1_grid[e1,e2] = f



plot_yld(f0_grid,params_0)
plot_yld(f1_grid,params_1)







# np.set_printoptions(linewidth=200)

# workdir = 'troubleshoot'
# os.chdir(workdir)

# with open("yield_surf.pkl", "rb") as f:
#      yld_surf = pickle.load(f)

# if 0:
#     style = FigureStyle(linewidth=3, 
#                         markersize=12,
#                         markeredgewidth = 2,
#                         fontsize=20)
    
#     fig, axs = plt.subplots(nrows=2, ncols=3) # type: ignore
#     fig, axs = plt.subplots(nrows=2, ncols=3) # type: ignore
#     fig.set_size_inches(20,(2/3)*20)  
        
#     plot_surface(axs, yld_surf, style)
    
    
#     fig.tight_layout()
#     fig.savefig('inspect_yld_surf.png') # type: ignore

# sigma = np.array([-420,0,0,0,0,0]).reshape(-1, 1)

# sigma_m = np.sum(sigma[:3])/3
# sigma_hydro = np.array([sigma_m,sigma_m,sigma_m,0,0,0]).reshape(-1, 1)
# sigma_dev = sigma - sigma_hydro

# C_0 = yld_surf.c[0]
# C_1 = yld_surf.c[1]

# k_0 =  yld_surf.k[0]
# k_1 =  yld_surf.k[1]

# Sigma_0 = np.matmul(C_0,sigma_dev)
# Sigma_1 = np.matmul(C_1,sigma_dev)

# Sigma_0_tensor = vec_to_tens_stress(Sigma_0)
# Sigma_1_tensor = vec_to_tens_stress(Sigma_1)

# Sigma_eigen_0 = np.linalg.eig(Sigma_0_tensor)[0]
# Sigma_eigen_1 = np.linalg.eig(Sigma_1_tensor)[0]

# a = yld_surf.a

# f = ((abs(Sigma_eigen_0[0]) - k_0*Sigma_eigen_0[0])**a +
#      (abs(Sigma_eigen_0[1]) - k_0*Sigma_eigen_0[1])**a +
#      (abs(Sigma_eigen_0[2]) - k_0*Sigma_eigen_0[2])**a +
#      (abs(Sigma_eigen_1[0]) - k_1*Sigma_eigen_1[0])**a +
#      (abs(Sigma_eigen_1[1]) - k_1*Sigma_eigen_1[1])**a +
#      (abs(Sigma_eigen_1[2]) - k_1*Sigma_eigen_1[2])**a)
     
# # z400, 1.069.363.8629745692
# # -z400, 1.069.319.2135079533
# breakpoint()
# # x420,  971.443
# # x-420, 971.485
# #breakpoint()












