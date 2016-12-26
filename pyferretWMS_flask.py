#!/usr/bin/env python

from __future__ import print_function

import multiprocessing

import gunicorn.app.base
from gunicorn.six import iteritems

import os, sys
import re
import shutil
import tempfile
import pyferret
from paste.request import parse_formvars
import subprocess

from jinja2 import Template
import itertools
from PIL import Image

from flask import Flask, render_template, make_response, request, Response, session, redirect, url_for
# from app import index_add_counter

import bokeh #0.12.3
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components

# http://cfss.uchicago.edu/slides/week10_flaskPlotting.pdf
import random

# For bokeh plots
import pandas as pd
import os
import collections
from datetime import datetime as dt
from bokeh.models import DatetimeTickFormatter
from math import pi

#==============================================================
# Define flask app
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.before_request
def session_management():
    # make the session last indefinitely until it is cleared
    session.permanent = True

@app.route('/test')
def test_index():
    return render_template('index.html')

@app.route('/')
def index():

    print("request.method in / !!!!!!!!!!!: ", request.method)

    if request.method =='GET':
        if request.args.get('REQUEST') == 'ReplaceMap' or request.args.get('REQUEST') == 'DeleteMap':
            print("Request from edit!!!: ", request.args)
            mapnum = int(request.args.get('MAPNUM')) 
            dset = str(request.args.get('DSET'))
            postvar = str(request.args.get('POSTVAR'))
            command = str(request.args.get('COMMAND'))
            variable = str(request.args.get('VARIABLE'))

            # Remove map from cart
            del session['cart'][mapnum -1]

            # Add new map to cart
            if request.args.get('REQUEST') == 'ReplaceMap':
                session["cart"].append({'command': command, 'variable': variable, 'dset': dset, 'postvar': postvar})

        elif not request.args: #initialize on start-up
            session.clear()
            session['cart'] = [] #to store ferret commands
            listSynchroMapsToSet = ''
            print("Initialized session[cart]: ", session['cart'])

    print("session[cart] in / !!!!!!!!!!!: ", session['cart'])
    nbMaps = len(session['cart'])
    listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

    return render_template('showmaps.html', cmdArray=session['cart'], listSynchroMapsToSet=listSynchroMapsToSet)

@app.route('/', methods = ['POST', 'GET'])
def map_formhandler():

    print("session[cart] in map_formhandler BEFORE: ", session['cart'])

    # print("request.form submit", request.form['submit'])
    if request.method =='POST':
        dset = str(request.form['DSET'])
        variable = str(request.form['VARIABLE'])
        command = request.form['COMMAND']
        postvar = str(request.form['POSTVAR'])
        # Add form input to session variable   
        session["cart"].append({'command': command, 'variable': variable, 'dset': dset, 'postvar': postvar})

    nbMaps = len(session['cart'])    #len(cmdArray)
    listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

    print("session[cart] in map_formhandler AFTER: ", session['cart'])

    return render_template('showmaps.html', cmdArray=session['cart'], listSynchroMapsToSet=listSynchroMapsToSet)


