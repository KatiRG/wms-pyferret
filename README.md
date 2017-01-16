
###Flask integration for wms-pyferret
*Cathy Nangini - LSCE*  
*built on the wms-pyferret project by Patrick Brockmann - LSCE*

Integrates the python micro-framework [Flask] (http://flask.pocoo.org/) into a [custom Gunicorn WSGI application] (http://docs.gunicorn.org/en/stable/custom.html) to manage the http requests. 

Provides an interface to input datasets and variables to be plotted on slippy maps generated on-the-fly by gunicorn workers to show data calculated by pyferret, as developed here:
https://github.com/PBrockmann/wms-pyferret.


####Features
* input form (dataset name, variable to be plotted, ferret command to use)
* add, edit, delete map
* plot timeseries over map coordinates in saveable Bokeh plot
* download timeseries data.

![Capture](https://github.com/KatiRG/wms-pyferret/raw/master/screenshot.png)


####Usage
```
$ ./pyferretWMS_flask.py --server
```

####Requirements
* **pyferret** which can be installed in the usual way from http://ferret.pmel.noaa.gov/Ferret/downloads/pyferret/
or by the conda-forge channel from https://anaconda.org/conda-forge/pyferret
* **gunicorn** (http://gunicorn.org) release 19.6.0
* **Flask** (http://flask.pocoo.org/), plus python modules such as [Bokeh](http://bokeh.pydata.org/en/latest/docs/installation.html) and [pandas](http://pandas.pydata.org/)