
Patrick Brockmann - LSCE

<hr>
2016/09/20

Depending the number of commands separated by ; passed as argument, you can now get until 3 synchroneous maps
with colorbars (keys) made from qualifiers requested.

```
Usage: pyferretWMS.py [--width=400] [--height=400] 'cmd; cmd'

Options:
  --version        show program's version number and exit
  -h, --help       show this help message and exit
  --width=WIDTH    300 < map width <= 600
  --height=HEIGHT  300 < map height <= 600


./pyferretWMS.py 'shade/lev=(-inf)(-10,30,1)(inf)/pal=mpl_PSU_inferno temp[k=@max]; shade/lev=(-inf)(0,140,5)(inf)/pal=mpl_Seq1_YlGnBu_r temp[k=@var]; shade/lev=(-inf)(30,40,0.5)(inf)/pal=mpl_PSU_viridis salt[k=1]'
```

produces
![Capture](https://github.com/PBrockmann/wms-pyferret/raw/master/capture_02.png)


<hr>
2016/09/16

Slippy map is now made from multiple workers. Problem: the dataset and variables if defined
should be passed somehow to the workers. I haven't found yet how to enherit from the calling
environment.

Also how this should be called ? From a external function ? As a new command ?

Speed for creating tiles is also an issue especially when you work with a curvilinear grid quite large
(1440x1021), even with several workers.

<hr>
2016/09/09

You can now get slippy maps by a simple ```import pyferretWMS``` and a call to ```pyferretWMS.slippyMap()```.
It is made possible because the gunicorn is now launched directly from python and not anymore from command line. 
All temporary files (png tiles and the html + package.json for the nw application)
are cleaned properly when exiting (either by closing the client application or by typing "CTRL+C" when launched from a python script).

Test it quicky from:
```python pyferretWMS_test.py 'shade/lev=(-inf)(-10,30,1)(inf)/pal=mpl_PSU_plasma temp[k=@max]'```

<hr>
2016/09/06

The idea developed in this early prototype is to render variables read and computed from pyferret as slippy maps.
This can be done directly from the memory without having to save them in netCDF files 
and expose them through a Thredds server to get a Web Map Service.

The tiles are generated by "workers" from a gunicorn server, a python WSGI HTTP server,
and they use pyferret for the rendering. You can then use the classic ferret syntax to display
your variable in a fully pan-and-zoom environment.

Slippy maps avoid the command-line typing and display loops and hopefully will help us on model analysis. 
Moreover, considering that nowdays models are becoming incredibily refined with sometimes resolutions at 1/12°.
That makes the pan/zoom navigation even more useful.

![Capture](https://github.com/PBrockmann/wms-pyferret/raw/master/capture_01.png)

![Screencast](https://github.com/PBrockmann/wms-pyferret/raw/master/screencast_01.mkv)

Next steps:
- Read variables and start the gunicorn server directly from pyferret ([Custom Application](http://docs.gunicorn.org/en/stable/custom.html)).
- Propose synchronous maps when 2 (or more) variables are requested to allow direct spatial intercomparison.

Prerequisites:
- pyferret 7.0
- gunicorn
- nw.js

Examples of calls:
- ```./slippy_map.bash 'shade/lev=(-inf)(-10,30,1)(inf)/pal=mpl_PSU_viridis temp[k=@max]'```
- ```./slippy_map.bash 'shade/lev=(-inf)(30,40,1)(inf)/pal=mpl_PSU_inferno salt[k=1]'```

Work based on:
- [OpenGIS® Web Map Service Interface Standard (WMS)] (http://www.opengeospatial.org/standards/wms)
- [pyferret] (http://ferret.pmel.noaa.gov/Ferret/documentation/pyferret)
- [gunicorn: a Python WSGI HTTP Server] (http://gunicorn.org)
- [WMS in Leaflet] (http://leafletjs.com/examples/wms/wms.html)
- [Node-Webkit] (http://nwjs.io)
