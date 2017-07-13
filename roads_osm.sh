#!/usr/bin/bash

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ghislainv.github.io
# GDAL version    :2.1.2 (OGR enabled)
# osmtools        :https://gitlab.com/osm-c-tools/osmctools
# license         :GPLv3
# ==============================================================================

# Variables
#proj="EPSG:102022" # Africa_Albers_Equal_Area_Conic, see http://epsg.io
#This epsg code is not recognized by gdal so we use WKT definition
proj="../proj.prj" # Path to file with Well Known Text (WKT) projection definition
resolution=30 # 30m resolution

# ===========================
# Roads from Open Street Map
# ===========================

# Message
echo "Roads from OSM\n"

# New directory for results
mkdir -p results
cd results

# Download OSM data from Geofabrik
url="http://download.geofabrik.de/africa-latest.osm.pbf"
wget -O country.osm.pbf $url
osmconvert country.osm.pbf -o=country.o5m

# All roads
osmfilter country.o5m --keep='highway=*' > all_roads.osm
ogr2ogr -overwrite -skipfailures -f 'ESRI Shapefile' -progress \
        -sql 'SELECT osm_id, name, highway FROM lines WHERE highway IS NOT NULL' \
        -lco ENCODING=UTF-8 all_roads.shp all_roads.osm

# Reproject
ogr2ogr -overwrite -s_srs EPSG:4326 -t_srs $proj -f 'ESRI Shapefile' \
        -lco ENCODING=UTF-8 all_roads_proj.shp all_roads.shp

# Rasterize
gdal_rasterize -tap -burn 1 \
               -co "COMPRESS=LZW" -co "PREDICTOR=2" -co "BIGTIFF=YES" -ot Byte \
               -a_nodata 255 \
               -tr $resolution $resolution -l all_roads_proj all_roads_proj.shp all_roads.tif

# End
