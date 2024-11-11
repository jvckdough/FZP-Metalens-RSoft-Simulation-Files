import gdspy
import numpy as np
import ast

# Load and parse the heights data as a nested list, then flatten it
heights_file = "/Users/jackdoughty/FDTD/FZP/FZP0Pxl_formatted.txt"
with open(heights_file, "r") as f:
    data = f.read()  # Read the entire file as a string
    ring_heights = np.array(ast.literal_eval(data)).flatten()  # Interpret as nested list and flatten

# Parameters
radius = 50  # Radius of the zone plate in meters
num_rings = len(ring_heights)  # Number of rings based on provided heights
ring_width = radius / num_rings  # Uniform width of each ring
min_tolerance = 1e-9  # Set a minimum tolerance to avoid NaN errors

# Define two layers for alternating black and white colors
layer_cycle = [1, 2]  # Alternating layers
current_layer_index = 0  # Start with the first layer in the cycle

# Create a GDSII library and a cell for the zone plate
lib = gdspy.GdsLibrary()
cell = lib.new_cell("Fresnel_Zone_Plate")

# Draw each ring, alternating layers when height increases
for i in range(num_rings):
    inner_radius = i * ring_width
    outer_radius = (i + 1) * ring_width
    
    # Skip rings with near-zero radius to avoid NaN issues
    if outer_radius <= min_tolerance:
        continue

    # Start a new color layer if the current ring height is greater than the previous
    if i > 0 and ring_heights[i] > ring_heights[i - 1]:
        # Alternate to the next layer in the 2-layer sequence
        current_layer_index = (current_layer_index + 1) % len(layer_cycle)

    # Assign the current layer from the layer cycle
    current_layer = layer_cycle[current_layer_index]

    # Create each ring as an annular structure with corresponding layer (color)
    ring = gdspy.Round(
        (0, 0),                 # Center of the zone plate
        outer_radius,           # Outer radius
        inner_radius=inner_radius,  # Inner radius
        tolerance=max(min_tolerance, 0.001),  # Avoid very small tolerance
        layer=current_layer     # Assign to current layer for color
    )
    cell.add(ring)

# Save the zone plate layout to a GDS file
output_file = "/Users/jackdoughty/FDTD/FZP/fresnel_zone_plate.gds"
lib.write_gds(output_file)
print(f"GDS file generated: {output_file}")