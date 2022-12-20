# Written by Ke Xu, Beihang University.

import ovito.io as io
import ovito.modifiers as mods
import numpy as np 

def cluster_analysis(filename, outfilename, cutoffs):
    node = io.import_file(filename, multiple_frames=True)
    expressions = []
    expressions.append("c_21 == 0") 
    for d1 in [0,1]:
        for d2 in [-1,0,1]:
            for d3 in [-1,0,1]:
                if d1 == 0 and d2 == -1:
                    continue
                if d1 == 0 and d2 == 0 and d3 == -1:
                    continue
                expressions.append(
                    f"c_21 != 0 && c_21 != 1 && d1 == {d1} && d2 == {d2} && d3 == {d3}")
    with open(outfilename,'w') as file:
        pass
    for nframe in range(node.source.num_frames):
        mean_positions, sizes, c_21s, d1s, d2s, d3s, nframe, box =\
             compute_clusters(node, expressions, cutoffs, nframe)
        output_cluster(outfilename, mean_positions, sizes, c_21s, d1s, d2s, d3s, nframe, box)


def compute_clusters(node, expressions, cutoffs, nframe):
    node.compute(nframe)
    num_particles = node.output.number_of_particles
    clusters = np.zeros(num_particles, int)    
    try:
        for expression in expressions:
            mod = mods.SelectExpressionModifier()
            mod.expression = expression
            node.modifiers.append(mod)
            mod = mods.ClusterAnalysisModifier()
            if expression == "c_21 == 0":
                cutoff = cutoffs['V']
            else:
                cutoff = cutoffs['I']
            mod.cutoff = cutoff
            mod.only_selected = True
            node.modifiers.append(mod)
            mod = mods.ClearSelectionModifier()
            node.modifiers.append(mod)
            node.compute(nframe)
            this_clusters = node.output.particle_properties['Cluster'].array.copy()
            this_clusters[this_clusters != 0] += max(clusters)
            clusters += this_clusters
        mean_positions = []
        sizes = []
        c_21s = []
        d1s = []
        d2s = [] 
        d3s = [] 
        for ncluster in range(1, max(clusters)+1):
            positions = node.output.particle_properties['Position'].array[clusters == ncluster]
            mean_position = np.array([np.mean(positions[:,d]) for d in range(3)])
            size = len(positions)
            c_21 = node.output.particle_properties['c_21'].array[clusters == ncluster][0]
            d1 = node.output.particle_properties['d1'].array[clusters == ncluster][0]
            d2 = node.output.particle_properties['d2'].array[clusters == ncluster][0]
            d3 = node.output.particle_properties['d3'].array[clusters == ncluster][0]
            mean_positions.append(mean_position)
            sizes.append(size)
            c_21s.append(c_21)
            d1s.append(d1)
            d2s.append(d2)
            d3s.append(d3)
        return mean_positions, sizes, c_21s, d1s, d2s, d3s, nframe, node.output.cell.matrix
    except:
        return [], [], [], [], [], [], nframe, node.output.cell.matrix

def output_cluster(filename, mean_positions, sizes, c_21s, d1s, d2s, d3s, nframe, box):
    lines = []
    lines.append("ITEM: TIMESTEP\n")
    lines.append(f"{nframe}\n")
    lines.append("ITEM: NUMBER OF ATOMS\n")
    lines.append(f"{len(sizes)}\n")
    lines.append("ITEM: BOX BOUNDS pp pp pp\n")
    for d in range(3):
        lines.append(f"{box[d][3]} {box[d][d]+box[d][3]}\n")
    lines.append("ITEM: ATOMS id x y z c_21 d1 d2 d3 size\n")
    id = 0
    for position, size, c_21, d1, d2, d3 in zip(mean_positions, sizes, c_21s, d1s, d2s, d3s):
        id += 1
        lines.append(
            f"{id} {position[0]} {position[1]} {position[2]} {c_21} {d1} {d2} {d3} {size}\n")
    with open(filename,'a') as file:
        file.writelines(lines)

if __name__ == "__main__":
    cluster_analysis("/home/xuke/Researches/Cascade/neutron_project/1.0/iv_direction.dump",
            "/home/xuke/Researches/Cascade/neutron_project/1.0/cluster_iv_direction.dump")
    