@app.route('/showmaps_resource', methods=['POST','GET'])
def api_calcmaps():

    # ImmutableMultiDict([('LAYERS', u''), ('STYLES', u''), ('WIDTH', u'256'), 
    # ('SERVICE', u'WMS'), ('FORMAT', u'image/png'), ('REQUEST', u'GetMap'), 
    # ('HEIGHT', u'256'), ('SRS', u'EPSG:4326'), ('VERSION', u'1.1.1'), 
    # ('COMMAND', u'shade/x=-180:180/y=-90:90/lev=20v/pal=mpl_PSU_inferno'), 
    # ('BBOX', u'0,-90,90,0'), ('VARIABLE', u'temp[k=@max]'), ('TRANSPARENT', u'true')])
    
    
    DSET = str(request.args.get('DSET'))
    POSTVAR = str(request.args.get('POSTVAR'))
    COMMAND = str(request.args.get('COMMAND'))
    VARIABLE = str(request.args.get('VARIABLE'))

    tmpname = tempfile.NamedTemporaryFile(suffix='.png').name
    tmpname = os.path.basename(tmpname)

    # pyferret.run('go ' + envScript) # load the environment (dset to open + variables definition)
    # print("starting pyferret.........................")
    # pyferret.start(journal=False, unmapped=True, quiet=False, verify=False)
    pyferret.run('use ' + DSET)
    # pyferret.run('show data/all')

    if request.args.get('REQUEST') == 'GetColorBar':

                pyferret.run('set window/aspect=1/outline=0')
                # pyferret.run('set window/aspect=.7')
                pyferret.run('go margins 2 4 3 3')
                pyferret.run(COMMAND + '/set_up ' + VARIABLE)
                pyferret.run('ppl shakey 1, 0, 0.15, , 3, 9, 1, `($vp_width)-1`, 1, 1.25 ; ppl shade')
                pyferret.run('frame/format=PNG/transparent/xpixels=400/file="' + tmpdir + '/key' + tmpname + '"')

                # print('tmpname: ', 'key' + tmpname)

                im = Image.open(tmpdir + '/key' + tmpname)
                box = (0, 325, 400, 375)
                area = im.crop(box)
                area.save(tmpdir + '/' + tmpname, "PNG")



    elif request.args.get('REQUEST') == 'GetMap':
        
        #Define pyferret variables for 'REQUEST' == 'GetMap'
        BBOX = request.args.get('BBOX')
        BBOX = BBOX.split(',')
    
        WIDTH = int(request.args.get('WIDTH'))
        HEIGHT = int(request.args.get('HEIGHT'))

        HLIM = '/hlim=' + str(BBOX[0]) + ':' + str(BBOX[2])
        VLIM = '/vlim=' + str(BBOX[1]) + ':' + str(BBOX[3])

        pyferret.run('set window/aspect=1/outline=5')
        pyferret.run('go margins 0 0 0 0')
        
        #For saving to file
        # pyferret.run('set mode meta')

        if POSTVAR:
            pyferret.run(COMMAND +  '/noaxis/nolab/nokey' + HLIM + VLIM + ' ' + VARIABLE + ',' + POSTVAR)
        else:
            pyferret.run(COMMAND +  '/noaxis/nolab/nokey' + HLIM + VLIM + ' ' + VARIABLE)
        
        #For saving to file
        pyferret.run('frame/format=PNG/transparent/xpixels=' + str(WIDTH) + '/file="' + tmpdir + '/' + tmpname + '"')
        # pyferret.run('cancel mode meta')
        # print("*************** file: ", tmpdir + '/' + tmpname)
        # pyferret.stop()
        # print("...................stopping pyferret")

    if os.path.isfile(tmpdir + '/' + tmpname):
        ftmp = open(tmpdir + '/' + tmpname, 'rb')
        img = ftmp.read()
        ftmp.close()    
        os.remove(tmpdir + '/' + tmpname)
    
    resp = Response(iter(img), status=200, mimetype='image/png')
    return resp

# Download timeseries to file
# http://code.runnable.com/UiIdhKohv5JQAAB6/how-to-download-a-file-generated-on-the-fly-in-flask-for-python
@app.route('/download')
def download_ts():
    print("request.args in download_ts: ", request.args)

    if request.args.get('REQUEST') == 'SaveTimeseries':
        BDS = str(request.args.get('BDS')) #[east, west, north, south]
        DSET = str(request.args.get('DSET'))
        VARIABLE = str(request.args.get('VARIABLE'))
        VARIABLE = VARIABLE.split('[', 1)[0]


        east = BDS.split(',',1)[0]
        west = BDS.split(',',2)[1]
        north = BDS.split(',',3)[2]
        south = BDS.split(',',4)[3]

        pyferret.run('use ' + DSET)
        # junk='LIST/FILE=' + tmpdir + '/ts.dat ' + VARIABLE + '[x=' + east + ':' + west + '@ave,y=' + south + ':' + north + '@ave]'
        # print('junk: ', junk)
        # http://ferret.pmel.noaa.gov/Ferret/documentation/users-guide/commands-reference/LIST
        #LIST/FILE=file.dat uwnd[x=20:160@ave,y=0:45@ave]

        # Store timeseries file in current working dir since saving to tmp dir gives error        
        pyferret.run('LIST/FILE=ts.dat ' + VARIABLE + '[x=' + east + ':' + west + '@ave,y=' + south + ':' + north + '@ave]')
        # pyferret.run('LIST/FILE=' + tmpdir + '/ts.dat ' + VARIABLE + '[x=' + east + ':' + west + '@ave,y=' + south + ':' + north + '@ave]')

        # pyferret.run('frame/format=PNG/transparent/xpixels=400/file="' + tmpdir + '/key' + tmpname + '"')

        ftmp = open('ts.dat', 'rb')
        ts_csv = ftmp.read()
        ftmp.close()    

        # http://stackoverflow.com/questions/30024948/flask-download-a-csv-file-on-clicking-a-button
        return Response(
            ts_csv,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=timeseries.csv"}
            )
   
