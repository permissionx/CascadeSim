# CascadeSim
End to end scripts for LAMMPS simulating cascade and OVITO extracting defect. 

## Features
* Finish a series of cascade simulation jobs almost by one key. Only a few paremeters need to be concerned. 
* You will know SIA directions, defect cluster informations. 

## Prerequisites 
* Lammps compiled with voronoi package.
* Python 3.6 or newer.
* Python libraries:
    * ovito 2.9
    * numpy
    * matplotlib

It is recommanded to install python and the libraries in a conda enviroment, which is the only way the author has tested. 
```bash
conda create -n CascadeSim python=3 numpy matplotlib conda-forge::ovito=2.9
```
If your device is not able to access Internet directly, ask your system manager to establish a ssh tunel for temperary download. 

## Installation
Simply download scripts.
`git clone https://github.com/permissionx/CascadeSim.git`

## :rocket:Usage
1. Assign input arguments in lammps in file `in` and run the LAMMPS.
```
#-----------------------------------------------------
#-------------------------INTPUT----------------------
#-----------------------------------------------------

# -loop variables
variable        env_temp index 500 300 #enviroment temperature
label           loop_env_temp

variable        E_PKA index 10 20 30  # unit: keV
label           loop_E_PKA
# --angle loop
variable        d_x index 0 1  #direction
variable        d_y index 0 3
variable        d_z index -1 5
variable        angle index 1 2
label           loop_angle

variable        random loop 10
label           loop_random

# -stop critical
variable        halt_dt equal -0.0000005*${env_temp}+0.00125
###This relationship should be determined by futher calculations.

# -box variable
variable        box_r equal 35 # the number of atoms > 25 times the energy of the projectile in eV (eg: 500 000 atoms for 20 keV)
variable        fix_th equal 2   # fix thickness
variable        bath_th equal 3   # bath thickness
variable        center equal 10

variable        lattice_constant equal 3.14

#------------------------------------------------------------
#-------------------------END-OF-INTPUT----------------------
#------------------------------------------------------------
```
Example above will calculate 2(temps)*3(energies)*2(angles)*10(random seeds) = 120 cases.

2. After finish the LAMMPS calculation. lammps trajetory files will writen in the dump folder. And a file `folder_name.csv` will be generated to store the names of all the calculated cases. To extract Step into `cascade_scripts`. Modify input paras in `extract_defect.py`.

3. Execuate defect extraction by typing `python extract_defect.py` in the shell. Results of the defects during and after cascade will be stored in `[cluster_dump_folder]`


## Known issues
* Cannot extract defect for too many cases (may over 500) at once. Slip the execuation into mutiple times by modify `extract_defect.py` can solve this problem temporarily.

## Things to do
* Update the OVITO interfact to 3.x.
* Add basic data statistics, such as defect nums VS sizes. 

## Acknowledgements
Any bug reports and feature requests are highly welcome. 
