import numpy as np 
import ovito.io as io
import ovito.modifiers as mod

def read_ref(file_name):
    node = io.import_file(file_name, multiple_frames=False)
    particles = node.source.particle_properties
    ids = particles['Particle Identifier'].array
    positions = particles['Position'].array
    return ids, positions

def recovery_iv_position(iv_name, lammps_iv_name, ref_name):
    ids, positions = read_ref(ref_name)
    with open(lammps_iv_name,'r') as infile:
        with open(iv_name,'w') as outfile:
            n = 0 
            in_step_count = 0
            for line in infile:
                in_step_count += 1
                if in_step_count < 9:
                    if in_step_count == 4:
                        natoms = int(line.split()[0])
                    outfile.write(line)
                elif in_step_count == 9:
                    outline = line[:-1] + ' x y z\n'
                    outfile.write(outline)
                    if natoms == 0:
                        in_step_count = 0
                else:
                    atom_id = int(line.split()[0])
                    position = positions[atom_id-1,:]
                    outline = line[:-1] + f' {position[0]} {position[1]} {position[2]}\n'
                    outfile.write(outline)
                    if in_step_count == 9+natoms:
                        n += 1 
                        in_step_count = 0

def generate_iv_direction(iv_direction_name, iv_name, lammps_2i_name):
    global lammps_node
    lammps_node = io.import_file(lammps_2i_name, multiple_frames=True)
    node = io.import_file(iv_name, multiple_frames=True)
    modifier = mod.PythonScriptModifier(function=direction_modifier)
    node.modifiers.append(modifier)
    io.export_file(node, iv_direction_name, 'lammps_dump', multiple_frames=True,
                 columns=['Particle Identifier','Particle Type',
                          'Position.x','Position.y','Position.z',
                          'c_2[1]','d1','d2','d3'])
    

def direction_modifier(frame, input, output):
    lammps_node.compute(frame)
    i2_positions = lammps_node.output.particle_properties['Position'].array
    positions = input.particle_properties['Position'].array
    ivs = input.particle_properties['c_2[1]'].array
    directions = []
    for n,position in enumerate(positions):
        if ivs[n] == 0:
            direction = [0,0,0]
        else:
            direction = compute_direction(position, i2_positions)
        directions.append(direction)
    directions = np.array(directions)
    ps = ['d1','d2','d3']
    for d,p in enumerate(ps):
        if len(directions) > 0:
            output.create_user_particle_property(p,'int',data=directions[:,d])
        else:
            output.create_user_particle_property(p,'int')

def compute_direction(position, i2_positions):
     d_positions = i2_positions - position 
     lengths = (d_positions[:,0]**2 + d_positions[:,1]**2 + d_positions[:,2]**2)**0.5
     min_arg_1 = np.argmin(lengths)
     lengths[min_arg_1] = float('inf')
     min_arg_2 = np.argmin(lengths)
     dr = i2_positions[min_arg_1] - i2_positions[min_arg_2]
     direction = dr_to_direction(dr)
     return direction 

def dr_to_direction(dr):
    length = np.linalg.norm(dr)
    direction = [0,0,0]
    for d in range(3):
        if dr[d]/length > 0.1:
            direction[d] = 1
        elif dr[d]/length < -0.1:
            direction[d] = -1
    if direction[0] < 0:
        direction = [-direction[i] for i in range(3)]        
    return direction

if __name__ == '__main__':
     recovery_iv_position('iv.dump', 'lammps_iv.dump', 'ref.dump')
     generate_iv_direction('iv_direction.dump', 'iv.dump', 'lammps_2i.dump')
