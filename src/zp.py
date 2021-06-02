import numpy as np
import matplotlib.pyplot as plt
import sys
import matplotlib.patches as patches

def glob(cluster_name):

# list is from /home/cflynn/alan/gaiaedr3/globs.MVsort.txt
# all clusters with M_V<15.5 for horizontal branch

    globs = ["NGC6397","M4","NGC6752","NGC104","M22","M55","M71","NGC5139",
             "M12","M10","NGC3201","M13","NGC5904","M92","NGC7099","NGC6352",
             "NGC6544","NGC6362","NGC6541","NGC288","NGC362","NGC6723","NGC4372"]

    return cluster_name in globs


def plotpoints(x,y,cluster_name,cluster,argument):
    for i in range(len(cluster)):
        alpha = 1
        cmask = cluster_name==cluster[i]
        open_clusters = False
        globs = False
        if argument == "all":
            globs = True
            open_clusters = True
        if argument == "globs":
            globs = True
        if argument == "open":
            open_clusters = True
        if globs :
            if glob(cluster[i]) == True:
                plt.plot(x[cmask],y[cmask],'.',ms=2,alpha=alpha,label=str(cluster[i]).split(" ")[0],zorder=0)
        if open_clusters:
            if glob(cluster[i]) == False:
                plt.plot(x[cmask],y[cmask],'.',ms=2,alpha=alpha,label=str(cluster[i]).split(" ")[0],zorder=0)
    return

############################### main #################################

nargs = len(sys.argv) - 1
if (nargs==1):
    argument = sys.argv[1]    
    corr = sys.argv[1]
else:
    print("Useage : ")
    print("python zp.py all/glob/open")
    print("eg python zp.py all")
    sys.exit()
    
filename = "all.zeropoint.txt"

# 0    1     2        3    4     5   6   7       8  9  10     11
# gmag bp-rp zpoffset name nueff psc ecl soltype gl gb zpvals parallax
gmag, bp_rp, zp, zp0, nueff, psc, ecl, soltype, gl, gb, par = np.loadtxt(filename, usecols=(0,1,2,10,4,5,6,7,8,9,11), unpack=True, dtype=float)

# TRGB test
trgb_mask = np.logical_and(gmag < 12, gmag > 8)

# Zinn test
#trgb_mask = gmag < 11

# Riess et al test
#trgb_mask = np.logical_and(gmag < 10, gmag > 6)

trgb_gmag = gmag[trgb_mask]
trgb_zpoff = zp[trgb_mask]
trgb_bp_rp = bp_rp[trgb_mask]
trgb_par = par[trgb_mask]
trgb_psc = psc[trgb_mask]
trgb_ecl = ecl[trgb_mask]
trgb_gl = gl[trgb_mask]
trgb_gb = gb[trgb_mask]
trgb_soltype = soltype[trgb_mask]
f = open("trgb.range.dat","w")
for i in range(len(trgb_gmag)):
    f.write(str(trgb_gmag[i])+" "+str(trgb_par[i])+" "+str(trgb_zpoff[i])+" "+str(trgb_psc[i])+" "+str(trgb_ecl[i])+" "+str(trgb_soltype[i])+" ")
    f.write(str(trgb_bp_rp[i])+" "+str(trgb_gl[i])+" "+str(trgb_gb[i])+"\n")
f.close()

cluster_name = np.loadtxt(filename, usecols=(3), unpack=True, dtype=str)
cluster_list = list(set(cluster_name))
print(cluster_list)

gmask = gmag < 14
print("Median parallax offset for G<14 ",np.median(zp[gmask]))

gmag_max = 18.2
gmag_min = 5

plt.figure(figsize=(20,10))

ax = plt.subplot(111)
plotpoints(bp_rp,gmag,cluster_name,cluster_list,argument)
plt.axhline(14.0,alpha=0.5)
rect = patches.Rectangle((0.5,9), width=2.0, height=2, alpha=0.1, facecolor='black',label='TRGB zone')
ax.add_patch(rect)
plt.ylim(gmag_max,gmag_min)
plt.xlabel('BP-RP')
plt.ylabel('Gmag')
plt.legend(ncol=3)

plt.tight_layout()

plt.show()

