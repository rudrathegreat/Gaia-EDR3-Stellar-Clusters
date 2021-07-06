import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import pyvo as vo
import pylab

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

def onclick(event):
    if event.key=="q":
        print('x=%d, y=%d, xdata=%f, ydata=%f, key=%s' %
              (event.x, event.y, event.xdata, event.ydata, event.key))
    f = open("pm.center.txt", "w")
    f.write(str(event.xdata)+" "+str(event.ydata)+"\n")
    f.close()


# load corrections based on
# Lindegren et al 2020
# archive 2012.01742v2
# Gaia Early Data Release 3
# Parallax bias versus magnitude, colour, and position

from zero_point import zpt
zpt.load_tables()

# marker colours and types
alpha_g = 1
alpha_b = 0.1
alpha_r = 1
marker_b = 'b.'
marker_g = 'g.'
marker_r = 'r.'

plotflag = True
#plotflag = False

# command line arguments
nargs = len(sys.argv) - 1
if nargs == 1:
    cluster = sys.argv[1]
else:
    print("Needs a cluster name, Rsky and Vlim")
    print("eg.")
    print("python cluster_clean.py M67 20 18")
    sys.exit()

filename ="../cluster_data/"+cluster+".csv"
print("reading "+filename)
try:
    data = pd.read_csv(filename)
except:
    print("Error reading data file / no such cluster")
    sys.exit()

print("data file loaded")    

statfile = "../stats/"+cluster+".stats"
sfileloaded = False
print("Looking for stats file "+statfile)
try:
    X, Y, Xlow, Xhigh, Ylow, Yhigh, PM_Rad, sky_rad = np.loadtxt(
    statfile,skiprows=1,usecols=(0,1,2,3,4,5,6,7),unpack=True)
    sfileloaded = True
    print("Loaded stats file")
    print(X, Y, Xlow, Xhigh, Ylow, Yhigh, PM_Rad, sky_rad)
except:
    pass

if sfileloaded == False:
    print("No stats file")

#sys.exit()
    
source_id = data['source_id'].values
ra = data['ra'].values
dec = data['dec'].values
pmra = data['pmra'].values
pmdec = data['pmdec'].values
parallaxes = data['parallax'].values
parallax_error = data['parallax_error'].values
gmag = data['phot_g_mean_mag'].values
bp_rp = data['bp_rp'].values
nueffused = data['nu_eff_used_in_astrometry'].values
psc = data['pseudocolour'].values
ecl_lat = data['ecl_lat'].values
soltype = data['astrometric_params_solved'].values
gl = data['l'].values
gb = data['b'].values

mask = np.logical_or(soltype==31, soltype==95)

source_id = source_id[mask]
ra = ra[mask]
dec = dec[mask]
pmra = pmra[mask]
pmdec = pmdec[mask]
parallaxes = parallaxes[mask]
parallax_error = parallax_error[mask]
gmag = gmag[mask]
bp_rp = bp_rp[mask]
nueffused = nueffused[mask]
psc = psc[mask]
ecl_lat = ecl_lat[mask]
soltype = soltype[mask]
gl = gl[mask]
gb = gb[mask]

zpvals = zpt.get_zpt(gmag, nueffused, psc, ecl_lat, soltype)

# save original parallaxes
saved_parallaxes = np.copy(parallaxes)

# apply zero point correction
parallaxes = parallaxes - zpvals

