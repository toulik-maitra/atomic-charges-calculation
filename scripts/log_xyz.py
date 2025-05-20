'''
Extracting Optimnized Geometry from .log file after Geometry Optimization in Gaussian 16

Edited by: Toulik Maitra, UC Dvais, 2025
'''

import cclib
from periodictable import elements

# parse the log
data = cclib.io.ccread('mol1.log')

# get the final coordinates and atomic numbers
final_coords = data.atomcoords[-1]    
atomic_numbers = data.atomnos         

# write XYZ for further calculations
natoms = len(atomic_numbers)
with open('optimized.xyz', 'w') as f:
    f.write(f"{natoms}\n")
    f.write("Optimized geometry from Gaussian\n")
    for Z, (x, y, z) in zip(atomic_numbers, final_coords):
        sym = elements[Z].symbol
        f.write(f"{sym} {x:.8f} {y:.8f} {z:.8f}\n")
print("Wrote optimized.xyz")