@app.route('/edit/<path:urlpath>', methods=['POST','GET'])
def edit_map(urlpath):
    try:
        print("urlpath: ", urlpath)
        url_split = urlpath.split("&")
        print("url_split: ", url_split)
        mapnum=int(urlpath.split("&")[0])
        dset=str(urlpath.split("&")[1])
        variable=str(urlpath.split("&")[2])
        command=str(urlpath.split("&")[3])
        postvar=str(urlpath.split("&")[4])

        print("from URL: ", str(mapnum) + ", " + dset + ", " + variable)

        if request.method=='POST':
           
            print("POST request.form: ", request.form)
            print("request.form submit", request.form['submit_type'])
            
            if request.form['submit_type'] == "Preview":
                dset = str(request.form['dset'])
                variable = str(request.form['mapvar'])
                command = request.form['ferretcmd']
                postvar = str(request.form['postvar'])
                
                return render_template("editmap.html", mapnum=mapnum, dset=dset, variable=variable, command=command, postvar=postvar)
            
        else: #display chosen map to be edited            
            return render_template("editmap.html", mapnum=mapnum, dset=dset, variable=variable, command=command, postvar=postvar)
    
    except Exception, e:
        return(str(e))

@app.route('/junk')
def bokehPlot():
    # generate some random integers, sorted
    exponent = .7 + random.random()*.6
    dta = []
    for i in range(50):
        rnum = int((random.random()*10)**exponent)
        dta.append(rnum)
    y = sorted(dta)
    x = range(len(y))

    print("bokeh x: ", x)
    print("bokeh y: ", y)

    # generate Bokeh HTML elements
    # create a `figure` object
    p = figure(title='A Bokeh plot',
        plot_width=500,plot_height=400)
    # add the line
    p.line(x,y)
    # add axis labels
    p.xaxis.axis_label = "time"
    p.yaxis.axis_label = "size"
    # create the HTML elements to pass to template
    figJS,figDiv = components(p,CDN)

    return (render_template('figures.html',
        y=y,
        figJS=figJS,figDiv=figDiv
        ))

# http://stackoverflow.com/questions/33869292/how-can-i-set-the-x-axis-as-datetimes-on-a-bokeh-plot
@app.route('/junk2')
def bokehDatePlot():
    df = pd.DataFrame(data=[1,2,3],
                  index=[dt(2015, 1, 1), dt(2015, 1, 2), dt(2015, 1, 3)],
                  columns=['foo'])

    print("df: ", df)

    # generate Bokeh HTML elements
    # create a `figure` object
    p = figure(title='A Bokeh plot',
        plot_width=500,plot_height=400)
    # add the line
    x=df.index
    y=df['foo']
    print("x: ", x)
    print("y: ", y)
    p.line(x, y)

    # add axis labels
    # p.xaxis.axis_label = "time"
    p.xaxis.formatter=DatetimeTickFormatter(formats=dict(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    ))
    p.xaxis.major_label_orientation = pi/4
    


    p.yaxis.axis_label = "size"


    # create the HTML elements to pass to template
    figJS,figDiv = components(p,CDN)

    return (render_template('figures.html',
        y=y,
        figJS=figJS,figDiv=figDiv
        ))

@app.route('/timeseries/<path:urlpath>')
def render_timeseries(urlpath):
    try:
        print("urlpath: ", urlpath)
        url_split = urlpath.split("&")
        print("url_split: ", url_split)
        mapnum=int(urlpath.split("&")[0])
        dset=str(urlpath.split("&")[1])
        variable=str(urlpath.split("&")[2])
        bds = str(urlpath.split("&")[3])
        
        return render_template("showts.html", mapnum=mapnum, dset=dset, variable=variable, bds=bds)
    except Exception, e:
        return(str(e))      
             
@app.route('/showts_resource', methods=['GET'])
def calc_timeseries():
    print("request.args in showts_resource: ", request.args)

    
    # if request.args.get('REQUEST') == 'CalcTimeseries':
    BDS = str(request.args.get('BDS')) #[east, west, north, south]
    DSET = str(request.args.get('DSET'))
    VARIABLE = str(request.args.get('VARIABLE'))
    VARIABLE = VARIABLE.split('[', 1)[0]
    
    east = BDS.split(',',1)[0]
    west = BDS.split(',',2)[1]
    north = BDS.split(',',3)[2]
    south = BDS.split(',',4)[3]
    
    tmpname = 'somename.png'
    
    #Calculate timeseries and return as PNG file
    # plot uwnd[x=20:160@ave,y=0:45@ave]
    pyferret.run('use ' + DSET)
    pyferret.run('show data/all')
    # pyferret.run('set window/aspect=1/outline=5')
    # pyferret.run('go margins 0 0 0 0')
    pyferret.run('plot ' + VARIABLE + '[x=' + east + ':' + west + '@ave,y=' + south + ':' + north + '@ave]')    
    pyferret.run('frame/format=PNG/transparent/xpixels=' + '256' + '/file="' + tmpdir + '/' + tmpname +  '"')
             
    if os.path.isfile(tmpdir + '/' + tmpname):
        ftmp = open(tmpdir + '/' + tmpname, 'rb')
        img = ftmp.read()
        ftmp.close()        
        os.remove(tmpdir + '/' + tmpname)
    
    resp = Response(iter(img), status=200, mimetype='image/png')
    return resp

    