#sfileloaded = False
if sfileloaded == False and plotflag:
    # draw proper motion cloud, select center
    fig, ax = plt.subplots(1,1, figsize=(20,10))
    #fig.figure(figsize=(20,10))    
    thismanager = plt.get_current_fig_manager()
    thismanager.toolbar.zoom()
    ax.plot(pmra,pmdec,'b.',alpha=alpha_b)
    plt.title("Center PM cloud with cursor and then hit q")
    cid = fig.canvas.mpl_connect('key_press_event', onclick)
    plt.show()
    fig.canvas.mpl_disconnect(cid)

    # now figure out a reasonable radius for the proper motion cloud
    x0, y0 = np.loadtxt("pm.center.txt", usecols=(0,1), unpack=True, dtype=float)

    x1 = pmra #- x0
    y1 = pmdec #- y0
    xlo, xhi = ax.get_xlim()
    ylo, yhi = ax.get_ylim()
    print("edges of plot")
    # override cursor position, with center of zoom box
    #x1 = (xlo+xhi)/2
    #y1 = (ylo+yhi)/2
    print(xlo, xhi, ylo, yhi)
    xmask = np.logical_and(x1>xlo,x1<xhi)
    ymask = np.logical_and(y1>ylo,y1<yhi)
    mask = np.logical_and(xmask,ymask)
    rad = (np.std(x1[mask])+np.std(y1[mask]))
    print("selection radius = ",rad)
    # set up center of PM cloud, and its size
    pmra0 = x0
    pmdec0 = y0
    pm_rmax = rad

else:
    pmra0 = X
    pmdec0 = Y
    pm_rmax = PM_Rad
    
# get center of cluster from SIMBAD
print("")
print('Connecting to SIMBAD TAP')
service = vo.dal.TAPService("https://simbad.u-strasbg.fr/simbad/sim-tap")
command = "SELECT RA, DEC FROM basic JOIN ident ON oidref = oid WHERE id = '"+str(cluster)+"'"
print(command)
print('Sending request for object center')
data = service.search(command)
try:
    ra0 = np.float(data['ra'])
    dec0 = np.float(data['dec'])
except:
    print("Error getting RA and DEC of target from SIMBAD")
    sys.exit()

print()
print("==============================")
print("Data from Simbad")
print("Coords (deg) : ",np.around(ra0,6),np.around(dec0,6))
print("==============================")
print()            


if cluster == "Berkeley_39":
    ra0 = 116.7
    dec0 = -4.67
    
# proper motion mask
#pm_rmax /= 2
pm_rad = np.sqrt((pmra-pmra0)**2+(pmdec-pmdec0)**2)
pm_rmax = np.std(pm_rad[pm_rad < pm_rmax*2])
pm_mask = pm_rad < pm_rmax 

print("============== cluster size ================")
# figure out a selection radius on the sky from proper motion masked positions
x1 = (ra[pm_mask] - ra0)*np.cos(dec0*np.pi/180.0)
y1 = dec[pm_mask] - dec0
pos_rmax = (np.std(x1)+np.std(y1))/2.0

print("sky selection radius = ",pos_rmax*60.0," min")

if sfileloaded==False:
    stats_file = '../stats/{}.stats'.format(cluster)
    print("Results saved to "+stats_file)
    with open(stats_file, "w") as file:
        file.write('X, Y, Xlow, Xhigh, Ylow, Yhigh, PM_Rad, sky_rad\n{} {} {} {} {} {} {} {}\n'.format(x0,y0,xlo,xhi,ylo,yhi,rad,pos_rmax))
        file.close()
    
# sky postion mask
pos_rad = np.sqrt( ( (ra-ra0)*np.cos(dec0*np.pi/180.0) )**2 + (dec-dec0)**2 )
pos_mask = pos_rad < pos_rmax

# apply both masks
mask = np.logical_and(pm_mask, pos_mask)

plt.figure(figsize=(20,10))

pm_sigma_width_multiplier = 3
pos_sigma_width_multiplier = 3

# plot proper motions
plt.subplot(256)
plt.plot(pmra[~mask],pmdec[~mask],marker_b,alpha=alpha_b)
#plt.plot(pmra[pos_mask],pmdec[pos_mask],marker_r,alpha=alpha_r)
# PM and sky position objects
plt.plot(pmra[mask],pmdec[mask],marker_g,alpha=alpha_g)
draw_pm_circle(pmra0,pmdec0,pm_rmax,'k')
plt.xlim(pmra0-pm_rmax*pm_sigma_width_multiplier,pmra0+pm_rmax*pm_sigma_width_multiplier)
plt.ylim(pmdec0-pm_rmax*pm_sigma_width_multiplier,pmdec0+pm_rmax*pm_sigma_width_multiplier)
plt.xlabel("PMRA [mas/yr]")
plt.ylabel("PMDEC [mas/yr]")
plt.title(filename)

