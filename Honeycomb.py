from abaqus import *
from abaqusConstants import *
import math
import part
import material
import section
import assembly
import step

# Function to create hexagon part
def create_hexagon(model, size, thickness, depth):
    sketch = model.ConstrainedSketch(name='Hexagon_Sketch', sheetSize=200.0)
    
    # Create outer hexagon
    points_outer = []
    for i in range(6):
        angle = i * math.pi / 3
        x = size * math.cos(angle)
        y = size * math.sin(angle)
        points_outer.append((x, y))
    
    for i in range(6):
        sketch.Line(point1=points_outer[i], point2=points_outer[(i+1)%6])
    
    # Create inner hexagon
    inner_size = size - thickness
    points_inner = []
    for i in range(6):
        angle = i * math.pi / 3
        x = inner_size * math.cos(angle)
        y = inner_size * math.sin(angle)
        points_inner.append((x, y))
    
    for i in range(6):
        sketch.Line(point1=points_inner[i], point2=points_inner[(i+1)%6])

    # Create a part from the sketch
    part = model.Part(name='Hexagon', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseSolidExtrude(sketch=sketch, depth=depth)
    
    return part

# Function to create honeycomb structure
def create_honeycomb(model, size, thickness, depth, nx, ny, nz):
    hexagon_part = create_hexagon(model, size, thickness, depth)

    # Create an assembly
    assembly = model.rootAssembly
    
    # Calculate the distance between hexagon centers
    dx = 1.5 * size  # Horizontal distance
    dy = size * math.sqrt(3)  # Vertical distance
    
    for i in range(nx):
        for j in range(ny):
            x = i * dx
            y = j * dy + (i % 2) * (size * math.sqrt(3) / 2)  # Offset every other row
            for k in range(nz):
                z = k * depth
                
                instance_name = 'Hexagon-{0}-{1}-{2}'.format(i, j, k)
                instance = assembly.Instance(name=instance_name, part=hexagon_part, dependent=ON)
                assembly.translate(instanceList=(instance_name,), vector=(x, y, z))

# Main script
model_name = 'Honeycomb_Model'

# Get user input
inputs = getInputs(
    fields=(
        ('Size of hexagon (distance from center to vertex):', '10.0'),
        ('Thickness of walls:', '1.0'),
        ('Depth of hexagon (adjust as needed):', '50.0'),
        ('Number of cells in x direction:', '10'),
        ('Number of cells in y direction:', '10'),
        ('Number of cells in z direction:', '1')
    ),
    label='Enter the parameters for the honeycomb structure',
    dialogTitle='Honeycomb Structure Parameters'
)

# Parse user input
size = float(inputs[0])
thickness = float(inputs[1])
depth = float(inputs[2])
nx = int(inputs[3])
ny = int(inputs[4])
nz = int(inputs[5])

# Create a new model
model = mdb.Model(name=model_name)

# Create the honeycomb structure
create_honeycomb(model, size, thickness, depth, nx, ny, nz)

# Save the model
mdb.saveAs('honeycomb_model.cae')
