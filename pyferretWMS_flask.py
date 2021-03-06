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

from flask import Flask, render_template, make_response, request, Response, session, url_for

# For bokeh plots
import pandas as pd
import bokeh #0.12.3
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components
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
   
    if request.method =='GET':
        if request.args.get('REQUEST') == 'ReplaceMap' or request.args.get('REQUEST') == 'DeleteMap':
            mapnum = int(request.args.get('MAPNUM')) 
            dset = str(request.args.get('DSET'))
            postvar = str(request.args.get('POSTVAR'))
            command = str(request.args.get('COMMAND'))
            variable = str(request.args.get('VARIABLE'))

            # Replace same map with edited params
            if request.args.get('REQUEST') == 'ReplaceMap':
                session['cart'][mapnum-1]['dset'] = dset
                session['cart'][mapnum-1]['variable'] = variable
                session['cart'][mapnum-1]['command'] = command
                session['cart'][mapnum-1]['postvar'] = postvar

            # Delete requested map from session[cart]
            elif request.args.get('REQUEST') == 'DeleteMap':
                del session['cart'][mapnum -1]

        elif not request.args: #initialize on start-up
            session.clear()
            session['cart'] = [] #to store ferret commands
            listSynchroMapsToSet = ''


    nbMaps = len(session['cart'])
    listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

    return render_template('showmaps.html', cmdArray=session['cart'], listSynchroMapsToSet=listSynchroMapsToSet)

@app.route('/', methods = ['POST', 'GET'])
def map_formhandler():
    
    if request.method =='POST':
        dset = str(request.form['DSET'])
        variable = str(request.form['VARIABLE'])
        command = request.form['COMMAND']
        postvar = str(request.form['POSTVAR'])
        # Add form input to session variable   
        session["cart"].append({'command': command, 'variable': variable, 'dset': dset, 'postvar': postvar})

    nbMaps = len(session['cart'])    #len(cmdArray)
    listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

    return render_template('showmaps.html', cmdArray=session['cart'], listSynchroMapsToSet=listSynchroMapsToSet)


@app.route('/showmaps_resource', methods=['POST','GET'])
def api_calcmaps():
    
    DSET = str(request.args.get('DSET'))
    POSTVAR = str(request.args.get('POSTVAR'))
    COMMAND = str(request.args.get('COMMAND'))
    VARIABLE = str(request.args.get('VARIABLE'))

    tmpname = tempfile.NamedTemporaryFile(suffix='.png').name
    tmpname = os.path.basename(tmpname)

    pyferret.run('use ' + DSET)
   
    # pyferret.run('show data/all')

    if request.args.get('REQUEST') == 'GetColorBar':

                pyferret.run('set window/aspect=1/outline=0')
                pyferret.run('go margins 2 4 3 3')
                pyferret.run(COMMAND + '/set_up ' + VARIABLE)
                pyferret.run('ppl shakey 1, 0, 0.15, , 3, 9, 1, `($vp_width)+0`, 1, 1.25 ; ppl shade')
                pyferret.run('frame/format=PNG/xpixels=400/file="' + tmpdir + '/key' + tmpname + '"')

                im = Image.open(tmpdir + '/key' + tmpname)
                box = (0, 325, 400, 375)
                area = im.crop(box)
                area.save(tmpdir + '/' + tmpname, "PNG")

    elif request.args.get('REQUEST') == 'GetMap':
                
        BBOX = request.args.get('BBOX')
        BBOX = BBOX.split(',')
    
        WIDTH = int(request.args.get('WIDTH'))
        HEIGHT = int(request.args.get('HEIGHT'))

        HLIM = '/hlim=' + str(BBOX[0]) + ':' + str(BBOX[2])
        VLIM = '/vlim=' + str(BBOX[1]) + ':' + str(BBOX[3])

        pyferret.run('set window/aspect=1/outline=5')
        pyferret.run('go margins 0 0 0 0')
         

        if POSTVAR:
            pyferret.run(COMMAND + '/noaxis/nolab/nokey' + HLIM + VLIM + ' ' + VARIABLE + ',' + POSTVAR)
        else:
            pyferret.run(COMMAND + '/noaxis/nolab/nokey' + HLIM + VLIM + ' ' + VARIABLE)
        
        #For saving to file
        pyferret.run('frame/format=PNG/transparent/xpixels=' + str(WIDTH) + '/file="' + tmpdir + '/' + tmpname + '"')

    if os.path.isfile(tmpdir + '/' + tmpname):
        ftmp = open(tmpdir + '/' + tmpname, 'rb')
        img = ftmp.read()
        ftmp.close()    
        os.remove(tmpdir + '/' + tmpname)
    
    resp = Response(iter(img), status=200, mimetype='image/png')
    return resp