# marginal histograms in PMRA and PMDEC
# PMRA
plt.subplot(251)
plt.hist(pmra[mask],orientation='vertical',histtype='step',bins=20,color='g')
plt.xlim(pmra0-pm_rmax*pm_sigma_width_multiplier,pmra0+pm_rmax*pm_sigma_width_multiplier)
# PMDEC
plt.subplot(257)
plt.hist(pmdec[mask],orientation='horizontal',histtype='step',bins=20,color='g')
plt.ylim(pmdec0-pm_rmax*pm_sigma_width_multiplier,pmdec0+pm_rmax*pm_sigma_width_multiplier)


# plot sky positions and selection circle
plt.subplot(253)
plt.plot(ra[~mask],dec[~mask],marker_b,alpha=alpha_b)
plt.plot(ra[mask],dec[mask],marker_g,alpha=alpha_g)
draw_sky_circle(ra0,dec0,pos_rmax,'k')
plt.xlabel("RA [deg]")
plt.ylabel("DEC [deg]")
df = 1.0/np.cos(dec0*np.pi/180.0)
plt.xlim(ra0-pos_rmax*df*pos_sigma_width_multiplier,ra0+pos_rmax*df*pos_sigma_width_multiplier)
plt.ylim(dec0-pos_rmax*pos_sigma_width_multiplier,dec0+pos_rmax*pos_sigma_width_multiplier)

# marginal histograms of ra and dec
# RA
plt.subplot(252)
plt.hist(dec[mask],orientation='horizontal',histtype='step',bins=20,color='g')
ax = plt.gca()
ax.set_xlim(ax.get_xlim()[::-1])
plt.ylim(dec0-pos_rmax*pos_sigma_width_multiplier,dec0+pos_rmax*pos_sigma_width_multiplier)
# DEC
plt.subplot(258)
plt.hist(ra[mask],orientation='vertical',histtype='step',bins=20,color='g')
ax = plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
df = 1.0/np.cos(dec0*np.pi/180.0)
plt.xlim(ra0-pos_rmax*df*pos_sigma_width_multiplier,ra0+pos_rmax*df*pos_sigma_width_multiplier)

# plot CMD
plt.subplot(154)
plt.plot(bp_rp[~mask],gmag[~mask],marker_b,alpha=alpha_b)
plt.plot(bp_rp[mask],gmag[mask],marker_g,alpha=alpha_g)
plt.xlabel("BP-RP")
plt.ylabel("Gmag")
plt.ylim(18.5,5)

# comparison of parallaxes for G>14 and G<14 for raw data
plt.subplot(255)
cluster_parallaxes = saved_parallaxes[mask]
cluster_gmag = gmag[mask]
cluster_bp_rp = bp_rp[mask]
cluster_nueffused = nueffused[mask]
cluster_psc = psc[mask]
cluster_ecl_lat = ecl_lat[mask]
cluster_soltype = soltype[mask]
cluster_zpvals = zpvals[mask]
plt.plot(cluster_parallaxes,cluster_gmag,marker_g,alpha=alpha_g)
gmask = np.logical_and(cluster_gmag > 14, cluster_gmag < 18)
calib_par = cluster_parallaxes[gmask]
calib_gmag = cluster_gmag[gmask]
calib_bp_rp = cluster_bp_rp[gmask]
median_parallax = np.median(calib_par)
std_parallax = np.std(calib_par-median_parallax)
std_mask = np.abs((calib_par-median_parallax)) < 2.0*std_parallax
med_uncorrected = np.median(calib_par[std_mask])
plt.plot(calib_par[~std_mask],calib_gmag[~std_mask],'r+')
plt.axvline(np.median(calib_par[std_mask]),label='Median parallax for 14 < G < 18')
plt.xlabel("parallax [mas]")
plt.ylabel("Gmag")
plt.ylim(18.5,5)
#plt.legend()

