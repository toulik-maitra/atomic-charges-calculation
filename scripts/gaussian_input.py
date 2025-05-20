'''
Gaussian 16 input file generation in a template

Edited by: Toulik Maitra, UC Dvais, 2025
'''

from ase.io import read
from ase.calculators.gaussian import Gaussian

# 1) Read your optimized geometry
atoms = read('optimized.xyz')  

# 2) Attach a Gaussian calculator
calc = Gaussian(
    label        = 'job',
    method       = 'B3LYP',
    basis        = '6-31G(d)',
    mem          = '8GB',
    nprocshared  = 16,
    charge       = 0,
    multiplicity = 1
)
atoms.set_calculator(calc)

# 3) Write the Gaussian input
calc.write_input(atoms)  
print("Wrote job.com")