@app.route('/edit/<path:urlpath>', methods=['POST','GET'])
def edit_map(urlpath):
    try:
        
        url_split = urlpath.split("&")
        mapnum=int(urlpath.split("&")[0])
        dset=str(urlpath.split("&")[1])
        variable=str(urlpath.split("&")[2])
        command=str(urlpath.split("&")[3])
        postvar=str(urlpath.split("&")[4])

        if request.method=='POST':
            
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

@app.route('/timeseries/<path:urlpath>')
def bokeh_ts(urlpath):
    try:
        url_split = urlpath.split("&")
        mapnum=int(urlpath.split("&")[0])
        dset=str(urlpath.split("&")[1])
        variable=str(urlpath.split("&")[2]).split('[', 1)[0]
        bds = str(urlpath.split("&")[3])

        east = bds.split(',',1)[0]
        west = bds.split(',',2)[1]
        north = bds.split(',',3)[2]
        south = bds.split(',',4)[3]

        pyferret.run('use ' + dset)

        tmpname = tempfile.NamedTemporaryFile(suffix='.csv').name
        tmpname = os.path.basename(tmpname)
    
        # Store timeseries file in current working dir for now
        pyferret.run('list/file="' + tmpdir + '/' + tmpname + '"' + ' ' + variable + '[x=' + east + ':' + west + '@ave,y=' + south + ':' + north + '@ave]')       
       
        # Read in csv file        
        df = pd.read_csv(tmpdir + '/' + tmpname, delimiter=':', skiprows=5)

        # Extract date string from col 0
        s = df.ix[:, 0]
        x = s.str.split(' /').str.get(0).str.split(' ').str.get(1)

        # Determine if x-col is a list of dates
        months=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        dateFlag=0
        for idx in range(12):
            if x[0].find(months[idx]) != -1:
                dateFlag=1

        if dateFlag==1:
            # Convert to datetime
            x = pd.to_datetime(x, infer_datetime_format=True)

        # Put x and y values in dataframe
        dfer = pd.DataFrame()
        dfer['xval'] = x
        dfer['yval'] = df.ix[:, 1]

        # Bokeh plot
        title='Average timeseries for ' + dset + ' (' + east + 'E-' + west + 'W, ' + south + 'S-' + north + 'N)'
        p = figure(title=title,
                    plot_width=700,plot_height=400)
        p.line(dfer['xval'], dfer['yval'])

        # format axes
        if dateFlag==1:
            p.xaxis.formatter=DatetimeTickFormatter(formats=dict(
                hours=["%d %B %Y"],
                days=["%d %B %Y"],
                months=["%d %B %Y"],
                years=["%d %B %Y"],
            ))
        p.xaxis.major_label_orientation = pi/4
        p.yaxis.axis_label = "avg " + variable

        # create the HTML elements to pass to template
        figJS,figDiv = components(p,CDN)

        return (render_template('ts_bokeh.html',
            y=dfer['yval'],
            figJS=figJS,figDiv=figDiv,
            tmpname=tmpname
            ))

    except Exception, e:
        return(str(e))

# Download timeseries to file
@app.route('/download')
def download_ts():
    print("request.args in download_ts: ", request.args)

    if request.args.get('REQUEST') == 'SaveTimeseries':
        
        fname = request.args.get('FILENAME')

        ftmp = open(tmpdir + '/' + fname, 'rb')
        ts_csv = ftmp.read()
        ftmp.close()
                
        return Response(
            ts_csv,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=timeseries.csv"}
            )
    
#==============================================================
def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

#==============================================================
class myArbiter(gunicorn.arbiter.Arbiter):

    def halt(self):
	# Close pyferret
        pyferret.stop()

        print("current wdir before exit: ", os.getcwd())

    	print('Removing temporary directory: ', tmpdir)
    	shutil.rmtree(tmpdir)

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
tmpdir = []
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