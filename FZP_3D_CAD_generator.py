# RSoft 3D Multi-Diffraction Lens Generation Script v0.8 Modified
# Copyright (c)2019 Synopsys, Inc. All Rights Reserved.

import sys
import rsoft.rspytools as rspy
from math import *
from rstools import *
from numpy import *

#########################################################################################################
# Inputs

# Output Prefix
prefix = 'menon'

# Design Parameters
F = 10                    # Lens Focal Length [um]
NA = 0.99                 # Lens Numerical Aperture
Lambda = 0.647            # Wavelength [um]
Pitch = 0.3               # Pitch of unit cell [um]
N0 = 1.5039               # Refractive index of the lens at design wavelength
Dx = 0.05                 # Grid size

D = 100  # Total diameter [um]

# Load ring heights from file
ring_heights_file = 'ring_heights.txt'  # Change to the actual file path if different
with open(ring_heights_file, 'r') as file:
    # Read the file, clean the string, and convert each value to float
    heights_string = file.read().strip().strip('[]')
    # Split by commas and remove any trailing spaces or other characters
    ring_heights = [float(height.strip().replace(',', '')) for height in heights_string.split() if height.strip()]

# Set L0 to the maximum height from the predefined ring heights
L0 = max(ring_heights)

# Number of rings is determined by the length of the predefined heights list
NR = len(ring_heights)

# Desired maximum radius
max_radius = 50  # [um]

# Generate a list of radii evenly distributed between 0 and max_radius with size NR
ring_radii = linspace(0, max_radius, NR)

# Calculate the ring widths based on the difference between consecutive radii
ring_widths = [ring_radii[i + 1] - ring_radii[i] for i in range(NR - 1)]
ring_widths.append(ring_radii[-1] - ring_radii[-2])  # Ensure the last width is correct

#########################################################################################################
# Material Properties

# Material and background refractive indices
mymat_nreal = 1.5039      # Real part of the refractive index of the material
mymat_nimag = 0           # Imaginary part of the refractive index (assumed to be zero for non-absorptive materials)
background_index = 1.0    # Refractive index of the background (e.g., air)

# Calculate delta (index contrast)
delta = mymat_nreal - background_index  # Delta represents the refractive index difference
deltashould = delta

#########################################################################################################

# Create .ind File
ind_file = RSoftCircuit()

#########################################################################################################
# Set Symbols In .ind File

# Design Symbols (set for record-keeping only, these symbols do not change structure)
ind_file.set_symbol('alpha', 0)
ind_file.set_symbol('background_index', background_index)
ind_file.set_symbol('cover_index', 1)
ind_file.set_symbol('delta', deltashould)  # Set delta to the calculated index contrast
ind_file.set_symbol('dimension', 3)
ind_file.set_symbol('eim', 0)
ind_file.set_symbol('fdtd_bc_bottom', 'FDTD_BC_SYMMETRIC')
ind_file.set_symbol('fdtd_bc_left', 'FDTD_BC_SYMMETRIC')
ind_file.set_symbol('free_space_wavelength', Lambda)
ind_file.set_symbol('height', 'width')
ind_file.set_symbol('k0', '(2*pi)/free_space_wavelength')
ind_file.set_symbol('launch_type', 'LAUNCH_RECTANGLE')
ind_file.set_symbol('launch_theta', 180)
ind_file.set_symbol('radial', 1)
ind_file.set_symbol('sim_tool', 'ST_FULLWAVE')
ind_file.set_symbol('width', Pitch)
ind_file.set_symbol('boundary_max', max_radius + Pitch)
ind_file.set_symbol('boundary_min', 0)
ind_file.set_symbol('boundary_max_y', max_radius + Pitch)
ind_file.set_symbol('boundary_min_y', 0)
ind_file.set_symbol('domain_max', 1.25 * F)
ind_file.set_symbol('domain_min', -10 * Dx)
ind_file.set_symbol('structure', 'STRUCT_CHANNEL')
ind_file.set_symbol('step_size', Dx)
ind_file.set_symbol('grid_size', Dx)
ind_file.set_symbol('grid_size_y', Dx)

#########################################################################################################
# Build MDL

# Substrate layer with SiO2 material
Seg = ind_file.add_segment((0, 0, 0), (0, 0, -2), (D, D))
Seg.structure('FIBER')
Seg.material('SiO2')  # Set the substrate material to SiO2

# Loop through the radii and use predefined heights
for i, (R, width) in enumerate(zip(ring_radii, ring_widths)):
    # Use predefined height from the list
    L = ring_heights[i]

    # Add component to .ind file at R value with "Locally Defined" material
    if i == 0:  # Center object needs to be a cylinder
        seg = ind_file.add_segment(position=(0, 0, 0), offset=(0, 0, L), dimensions=(2 * width, 2 * width))
        seg.structure('FIBER')
        seg.material('Locally Defined')  # Set material to "Locally Defined"
    else:
        seg = ind_file.add_arc(position=(-R, 0, L / 2), arcinfo=(R, 0, 360), dimensions=(width, L))
        seg.rotation((0, 90, 0))
        seg.material('Locally Defined')  # Set material to "Locally Defined"

#########################################################################################################
# Write Output

# Write .ind File
ind_file.write(f'MDL_TE_{prefix}.ind')