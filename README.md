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

The script `scripts/one_molecule.py` handles the extraction of a single molecule from a unit cell structure. It provides two methods:
- Using connectivity starting from a specific atom
- Using distance-based selection from a center atom

Run the script:

```bash
python scripts/one_molecule.py
```

### 2. Create Gaussian Input for Geometry Optimization

The script `scripts/create_gaussian_input.py` creates a Gaussian input file for geometry optimization using B3LYP/6-31G(d) level of theory.

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

The script `scripts/extract_optimized_geometry.py` extracts the optimized geometry from the Gaussian output file and saves it in XYZ format.

Run the script:

```bash
python scripts/extract_optimized_geometry.py
```

### 4. Create Wavefunction Calculation Job

The script `scripts/create_wfx_job.py` prepares a Gaussian input file for wavefunction calculation using B3LYP/6-311++G(d,p) level of theory and generates a WFX file for charge analysis.

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