#####################################################################################
# plot parallaxes of cluster members only, compare parallaxes after zp correction
# of fainter and brighter stars to look for zeropoint offsets
plt.subplot(2,5,10)
cluster_parallaxes = parallaxes[mask]
cluster_gmag = gmag[mask]
cluster_bp_rp = bp_rp[mask]
cluster_gl = gl[mask]
cluster_gb = gb[mask]
gmask = np.logical_and(cluster_gmag > 14, cluster_gmag < 18)
calib_par = cluster_parallaxes[gmask]
calib_gmag = cluster_gmag[gmask]
calib_bp_rp = cluster_bp_rp[gmask]
calib_nueffused = cluster_nueffused[gmask]
calib_psc = cluster_psc[gmask]
calib_ecl_lat = cluster_ecl_lat[gmask]
calib_soltype = cluster_soltype[gmask]
#plt.plot(parallaxes,gmag,marker_b,alpha=alpha_b)
plt.plot(cluster_parallaxes,cluster_gmag,marker_g,alpha=alpha_g)
plt.xlabel("parallax [mas]")
plt.ylabel("Gmag")
plt.ylim(18.5,5)

print("====================================================================")
print()

# first cleaning round
median_parallax = np.median(calib_par)
print("median_parallax ",median_parallax)
plt.axvline(median_parallax,label='Median parallax for 14 < G < 18, no clip')
std_parallax = np.std(calib_par)
std_mask = np.abs((calib_par-median_parallax)) < 2.5*std_parallax
print("std_parallax ",std_parallax)

# second cleaning round
std_parallax_2 = np.std(calib_par[std_mask])
median_parallax_2 = np.median(calib_par[std_mask])
print("median_parallax_2 ",median_parallax_2)
std_mask_2 = np.abs((calib_par-median_parallax_2)) < 2.5*std_parallax_2
print("std_parallax_2 ",std_parallax_2)

plt.plot(calib_par[~std_mask_2],calib_gmag[~std_mask_2],'r+')
plt.axvline(median_parallax_2,label='Median parallax for 14 < G < 18, clipped')


###########################################################################################

print("Saving plot as ../plots/"+cluster+".png")    
plt.savefig("../plots/"+cluster+".png")
    
if plotflag:
    plt.show()

outputfilname = "../analysis/"+cluster+".zeropoint.txt"

print()
print("median parallaxes ZP-uncorrected, ZP-corrected: ",med_uncorrected, median_parallax_2)
print()

f = open(outputfilname, "w")

#for i in range(len(calib_par)):
#    if std_mask_2[i]:
#        f.write(str(calib_gmag[i])+" "
#                +str(calib_bp_rp[i])+" "
#                +str(calib_par[i]-median_parallax_2)+" "
#                +str(cluster)
#                +"\n")

#f.write('#gmag bp-rp zpoffset name nueff psc ecl soltype gl gb zpvals')
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

        
print()
print("results in "+outputfilname)
print()

def rdec(x,ndec):
    x = str(x)+"00000000001"
    x = np.float(x)
    return str(np.format_float_positional(x, precision=ndec))

print(dec0)

#ftable = open("tabletex.append.txt","a")
#ftable.write(cluster+" & "+rdec(ra0,3)+" & $"+rdec(dec0,3)+"$ & $"+rdec(pmra0,2)+"$ & $"+rdec(pmdec0,2)+"$ & $"+rdec(pos_rmax,2)+"$ & $"+rdec(pm_rmax,2)+"$ & "+str(len(cluster_gmag))+"  \\\\ \n")
#ftable.close()

#print(cluster," & ",rdec(ra0,3)," & $",rdec(dec0,3),"$ & $",rdec(pmra0,2),"$ & $",rdec(pmdec0,2),"$ & $",rdec(pos_rmax,2), "$ & $",rdec(pm_rmax,2), "$ & ",len(cluster_gmag),"  \\\\")


#if plotflag == False:
#    fig_file_zp = "uncorrected_plots/"+cluster+".zeropoints.png"
#    print("saving figure as "+fig_file_zp)
#    plt.savefig(fig_file_zp)
#    #plt.show()


