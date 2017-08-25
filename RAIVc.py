#!/usr/bin/env python
'''
Copyright (C) 2017 World Meteorological Organization

This is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this.  If not, see <http://www.gnu.org/licenses/>.
'''
## Regional Association IV - Caribbean
#  

## 
# @file
# @author Daniel Michelson, Environment and Climate Change Canada, for the 
# WMO Interprogramme Expert Team on Operational Weather Radar
# @date 2017-03-11
 
import sys, os, zipfile, re, glob, string
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import shapefile
from countries import plotCountry, Round

title = "RA IV Caribbean: March 2017"
fstr = 'RAIVc'

COUNTRIES="US,CU,VE,GY,SR,CW,BB,BZ,DO,GF,JM,MQ,TT,SX,GP,PR,BS"

# x1=east, x2=west, y1=south, y2=north
x1 = -92
x2 = -48
y1 = 0
y2 = 28
lon, lat, step = -70.0, 15.0, 10

fig = plt.figure()
ax = plt.subplot(111)

plt.title(title)
 
m = Basemap(resolution='i',projection='laea', 
            llcrnrlat=y1,urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,
            lon_0=lon,lat_0=lat,lat_ts=(y1+y2)/2)
m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawmeridians(np.arange(Round(x1,False,step)-step,
                          Round(x2,False,step)+2*step,step),
                labels=[0,0,0,1],color='black',linewidth=0.2)
m.drawparallels(np.arange(Round(y1,False,step)-step,Round(y2)+step,step),
                labels=[1,0,0,0],color='black',linewidth=0.2)
m.shadedrelief()

# Loop through country list and add label for each
missing = []
for c in COUNTRIES.split(','):
    try:
        plotCountry(m, ax, c)
    except shapefile.ShapefileException:
        missing.append(c)
missing.sort()
if len(missing): print "No information for %s" % string.join(missing, ",")

# Write out and/or plot results
plt.savefig('%s.png' % fstr,dpi=300)
os.system('convert -trim %s.png %s.png' % (fstr, fstr))
#plt.savefig('%s.pdf % fstr',dpi=300)
plt.show()
