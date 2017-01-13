
###Web application to display synchronous slippy maps using a Web Map Service (WMS) provided by pyferret
*Cathy Nangini - LSCE, adapted from Patrick Brockmann - LSCE*

####Motivation
Allows users to interactively generate map data on-the-fly and render them on maps that can be zoomed and panned (i.e. slippy maps).

This application is based on the Flask python framework, Gunicorn, a Python WSGI HTTP Server that uses "workers" to generate map tiles, and pyferret that renders the map data.


Palettes used are available from: http://www.pmel.noaa.gov/maillists/tmap/ferret_users/fu_2015/msg00475.html
or from https://github.com/PBrockmann/fast

####Requirements
* **pyferret** which can be installed in the usual way from http://ferret.pmel.noaa.gov/Ferret/downloads/pyferret/
or by the conda-forge channel from https://anaconda.org/conda-forge/pyferret
* **gunicorn** (http://gunicorn.org) release 19.6.0 to be installed with conda:
```
conda install gunicorn
```
* **nwjs** (http://nwjs.io/downloads/), choose the stable release.

####Installation notes
* nw should be accessible from your $PATH environment variable
* on Mac OS X: nwjs should be renamed nw and accessible with the $PATH environment variable (or changed in pyferretWMS.py)

####Work based on
- [OpenGIS® Web Map Service Interface Standard (WMS)] (http://www.opengeospatial.org/standards/wms)
- [pyferret] (http://ferret.pmel.noaa.gov/Ferret/documentation/pyferret)
- [gunicorn: a Python WSGI HTTP Server] (http://gunicorn.org)
- [WMS in Leaflet] (http://leafletjs.com/examples/wms/wms.html)
- [Node-Webkit] (http://nwjs.io)
- [Synchronous maps] (https://github.com/turban/Leaflet.Sync)

