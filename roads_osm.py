#!/usr/bin/env python

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ghislainv.github.io
# GDAL version    :2.1.2 (OGR enabled)
# osmtools        :https://gitlab.com/osm-c-tools/osmctools
# license         :GPLv3
# ==============================================================================

import os
from osgeo import ogr, osr
import urllib

# Variables
# Well Known Text (WKT) projection definition
continent_list = ["Africa", "South_America", "Central_America",
                  "North_America"]
proj_file = ["proj102022.prj", "proj102033.prj", "", ""]
resolution = 30
res_str = str(resolution) + " " + str(resolution)

# Select continent
i = 0
continent = continent_list[i]

# Input projection
inproj = osr.SpatialReference()
inproj.ImportFromEPSG(4326)

# Output projection
with open(proj_file[i], 'r') as f:
    proj = f.read()
outproj = osr.SpatialReference()
outproj.ImportFromWkt(proj)

# Points coordinates
x_ll, y_ll = -92, -56.0
x_ur, y_ur = -31, 15.0
extent = (x_ll, y_ll, x_ur, y_ur)


# Convert extent
def convertExtent(extent, inproj, outproj):

    # Coordinates from extent
    xmin, ymin, xmax, ymax = extent[0], extent[1], extent[2], extent[3]

    # Create points from coordinates
    point_ll = ogr.Geometry(ogr.wkbPoint)
    point_ll.AddPoint(xmin, ymin)
    point_ur = ogr.Geometry(ogr.wkbPoint)
    point_ur.AddPoint(xmax, ymax)

    # Transformation
    ct = osr.CoordinateTransformation(inproj, outproj)
    # Transform points
    point_ll.Transform(ct)
    point_ur.Transform(ct)

    # Extent
    extent_proj = (point_ll.GetX(), point_ll.GetY(),
                   point_ur.GetX(), point_ur.GetY())

    # Return
    return(extent_proj)


# New extent
extent_proj = convertExtent(extent, inproj, outproj)
extent_str = " ".join(map(str, extent_proj))

# ===========================
# Roads from Open Street Map
# ===========================

# Message
print("Roads from OSM")

# New directory for results
results_dir = "results_" + continent
os.makedirs(results_dir)
os.chdir(results_dir)
# Download OSM data from Geofabrik
# url="http://download.geofabrik.de/africa-latest.osm.pbf"
url = "http://download.geofabrik.de/south-america-latest.osm.pbf"
urllib.urlretrieve(url, "country.osm.pbf")
os.system("osmconvert country.osm.pbf -o=country.o5m")

# All roads
os.system("osmfilter country.o5m --keep='highway=*' > all_roads.osm")
cmd = "ogr2ogr -overwrite -skipfailures -f 'ESRI Shapefile' -progress \
        -sql 'SELECT osm_id, name, highway FROM lines \
        WHERE highway IS NOT NULL' \
        -lco ENCODING=UTF-8 all_roads.shp all_roads.osm"
os.system(cmd)

# Reproject
os.system("ogr2ogr -overwrite -s_srs EPSG:4326 -t_srs $proj -f 'ESRI Shapefile' \
        -lco ENCODING=UTF-8 all_roads_proj.shp all_roads.shp")

# Rasterize
cmd = "gdal_rasterize -tap -burn 1 \
        -co 'COMPRESS=LZW' -co 'PREDICTOR=2' -co 'BIGTIFF=YES' -ot Byte \
        -te " + extent_str + " \
        -a_nodata 255 \
        -tr " + res_str + " \
        -l all_roads_proj all_roads_proj.shp all_roads.tif"
os.system(cmd)

# End
