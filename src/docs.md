# Understanding the Code

This documentation aims to explain the programs used in this study.

### `cluster_clean.py`

`cluster_clean.py` aims to clean the data so that only stars that are considered to be in the cluster are selected and further analysed. The approach we have used is a direct, yet conservative approach and uses data from the SIMBAD database on Gaia observations to plot the relevant properties of the cluster stars.

### How to Run the Program

`cluster_clean.py` runs as so in the command line using Python 3 - 

```Bash

python cluster_clean.py cluster_name

```
### How the Program Works
The program first starts off by importing the relevant python libraries and plugins (follow the instructions [here](https://github.com/rudrathegreat/Gaia-EDR3-Stellar-Clusters/blob/main/README.md) on this documentation to learn how you can install these libraries) - 

```Python

import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import pyvo as vo
import pylab

```

It then also loads the zeropoint correction tables attained by Lindegren et. al. 2020 from the Gaia Early Data Release 3, as shown below.

```Python

from zero_point import zpt
zpt.load_tables()

```

It then checks if a cluster name has been provided and then locates the relevant `.csv` file, as shown below - 

```Python

nargs = len(sys.argv) - 1
if nargs == 1:
    cluster = sys.argv[1]
else:
    print("Needs a cluster name, Rsky and Vlim")
    print("eg.")
    print("python cluster_clean.py M67 20 18")
    sys.exit()

filename = cluster+".csv"
print("reading "+filename)
try:
    data = pd.read_csv(filename)
except:
    print("Error reading data file / no such cluster")
    sys.exit()
    
```

It then tries to load a generated .stats file. If the `.stats` file is not located, then it will generate the `.stats` file itself later in the program. The `.stats` file contains information as to which stars to select. This selection process is done by checking if the stars fall within a certain range around the cluster (both in propermotion and in physical location) and then selects the star. To put it more simply, the program draws an oval-shape around the cluster and then selects stars that are within the oval.

This process of generating that oval shape can be seen below -

```Python

def draw_pm_circle(pmra0,pmdec0,rad,colour):
    t = np.linspace(0,2*np.pi,100)
    x = pmra0 + rad*np.sin(t)
    y = pmdec0 + rad*np.cos(t)
    plt.plot(x,y,colour,alpha=0.5)
    return

def draw_sky_circle(ra0,dec0,rad,colour):
    t = np.linspace(0,2*np.pi,100)
    x = ra0 + rad*np.sin(t)/np.cos(dec0*np.pi/180.0)
    y = dec0 + rad*np.cos(t)
    plt.plot(x,y,colour,alpha=0.5)
    return

```

And then all the relevant plots are then created. You can see the final result in [Figure 1](#figure-1-generated-plot-for-ngc7789) below.

Finally, the programs generates a `.zeropoint.txt`, which contains the following data for each star selected - 
1. Absolute magnitude of the stars (Gmag)
2. Blue light to red light ratio of these stars (BP-RP)
3. Offset between the parallaxes of the stars and the median parallax for the entire cluster (parallax offset)
4. Name of the cluster
5. Nueffused
6. Cluster PSC
7. The ecliptic latitude of the stars within the cluster
8. Soltype
9. The galactic latitude (gl) and the galactic longitude (gb) of the stars in the cluster
10. The zeropoint values for each of the stars
11. The parallax of the star

```Python

outputfilname = cluster+".zeropoint.txt"

for i in range(len(cluster_parallaxes)):
    if cluster_gmag[i]<18:
        f.write(str(cluster_gmag[i])+' ' 
            +str(cluster_bp_rp[i])+' '
            +str(cluster_parallaxes[i]-median_parallax_2)+' '
            +str(cluster)+' '
            +str(cluster_nueffused[i])+' '
            +str(cluster_psc[i])+' '
            +str(cluster_ecl_lat[i])+' '
            +str(cluster_soltype[i])+' '
            +str(cluster_gl[i])+' '
            +str(cluster_gb[i])+' '
            +str(cluster_zpvals[i])+' '
            +str(cluster_parallaxes[i])+' '
            +"\n")
            
 ```

## Figure 1: Generated Plot for NGC7789
![Generated Plot for NGC7789](https://github.com/rudrathegreat/Gaia-EDR3-Stellar-Clusters/blob/main/plots/NGC7789.png)

### `zp.py`

`zp.py` aims to compare the stars of several clusters to each other and identify 'tip of the red giant branch' stars, also known as TRGB stars. With this program, we can gain insights into the properties of the stars of several clusters.

### How to Run the Program

The program can be run as follows using Python 3 - 

```Bash

python zp.py type_of_cluster

```

There are three options for the type of cluster. There is - 

1. all
2. open
3. globs

