# Computational Chemistry Workflow

This repository contains scripts and instructions for conducting computational chemistry analyses using ASE (Atomic Simulation Environment), Gaussian, and Chargemol. The workflow includes molecular extraction, geometry optimization, wavefunction calculations, and charge/bond order analysis.

## Workflow Overview

1. Extract a single molecule from a unit cell structure
2. Perform geometry optimization using Gaussian
3. Extract optimized geometry for wavefunction calculations
4. Calculate atomic charges and bond orders using Chargemol

## Prerequisites

- Python 3.6+
- ASE (Atomic Simulation Environment)
- Gaussian 16 (or compatible version)
- Chargemol

## Installation

### ASE Installation

```bash
pip install ase
```

### Chargemol Installation

1. Download Chargemol from [SourceForge](https://sourceforge.net/projects/ddec/)
2. Extract and set up the environment:

```bash
# Extract the downloaded zip file
unzip chargemol.zip

# Create directory structure in your home directory
mkdir -p $HOME/bin

# Copy the executable and make it executable
cp /path/to/extracted/Chargemol_09_26_2017_linux_parallel $HOME/bin/
chmod +x $HOME/bin/Chargemol_09_26_2017_linux_parallel

# Copy atomic densities to bin directory
cp -r /path/to/extracted/atomic_densities/ $HOME/bin/
```

## Usage Instructions

### 1. Extract One Molecule from Unit Cell

Create a file named `one_molecule.py` with the following content:

```python
from ase import io
import numpy as np

# Read the unit cell structure
unitcell = io.read('path/to/unitcell_file.cif')  # Adjust file format as needed

# Extract a single molecule (this will depend on your specific structure)
# Method 1: Using connectivity
from ase.build import connected_indices
atoms_indices = connected_indices(unitcell, 0)  # Start from atom index 0
molecule = unitcell[atoms_indices]

# Method 2: Alternative approach for specific cases
# Define a center atom and select atoms within a certain radius
# center_atom_index = 0
# cutoff_radius = 3.0  # Adjust as needed (in Å)
# distances = unitcell.get_distances(center_atom_index, range(len(unitcell)), mic=True)
# molecule_indices = np.where(distances < cutoff_radius)[0]
# molecule = unitcell[molecule_indices]

# Verify the number of atoms in the extracted molecule
expected_atoms = 42  # Replace with the expected number of atoms in your molecule
if len(molecule) != expected_atoms:
    print(f"Warning: Extracted molecule has {len(molecule)} atoms, expected {expected_atoms}")
else:
    print(f"Successfully extracted molecule with {len(molecule)} atoms")

# Write the molecule to a file
io.write('molecule.xyz', molecule)
```

Run the script:

```bash
python scripts/one_molecule.py
```

### 2. Create Gaussian Input for Geometry Optimization

Create a file named `create_gaussian_input.py` in the scripts directory:

```python
from ase import io
from ase.calculators.gaussian import Gaussian

# Read the extracted molecule
molecule = io.read('molecule.xyz')

# Set up Gaussian calculator for geometry optimization
calc = Gaussian(
    mem='8GB',
    nprocshared=8,
    label='gaussian/geom_opt',  # Updated path
    method='B3LYP',
    basis='6-31G(d)',
    opt='Tight',
    scf='QC',
    chk='gaussian/geom_opt.chk'  # Updated path
)

molecule.calc = calc

# Write the Gaussian input file
calc.write_input(molecule)
```

Run the script to generate the Gaussian input file:

```bash
python scripts/create_gaussian_input.py
```

Submit the job to Gaussian:

```bash
cd gaussian
g16 < geom_opt.com > geom_opt.log
cd ..
```

### 3. Extract Optimized Geometry from Gaussian Log File

Create a script named `extract_optimized_geometry.py` in the scripts directory:

```python
from ase import io
from ase.io.gaussian import read_gaussian_out

# Read the optimized geometry from the log file
optimized_molecule = read_gaussian_out('gaussian/geom_opt.log', index=-1)

# Write the optimized geometry to XYZ format
io.write('gaussian/optimized_molecule.xyz', optimized_molecule)

print(f"Successfully extracted optimized geometry with {len(optimized_molecule)} atoms")
```

Run the script:

```bash
python scripts/extract_optimized_geometry.py
```

### 4. Create Wavefunction Calculation Job

Create a script named `create_wfx_job.py` in the scripts directory:

```python
from ase import io
from ase.calculators.gaussian import Gaussian

# Read the optimized molecule
optimized_molecule = io.read('gaussian/optimized_molecule.xyz')

# Set up Gaussian calculator for wavefunction calculation
calc = Gaussian(
    mem='16GB',
    nprocshared=16,
    label='gaussian/wfx_calc',  # Updated path
    method='B3LYP',  # Use the same level of theory as optimization
    basis='6-311++G(d,p)',  # Typically a larger basis set for wavefunction analysis
    output='wfx',  # Request WFX file output
    pop='full',
    density='current',
    scf='QC'
)

optimized_molecule.calc = calc

# Write the Gaussian input file
calc.write_input(optimized_molecule)

# Modify the generated com file to ensure .wfx file generation
with open('gaussian/wfx_calc.com', 'r') as file:  # Updated path
    content = file.readlines()

# Add WFX file generation instruction if needed
modified_content = []
for line in content:
    modified_content.append(line)
    if line.strip() == '':  # Find the first blank line after route section
        # Add the wfx filename specification
        modified_content.append('output.wfx\n\n')
        break

with open('gaussian/wfx_calc.com', 'w') as file:  # Updated path
    file.writelines(modified_content)

print("Created wavefunction calculation input file: gaussian/wfx_calc.com")
```

Run the script and submit the job:

```bash
python scripts/create_wfx_job.py
cd gaussian
g16 < wfx_calc.com > wfx_calc.log
cd ..
```

### 5. Use Chargemol to Calculate Atomic Charges and Bond Orders

#### Prepare the job_control.txt file

Create a file named `job_control.txt` in the gaussian directory with the following content:

```
<atomic densities directory complete path>
$HOME/bin/atomic_densities/

<charge type>
DDEC6

<compute BOs>
.true.

<input filename>
output.wfx

<net charge>
0
```

Adjust the `<net charge>` value according to your molecule.

#### Run Chargemol

```bash
cd gaussian  # Change to the gaussian directory where the wfx file is located
cp /path/to/job_control.txt ./
$HOME/bin/Chargemol_09_26_2017_linux_parallel
cd ..
```

## Project Structure

```
.
├── README.md
├── scripts/
│   ├── one_molecule.py
│   ├── create_gaussian_input.py
│   ├── extract_optimized_geometry.py
│   └── create_wfx_job.py
├── gaussian/
│   ├── geom_opt.com
│   ├── geom_opt.log
│   ├── geom_opt.chk
│   ├── optimized_molecule.xyz
│   ├── wfx_calc.com
│   ├── wfx_calc.log
│   ├── output.wfx
│   └── job_control.txt
└── atomic_densities/  # Optional: If you want to keep atomic densities in project

## Output Analysis

After running Chargemol, you'll find several output files in the gaussian directory:

- `DDEC6_even_tempered_net_atomic_charges.xyz`: Contains the optimized geometry with DDEC6 charges
- `DDEC_atomic_spinmoments.xyz`: Contains atomic spin moments
- `DDEC6_bond_orders.csv`: Contains bond order values between atoms

You can analyze these files to understand the electronic structure and bonding in your molecule.

## Tips for Troubleshooting

- **Molecule extraction issues**: Adjust the connectivity algorithm or cutoff radius
- **Gaussian errors**: Check the log file for error messages
- **Chargemol errors**: Ensure paths in job_control.txt are correct
- **Memory issues**: Adjust memory allocations in Gaussian input files

## Additional Resources

- [ASE Documentation](https://wiki.fysik.dtu.dk/ase/)
- [Gaussian Documentation](https://gaussian.com/man/)
- [Chargemol/DDEC6 Documentation](https://github.com/qzhu2017/DDEC6)