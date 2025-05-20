'''
Extracting one molecule from Unit Cell

Edited by: Toulik Maitra, UC Dvais, 2025
'''

import os
import ase.io
import numpy as np
import networkx as nx
from ase.neighborlist import natural_cutoffs, neighbor_list
from ase.calculators.gaussian import Gaussian

def find_molecules(atoms):
    """
    Build a connectivity graph (only within the cell, no PBC‐wrapped bonds)
    and return a list of sets of atom indices, one per molecule.
    """
    i, j, S = neighbor_list(
        quantities='ijS',
        a=atoms,
        cutoff=natural_cutoffs(atoms)
    )
    G = nx.Graph()
    for a, b, s in zip(i, j, S):
        if sum(s) == 0:
            G.add_edge(int(a), int(b))
    return list(nx.connected_components(G))


def extract_and_write_monomer(
    cif_path: str,
    molecule_index: int = 0,
    gaussian_method: str = 'B3LYP',
    gaussian_basis: str  = '6-31G(d)',
    gaussian_mem: str    = '16GB',
    gaussian_nproc: int  = 16,
    charge: int = 0,
    multiplicity: int = 1,
    out_label: str   = 'monomer'
):
    # Read the CIF (unit cell only)
    atoms = ase.io.read(cif_path)
    # Identify disconnected fragments
    fragments = find_molecules(atoms)
    try:
        frag = fragments[molecule_index]
    except IndexError:
        raise ValueError(f"Only {len(fragments)} molecules found; "
                         f"cannot pick index {molecule_index}")
    # Extract that molecule
    mol = atoms[list(frag)]
    mol.set_pbc((False, False, False))
    # Write out an .xyz so you can inspect it:
    xyz_path = f"{out_label}.xyz"
    ase.io.write(xyz_path, mol)
    print(f"Wrote XYZ → {xyz_path}")

    # 6) Set up a Gaussian input
    calc = Gaussian(
        label        = out_label,
        method       = gaussian_method,
        basis        = gaussian_basis,
        mem          = gaussian_mem,
        nprocshared  = gaussian_nproc,
        charge       = charge,
        multiplicity = multiplicity
    )
    mol.set_calculator(calc)
    # 7) Write the Gaussian .com/.gjf file
    calc.write_input(mol)
    print(f"Wrote Gaussian input → {out_label}.com")


if __name__ == '__main__':
    # Example usage:
    extract_and_write_monomer(
        cif_path          = 'anthracene.cif',
        molecule_index    = 0,          # first molecule in the cell
        gaussian_method   = 'B3LYP',
        gaussian_basis    = '6-31G(d)',
        gaussian_mem      = '16GB',
        gaussian_nproc    = 16,
        charge            = 0,
        multiplicity      = 1,
        out_label         = 'mol1'
    )
