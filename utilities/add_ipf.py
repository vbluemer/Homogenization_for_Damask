# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 11:39:26 2025

@author: BlumerVM
"""

import damask
import numpy as np

geom = 'Polycrystal_10_32x32x32.vti'        # path for geometry file
material_config = 'titanium_assigned.yaml'    # path for material.yaml

v = damask.VTK.load(geom)
material_ID = v.get(label='material').flatten()

ma = damask.ConfigMaterial.load(material_config)

phases = list(ma['phase'].keys())
info = []

for m in ma['material']:
    c = m['constituents'][0]
    phase = c['phase']
    info.append({'phase':   phase,
                 'phaseID': phases.index(phase),
                 'lattice': ma['phase'][phase]['lattice'],
                 'O':       c['O'],
                })
    
l = np.array([0,0,1])                            # lab frame direction for IPF

IPF = np.ones((len(material_ID),3),np.uint8)
for i,data in enumerate(info):
    IPF[np.where(material_ID==i)] = \
    np.uint8(damask.Orientation(data['O'],lattice=data['lattice']).IPF_color(l)*255)
    
v = v.set(f'IPF_{l}',IPF)

p   = np.array([d['phase'] for d in info])
pid = np.array([d['phaseID'] for d in info])
v = v.set(label='phase',data=p[material_ID],info='phase name')
v = v.set(label='phaseID',data=pid[material_ID],info='phase ID')

v.save(geom.removesuffix('.vti')+'_IPF.vti')
