# From example given by Damask:
# https://damask-multiphysics.org/documentation/examples/Voronoi_tessellation.html

import damask
import numpy as np

# Dimensions for grid
size = np.ones(3)*1e-5
cells = [50, 50, 50]
N_grains = 50

# Material properties to process
base_material = "example_base_material.yaml"
processed_material = "example_material.yaml"

# Create a random grid with N_grains unique grains
seeds = damask.seeds.from_random(size,N_grains,cells)
grid = damask.GeomGrid.from_Voronoi_tessellation(cells,size,seeds)
grid.save(f'Polycrystal_{N_grains}_{cells[0]}x{cells[1]}x{cells[2]}')
grid

# Create a dummy homogenization
config_material = damask.ConfigMaterial()
config_material['homogenization']['dummy']  = {'N_constituents':1,'mechanical':{'type':'pass'}}
config_material['phase']['A']               = damask.ConfigMaterial.load(base_material)

# Create random orientations for all the N_grains
O_A = damask.Rotation.from_random(shape=N_grains)

# Store the grain properties to the file.
config_material = config_material.material_add(homogenization='dummy',phase='A',O=O_A)
config_material.save(processed_material)