mask = gmag<20
fmask = gmag<12

plt.figure(figsize=(20,10))

parlim = 0.20

plt.subplot(515)
plotpoints(gmag[mask],zp[mask]+zp0[mask],cluster_name[mask],cluster_list,argument)
plt.axvline(14.0,c='k',alpha=0.5)
plt.axhline(0.0,c='b',alpha=0.5)
plt.ylabel('zp offset [mas]')
plt.xlabel('Gmag')
plt.xlim(6.0,18.0)
plt.ylim(-parlim,parlim)

plt.subplot(513)
plotpoints(gmag[mask],zp[mask],cluster_name[mask],cluster_list,argument)
plt.axvline(14.0,c='k',alpha=0.5)
plt.axhline(0.0,c='b',alpha=0.5)
plt.ylabel('zp offset [mas]')
plt.xlabel('Gmag')
plt.xlim(6.0,18.0)
plt.ylim(-parlim,parlim)

plt.subplot(514)
plotpoints(gmag[mask],zp0[mask],cluster_name[mask],cluster_list,argument)
plt.axhline(0.0,c='b',alpha=0.5)
plt.axvline(14.0,c='k',alpha=0.5)
plt.ylabel('zp0 correction [mas]')
plt.xlabel('Gmag')
plt.xlim(6.0,18.0)
plt.ylim(-parlim,parlim)

corr_mask = gmag < 10
print("median correction for gmag<10 : ",np.median(zp0[corr_mask]))



gmag_orig = np.copy(gmag)
zp_orig = np.copy(zp)
zp0_orig = np.copy(zp0)
bp_rp_orig = np.copy(bp_rp)

gmag = gmag_orig[mask]
zp = zp_orig[mask]
zp0 = zp0_orig[mask]
bp_rp = bp_rp_orig[mask]
medians = []
gbin = []
mscatt = []
glo = 6.00
dg = 0.50

colour_cut = 100.0
    
cmask = bp_rp<colour_cut
gmag = gmag[cmask]
zp = zp[cmask]
zp0 = zp0[cmask]
bp_rp = bp_rp[cmask]
for i in range(24):
    ax1 = plt.subplot(5,12,i+1)
    gmask = np.logical_and(gmag>glo,gmag<glo+dg)
    bins = np.arange(-0.20,0.20,0.02)
    Nzp = np.sum(gmask)
    medians.append(np.median(zp[gmask]))
    gbin.append(glo+dg/2.0)
    mscatt.append(np.std(zp[gmask])/np.sqrt(Nzp))
    print(glo,glo+dg,Nzp,np.std(zp[gmask]),mscatt[-1])
    plt.hist(zp[gmask],bins=bins,alpha=0.5)
    plt.axvline(0.0,c='k',alpha=0.5)
    ax1.axes.xaxis.set_visible(False)
    ax1.axes.yaxis.set_visible(False)
    plt.xlim(-0.2,0.2)
    plt.title(str(glo)+"<G<"+str(glo+dg))
    glo += dg 

plt.subplot(513)
plt.step(np.array(gbin)+dg/2,medians,'k-',lw=1)
mscatt = np.array(mscatt)*2
plt.errorbar(gbin,medians,yerr=mscatt,fmt='k+',ms=0,elinewidth=2)

medians = []
gbin = []
mscatt = []
cmask = bp_rp<colour_cut
gmag = gmag[cmask]
glo = 6.00
bp_rp = bp_rp[cmask]
for i in range(24):
    gmask = np.logical_and(gmag>glo,gmag<glo+dg)
    Nzp = np.sum(gmask)
    raw_zp = zp[gmask]+zp0[gmask]
    medians.append(np.median(raw_zp))
    gbin.append(glo+dg/2.0)
    mscatt.append(np.std(zp[gmask])/np.sqrt(Nzp))
    print(glo,glo+dg,Nzp,np.std(zp[gmask]),mscatt[-1])
    glo += dg 

plt.subplot(515)
plt.step(np.array(gbin)+dg/2,medians,'k-',lw=1)
mscatt = np.array(mscatt)*2
plt.errorbar(gbin,medians,yerr=mscatt,fmt='k+',ms=0,elinewidth=2)

plt.show()

