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

## Reads country label info from two sources:
#  Countries of the World (COW): names and abbreviations
#  Phys geo: centroid coordinated
#  Phys geo is read first, ISO 3166 abbreviations are used to look up UNGEGN
#  abbreviations and centroid coordinated
#  Note that there are discrepancies between ISO 3166-1 alpha 2 and ccTLD
#  as it is used in practice (UK)
#  Output is a dictionary where ISO 3166 is the key and a tuple containing
#  (TLD, "lon lat") is the value.

# Originally coded while the author was at SMHI, 2014-07-01

## @file
## @author Daniel Michelson, Environment and Climate Change Canada
## @date 2017-03-11

import sys, os, re
import numpy as np
import shapefile
from matplotlib.collections import LineCollection
import matplotlib.patheffects as PathEffects


## Reads select contents of Countries of the World into a dictionary
# @param string of the input COW file name
# @returns dictionary containing ISO 3166-1 alpha-2, 
# something else two-lettered, and the country's full name.
# Keys in the dictionary are country TLAs, ISO 3166-1 alpha-3
def readISO(fstr="labels/cow.txt"):
    fd = open(fstr)
    LINES = fd.readlines()
    fd.close()

    iso = {}

    for l in range(29,len(LINES)):
        line = LINES[l].split("; ")
        iso[line[1]] = line[0], line[3], line[4]

    return iso


## Reads select contents of phys_geo CSV file into a dictionary
# @param string of the input phys_geo file name
# @returns dictionary containing a single string of the country's centroid
# coordinates as 'lon lat'
# Keys in the dictionary are country TLAs
def readPG(fstr="labels/phys_geo.csv"):
    fd = open(fstr)
    LINES = fd.readlines()
    fd.close()

    pg = {}

    for l in range(1,len(LINES)):
        line = LINES[l].split(",")
        c = re.sub('"', '', line[0])
        pg[c] = "%s %s" % (line[4], line[3])     # Old: "lon lat"
        pg[c] = float(line[4]), float(line[3])  # New: (lon, lat)

    return pg
        

## Reads the COW and phys_geo according to the above and merges the information
# @param boolean whether to make noise if we can't merge a given country because
# it doesn't exist in phys_geo.
# @returns dictionary containing a single string of the country's centroid
# coordinates as 'lon lat'
# Keys in the dictionary are the country ISO 3166-1 alpha-2 strings
def merge(verbose=False):
    iso = readISO()
    pg = readPG()

    d = {}

    for k in iso.keys():
        tld = iso[k][0]
        try:
            d[tld] = k, pg[k]
        except KeyError:
            if verbose:
                print "No matching key for %s: %s" % (k, iso[k][2])

    return d


merged = merge()


## Draws the country adm0 polygon and fills it. Adds the country label at that
# country's centroid
# @param map object
# @param axis object
# @param string containing that country's ISO 8611-1 Alpha2 id
# @param string path where to find shape files for that country
def plotCountry(m, ax, id, path='gadm0'):
    country, lonlat = merged[id]

    r = shapefile.Reader(r"%s/%s_adm0" % (path, country))
    shapes = r.shapes()
    records = r.records()

    for record, shape in zip(records,shapes):
        lons,lats = zip(*shape.points)
        data = np.array(m(lons, lats)).T

        if len(shape.parts) == 1:
            segs = [data,]
        else:
            segs = []
            for i in range(1,len(shape.parts)):
                index = shape.parts[i-1]
                index2 = shape.parts[i]
                segs.append(data[index:index2])
            segs.append(data[index2:])

        lines = LineCollection(segs,antialiaseds=(1,))
        lines.set_facecolors('lightgreen')
        lines.set_edgecolors('k')
        lines.set_linewidth(0.1)
        lines.set_alpha(0.5)
        ax.add_collection(lines)

    # Add country centroid
    lon, lat = lonlat
    xpt,ypt = m(lon,lat)
    txt = ax.annotate(id, (xpt, ypt), color='r', size='medium',
                      ha='center', va='center',
                      path_effects=[PathEffects.withStroke(linewidth=3,
                                                           foreground="w"),
                                    PathEffects.withSimplePatchShadow()])


## Convenience function for rounding up/down a given coordinate
# @param value either int or float to round up or down
# @param int how much to round up or down
# @returns float
def Round(coord, up=True, inc=10):
    if up:
        return int(coord/10)*10. + inc
    else:
        return int(coord/10)*10. - inc


if __name__ == "__main__":
    l, f = sys.argv[1], sys.argv[2]
    d = merge(True)
    fd = open(f, "w")
    for c in l.split(","):
        try:
            dc = d[c]
        except KeyError:
            print "No look-up for %s" % c
        if c == "GB": c = "UK"
        fd.write("%s %s\n" % (dc, c))
    fd.close()
