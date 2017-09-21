# Extract roads from OpenStreetMap (OSM)

## Code

This repository includes a Python script to extract roads from Open
Street Map (OSM). Computation relies on
[`osmtools`](https://gitlab.com/osm-c-tools/osmctools) and
[`GDAL/OGR`](<http://gdal.org>) utilities.

## Results

The code produces rasters of roads extracted from OSM for several
regions of the world. Each region has an extent and a projection. The
raster includes all types of roads (highway=*) provided by
OSM. Rasters of roads have the following characteristics:

Resolution: 30m. Format: GeoTIFF. Data type:Byte. No-data value: 255.

## Download

Rasters of roads are available on Figshare:
\[Roadless Forest project](https://figshare.com/account/home#/projects/24577)\].