#==============================================================
def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

#==============================================================
class myArbiter(gunicorn.arbiter.Arbiter):

    def halt(self):
	# Close pyferret
        pyferret.stop()

    	print('Removing temporary directory: ', tmpdir)
    	shutil.rmtree(tmpdir)

        #REMOVE TS FILE IN ROOT DIR -- HACK
        os.remove('ts.dat')

        super(myArbiter, self).halt()


#==============================================================
class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):

	    # Start pyferret	
        pyferret.start(journal=False, unmapped=True, quiet=True, verify=False)

    	master_pid = os.getpid()
    	print('---------> gunicorn master pid: ', master_pid)    

        self.options = options or {}
        self.application = app

        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

# if control before exiting is needed
    def run(self):
        try:
            myArbiter(self).run()
        except RuntimeError as e:
            print('\nError: %s\n' % e, file=sys.stderr)
            sys.stderr.flush()
	    sys.exit(1)


#==============================================================
from optparse import OptionParser

#------------------------------------------------------
usage = "%prog [--env=script.jnl] [--width=400] [--height=400] [--size=value] [--center=[0,0]] [--zoom=1] [--server]" + \
	"\n                              'cmd/qualifiers variable; cmd/qualifiers variable'" + \
	"\n\n'cmd/qualifiers variable' is a classic ferret call (no space allowed except to" + \
	"\nseparate the variable from the command and its qualifiers). The semi-colon character ';'" +\
	"\nis the separator between commands and will determine the number of maps to be drawn." + \
	"\nThe qualifiers can include the title qualifier considering that the space character" + \
	"\nis not allowed since used to distinguish the cmd/qualifiers and the variable(s)." + \
	"\nFor this, you can use the HTML code '&nbsp' for the non-breaking space (without the ending semi-colon)." + \
	"\nFor example: 'shade/lev=20/title=Simulation&nbspA varA; shade/lev=20/title=Simulation&nbspB varB'"

version = "%prog 0.9.5"

#------------------------------------------------------
parser = OptionParser(usage=usage, version=version)

parser.add_option("--width", type="int", dest="width", default=400,
		help="200 < map width <= 600")
parser.add_option("--height", type="int", dest="height", default=400,
		help="200 < map height <= 600")
parser.add_option("--size", type="int", dest="size",
		help="200 < map height and width <= 600")
parser.add_option("--env", dest="envScript", default="pyferretWMS.jnl",
		help="ferret script to set the environment (default=pyferretWMS.jnl). It contains datasets to open, variables definition.")
parser.add_option("--center", type="string", dest="center", default='[0,-40]',
		help="Initial center of maps as [lat, lon] (default=[0,-40])")
parser.add_option("--zoom", type="int", dest="zoom", default=1,
		help="Initial zoom of maps (default=1)")
parser.add_option("--server", dest="serverOnly", action="store_true", default=False,
		help="Server only (default=False)")

(options, args) = parser.parse_args()

if options.size:
	mapHeight = options.size
	mapWidth = options.size
else:
	mapHeight = options.height
	mapWidth = options.width

mapCenter = options.center
mapZoom = options.zoom
envScript = options.envScript
serverOnly = options.serverOnly

#------------------------------------------------------
# Global variables
nbMaps = 0
cmdArray = []
tmpdir = tempfile.mkdtemp()

print('Temporary directory to remove: ', tmpdir)

#------------------------------------------------------
if serverOnly:
	if len(args) != 0:
        	parser.error("No argument needed in mode server")
		parser.print_help()

#------------------------------------------------------
options = {
    'bind': '%s:%s' % ('127.0.0.1', '8000'),
    'workers': number_of_workers(),
    'worker_class': 'sync',
    'threads': 1 
}

# Pass flask app directly to StandaloneApplication()
# Idea came from run_simple here http://flask.pocoo.org/docs/0.11/patterns/appdispatch/
#StandaloneApplication(handler_app, options).run()
StandaloneApplication(app, options).run()

sys.exit(1)