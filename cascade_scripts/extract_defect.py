from iv import *
from cluster_analysis import *
import os

def get_out_cluster_name(filename): # only for linux
    names = filename.split('/')
    name = names[-1]
    names[-1] = "cluster_"+name
    outname = ""
    for n,name in enumerate(names):
        outname += name
        if n != len(names)-1:
            outname += '/'
    return outname

def extract_dirs(prefix, dir_log):
    with open(dir_log,'r') as file:
        lines = file.readlines()
    dirs = []
    names = []
    for line in lines[1:]:
        names.append(line[:-1])
        dirs.append(prefix+'/'+line[:-1])
    return dirs, names


if __name__ == '__main__':
    #############################################
    ##################Input#######################
    ################################################
    last = True #  compute all frames if False
    cluster = False # cluster analysis if True
    prefix = "../dump"
    dir_log = "../folder_name.csv"
    cluster_dump_folder = "../cluster_dump"
    cutoff_I = 4.4815
    cutoff_V = 3.1689
    ##################End of Input################
    ###############################################
    cutoffs = {"I":cutoff_I, "V": cutoff_V}
    os.system(f"mkdir {cluster_dump_folder}")
    if last == False and cluster == True:
        Warning("This would last for a long time since clustering middle frames...")
    if not last:
        Warning("Direction will be computed only when last == True")
    file_dirs, cascade_names = extract_dirs(prefix, dir_log)
    # If you want to enforce dirs, set here
    # file_dirs = ["path to dump_dir"]
    for file_dir, cascade_name in zip(file_dirs, cascade_names):
        print(f"Computing in {file_dir} ...")
        if last:
            iv_name = file_dir+'/iv_last.dump'
            lammps_iv_name = file_dir+'/lammps_iv_last.dump'
            ref_name = file_dir +'/ref.dump'
            iv_direction_name = file_dir + '/iv_direction_last.dump'
            lammps_2i_name = file_dir + '/lammps_2i_last.dump'
        else:
            iv_name = file_dir+'/iv.dump'
            lammps_iv_name = file_dir+'/lammps_iv.dump'
            ref_name = file_dir +'/ref.dump'
            iv_direction_name = file_dir + '/iv_direction.dump'
            lammps_2i_name = file_dir + '/lammps_2i.dump'
        out_cluster_name = get_out_cluster_name(iv_direction_name)
        
        recovery_iv_position(iv_name, lammps_iv_name, ref_name)
        if last:
            generate_iv_direction(iv_direction_name, iv_name, lammps_2i_name)
        if cluster:
            cluster_analysis(iv_direction_name, out_cluster_name, cutoffs)
            os.system(f"cp {out_cluster_name} {cluster_dump_folder}/{cascade_name}.cluster.dump")
