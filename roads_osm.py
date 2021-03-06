#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ghislainv.github.io
# GDAL version    :2.1.2 (OGR enabled)
# osmtools        :https://gitlab.com/osm-c-tools/osmctools
# license         :GPLv3
# ==============================================================================

import os
# import urllib

# Areas of interest
area = ["Africa", "Asia", "Australia", "Mexico", "South_America"]
# Well Known Text (WKT) projection definition
proj = ["proj/proj102022.prj", "proj/proj102028.prj", "proj/proj102028.prj",
        "proj/proj102033.prj", "proj/proj102033.prj"]
# Extents
ext_Africa = (-18, -27, 52, 16)
ext_Asia = (68, -16, 145, 29)
ext_Australia = (143, -46, 170, 1)
ext_Mexico = (-114, 6, -57, 29)
ext_South_America = (-84, -36, -32, 12)
extent = [ext_Africa, ext_Asia, ext_Australia, ext_Mexico, ext_South_America]
# Original working directory
owd = os.getcwd()

# Download planet data from OpenStreetMap (version of 11/09/2017)
# url = "https://planet.osm.org/pbf/planet-170911.osm.pbf"
# urllib.urlretrieve(url, "planet.osm.pbf")
if os.path.isfile("planet-170911.osm.pbf") is False:
    os.system("wget https://planet.osm.org/pbf/planet-170911.osm.pbf")
# OSM planet file
planet = os.path.join(owd, "planet-170911.osm.pbf")


def _mkdir(newdir):
    """works the way a good mkdir should :)
    - already exists, silently complete
    - regular file in the way, raise an exception
    - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired "
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        # print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


# Function roads_osm
def roads_osm(planet, area, extent, proj, res):
    """Function to extract roads from OpenStreetMap planet data and
    rasterize the data.

    :param planet: Path to planet .osm.pbf file

    :param area: Area of interest. Will be used to create a new directory.

    :param extent: Extent (xmin, ymin, xmax, ymax) used to extract OSM
    data with osmconvert.

    :param proj: Projection used to reproject road data.

    :param res: Resolution used to rasterize roads.

    """

    # New directory for results
    results_dir = "results/" + area
    print("Create directory: " + results_dir)
    _mkdir(results_dir)
    os.chdir(os.path.join(owd, results_dir))

    # Call to osmconvert with box
    box = ",".join(map(str, extent))
    print("Convert OSM data with box: " + box)
    os.system("osmconvert " + planet + " -b=" + box + " -o=area.o5m -v")

    # Extract roads
    print("Extract roads from OSM data")
    os.system("osmfilter area.o5m --keep='highway=*' -o=all_roads.osm -v")
    cmd = "ogr2ogr -overwrite -skipfailures -f 'ESRI Shapefile' -progress \
           -sql 'SELECT osm_id, name, highway FROM lines \
           WHERE highway IS NOT NULL' \
           -lco ENCODING=UTF-8 all_roads.shp all_roads.osm"
    os.system(cmd)

    # Reproject
    print("Reproject road vector data")
    os.system("ogr2ogr -overwrite -s_srs EPSG:4326 -t_srs " + proj + " -f 'ESRI Shapefile' \
               -progress \
               -lco ENCODING=UTF-8 all_roads_proj.shp all_roads.shp")

    # Resolution as string
    res_str = str(res) + " " + str(res)

    # Rasterize
    print("Rasterize road vector data")
    cmd = "gdal_rasterize -tap -burn 1 \
           -co 'COMPRESS=LZW' -co 'PREDICTOR=2' -co 'BIGTIFF=YES' \
           -ot Byte \
           -a_nodata 255 \
           -tr " + res_str + " \
           -l all_roads_proj all_roads_proj.shp roads_" + area + ".tif"
    os.system(cmd)

# Loop on areas of interest
for i in range(5):
    projection = os.path.join(owd, proj[i])
    roads_osm(planet, area[i], extent[i], projection, 30)

# End
