import matplotlib.pyplot as plt
import numpy as np
import sys
import mpl_scatter_density 
from matplotlib.colors import LinearSegmentedColormap

def running_med(x,y,N):
    idx = np.argsort(x)
    x = x[idx]
    y = y[idx]
    # compute number of bins needed
    Nbins = np.int(len(x)/N)
    # if not an exact number of N sized bins, add one more
    if np.abs(np.int(len(x)/N)-len(x)/N)>1e-10:
        Nbins += 1
    print("Nbins=",Nbins)
    xmean = []
    xedges = []
    ymedian = []
    sigma = []
    for i in range(Nbins):
        ilo = i*N; ihi = ilo + N
        if ihi>len(x):
            ihi = len(x)
        xmean.append(np.mean(x[ilo:ihi]))
        xedges.append(np.min(x[ilo:ihi]))
        ymedian.append(np.median(y[ilo:ihi]))
        sigma.append(np.std(y[ilo:ihi])/np.sqrt(len(y[ilo:ihi])))
    xedges.append(np.max(x[ilo:ihi]))
    yedges = ymedian.copy()
    yedges.append(yedges[-1])
    return xedges, yedges, xmean, ymedian, sigma

#
#f.write(str(trgb_gmag[i])+" "+str(trgb_par[i])+" "+str(trgb_zpoff[i])+" "+str(trgb_psc[i])+" "+str(trgb_ecl[i])+" "+str(trgb_soltype[i])+" ")
#f.write(str(trgb_bp_rp[i])+" "+str(trgb_gl[i])+" "+str(trgb_gb[i])+"\n")

gmag, par, zpoff, psc, el, soltype, bp_rp, gl, gb = np.loadtxt("trgb.range.dat", usecols=(0,1,2,3,4,5,6,7,8), unpack=True, dtype=float)

soltype += np.random.random(len(soltype))*10
el += np.random.random(len(el))*5.0

fig = plt.figure(figsize=(16,8))
                
def doit(y,x,name,Npoints,N):
    mask = np.isnan(x)
    x = x[~mask]
    y = y[~mask]
    plt.subplot(4, 2, N)
    plt.plot(x,y,'b.',alpha=0.2,ms=2)
    plt.axhline(0.0,alpha=0.5)
    plt.ylim(-0.25,0.25)
    plt.xlabel(name)
    xe, ye, xm, ym, sigma = running_med(x,y,Npoints)
#    print("xm, ym lens ",len(xm), len(ym))
#    for i in range(len(xm)):
#        print(xm[i],ym[i])
    for i in range(len(xe)):
#        print(xe[i],ye[i])
        plt.axvline(xe[i],color='k',alpha=0.2)
    plt.step(xe,ye,'k-',lw=2,where='post')
    sigma = np.array(sigma)*2
    plt.errorbar(xm, ym, yerr=sigma,fmt='k+',ms=0,elinewidth=2)
    plt.ylabel("zero point offset")
    return
    
doit(zpoff,gmag,"Gmag",100,1)    

doit(zpoff,par,"parallax [mas]",100,2)

doit(zpoff,psc,"pseudo-colour",30,3)

doit(zpoff,el,"ecliptic latitude [deg]",100,4)

mask = soltype<50
doit(zpoff,soltype,"soltype",np.int(sum(mask)),5)
plt.xlim(20,120)

doit(zpoff,bp_rp,"BP_RP",100,6)

gl += np.random.random(len(gl))*2
doit(zpoff,gl,"Gl [deg]",100,7)

gb += np.random.random(len(gb))*2
doit(zpoff,gb,"Gb [deg]",100,8)

plt.tight_layout()

plt.show()

print("median zp offset : ",np.median(zpoff)*1000.0," uas")
