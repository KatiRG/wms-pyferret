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

from flask import Flask, render_template, make_response, request, Response, session
# from app import index_add_counter

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
    return render_template('index.html', message='')

@app.route('/')
def index():
    session.clear()
    session['cart'] = [] #to store ferret commands
    session['img_cart'] = [] #to store img for later downloading
    

    return render_template('mapform.html')

dataset=''
@app.route('/', methods = ['POST', 'GET'])
def map_formhandler():

    dataset = str(request.form['dataset'])
    variable = str(request.form['mapvar'])
    command = request.form['ferretcmd']
    postvar = str(request.form['postvar'])

    session["cart"].append({'command': command, 'variable': variable, 'dataset': dataset, 'postvar': postvar})
    cmdArray = session['cart']
    print("cmdArray: ", cmdArray)
    
    nbMaps = len(cmdArray)
    listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

    return render_template('showmaps.html', cmdArray=cmdArray, listSynchroMapsToSet=listSynchroMapsToSet)


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
    print("############### DSET: ", DSET)

    tmpname = tempfile.NamedTemporaryFile(suffix='.png').name
    tmpname = os.path.basename(tmpname)

    # pyferret.run('go ' + envScript) # load the environment (dataset to open + variables definition)           
    # pyferret.run('use levitus_climatology')
    pyferret.run('use ' + DSET)

    if request.args.get('REQUEST') == 'GetColorBar':

                pyferret.run('set window/aspect=1/outline=0')
                # pyferret.run('set window/aspect=.7')
                pyferret.run('go margins 2 4 3 3')
                pyferret.run(COMMAND + '/set_up ' + VARIABLE)
                pyferret.run('ppl shakey 1, 0, 0.15, , 3, 9, 1, `($vp_width)-1`, 1, 1.25 ; ppl shade')
                pyferret.run('frame/format=PNG/transparent/xpixels=400/file="' + tmpdir + '/key' + tmpname + '"')

                print('tmpname: ', 'key' + tmpname)

                im = Image.open(tmpdir + '/key' + tmpname)
                box = (0, 325, 400, 375)
                area = im.crop(box)
                area.save(tmpdir + '/' + tmpname, "PNG")

                #store img before erasing
                session["img_cart"] = tmpdir + '/key' + tmpname
                print("session['img_cart'] in GetColorBar: ", session['img_cart'])
                print("session['cart'] in GetColorBar: ", session['cart'])


    elif request.args.get('REQUEST') == 'GetMap':
        
        #Define pyferret variables for 'REQUEST' == 'GetMap'
        BBOX = request.args.get('BBOX')
        BBOX = BBOX.split(',')
    
        WIDTH = int(request.args.get('WIDTH'))
        HEIGHT = int(request.args.get('HEIGHT'))

        HLIM = '/hlim=' + str(BBOX[0]) + ':' + str(BBOX[2])
        VLIM = '/vlim=' + str(BBOX[1]) + ':' + str(BBOX[3])
        
        # need to cycle through 6 BBOX coords
        # bboxArray = [ [-90, 0, 0, 90], [0, 0, 90, 90], [-180, 0, -90, 90], [-90, -90, 0, 0], 
        # [0, -90, 90, 0], [-180, -90, -90, 0] ]

        # pyferret.run('use levitus_climatology') #to load a second dataset, then use d=2 in command line
        #shade/x=-180:180/y=-90:90/lev=20v/pal=mpl_PSU_inferno temp[k=@min, d=1]

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
        pyferret.run('cancel mode meta')
        print("*************** file: ", tmpdir + '/' + tmpname)

    if os.path.isfile(tmpdir + '/' + tmpname):
        ftmp = open(tmpdir + '/' + tmpname, 'rb')
        img = ftmp.read()               
        ftmp.close()

        # #store img before erasing
        # session["img_cart"].append({'img': img})
        # imgArray = session['img_cart']
        # print("imgArray: ", imgArray)
        os.remove(tmpdir + '/' + tmpname)
    
    resp = Response(iter(img), status=200, mimetype='image/png')
    return resp

# Download map to file

# http://code.runnable.com/UiIdhKohv5JQAAB6/how-to-download-a-file-generated-on-the-fly-in-flask-for-python
@app.route('/download')
def download():
    print("session img_cart: ", session["img_cart"])
    png_img=session['img_cart']

    # csv = """"REVIEW_DATE","AUTHOR","ISBN","DISCOUNTED_PRICE"
    #         "1985/01/21","Douglas Adams",0345391802,5.95
    #         "1990/01/12","Douglas Hofstadter",0465026567,9.95
    #         "1998/07/15","Timothy ""The Parser"" Campbell",0968411304,18.99
    #         "1999/12/03","Richard Friedman",0060630353,5.95
    #         "2004/10/04","Randel Helms",0879755725,4.50"""


    # http://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
    with open(png_img, 'rb') as image_file:
        def wsgi_app(environ, start_response):
            start_response('200 OK', [('Content-type', 'image/png')])
            return image_file.read()
        response = make_response(wsgi_app)
        response.headers["Content-Disposition"] = "attachment; filename=test.png"
        return response
    
    

    

    

# Reproduces PB's code for two slippymaps (e.g. page_01.html)

# http://blog.luisrei.com/articles/flaskrest.html
@app.route('/slippymaps_maplayer', methods = ['GET', 'POST'])
def api_slippymaps_maplayer():
    nbMaps = 2 #fixed number of maps already on the screen

    # print("REQUEST IN MAPLAYER: ", request.args)
    # print("fields['REQUEST']: ", request.args.get('REQUEST'))

    if request.method == 'POST':
        nummaps = int(request.form['nummaps'])
        print("########### global nbMaps: ", nbMaps)
        print("########### nummaps: ", nummaps)
        listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+nummaps+1), 2))
        print("############# listSynchroMapsToSet in POST: ", listSynchroMapsToSet)

        return render_template('slippymaps.html', listSynchroMapsToSet=listSynchroMapsToSet, nbMaps=nbMaps, nummaps=nummaps)

    elif request.method == 'GET':
    # if request.method == 'GET':
        try:

            if request.args.get('SERVICE') != 'WMS':
                raise

            listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

            # environ commands from original script
            # MultiDict([('SERVICE', 'WMS'), ('REQUEST', 'GetMap'), ('LAYERS', ''), ('STYLES', ''), 
            # ('FORMAT', 'image/png'), ('TRANSPARENT', 'true'), ('VERSION', '1.1.1'), 
            # ('COMMAND', 'shade/x=-180:180/y=-90:90/lev=20v/pal=mpl_PSU_inferno'), 
            # ('VARIABLE', 'temp[k=@max]'), ('HEIGHT', '256'), ('WIDTH', '256'), 
            # ('SRS', 'EPSG:4326'), ('BBOX', '0,-90,90,0')])

            # GET params from URL:
            # http://localhost:8000/slippymaps_maplayer?
            # SERVICE=WMS&
            # REQUEST=GetMap&
            # LAYERS=&
            # STYLES=&
            # FORMAT=image%2Fpng&
            # TRANSPARENT=true&
            # VERSION=1.1.1&
            # COMMAND=shade%2Fx%3D-180%3A180%2Fy%3D-90%3A90%2Flev%3D20v%2Fpal%3Dmpl_PSU_inferno&VARIABLE=temp%5Bk%3D%40max%5D&
            # HEIGHT=256&
            # WIDTH=256&
            # SRS=EPSG%3A4326&
            # BBOX=-90,0,0,90

            COMMAND = str(request.args.get('COMMAND'))
            VARIABLE = str(request.args.get('VARIABLE'))

            tmpname = tempfile.NamedTemporaryFile(suffix='.png').name
            tmpname = os.path.basename(tmpname)

            # pyferret.run('go ' + envScript) # load the environment (dataset to open + variables definition)           
            pyferret.run('use levitus_climatology')

            if request.args.get('REQUEST') == 'GetColorBar':                
                print("GetColorBar COMMAND: ", COMMAND)
                print("GetColorBar VARIABLE: ", VARIABLE)

                pyferret.run('set window/aspect=1/outline=0')
                pyferret.run('go margins 2 4 3 3')
                pyferret.run(COMMAND + '/set_up ' + VARIABLE)
                pyferret.run('ppl shakey 1, 0, 0.15, , 3, 9, 1, `($vp_width)-1`, 1, 1.25 ; ppl shade')
                pyferret.run('frame/format=PNG/transparent/xpixels=400/file="' + tmpdir + '/key' + tmpname + '"')

                im = Image.open(tmpdir + '/key' + tmpname)
                box = (0, 325, 400, 375)
                area = im.crop(box)
                area.save(tmpdir + '/' + tmpname, "PNG")


            elif request.args.get('REQUEST') == 'GetMap':
                print("GetMap COMMAND: ", COMMAND)
                print("GetMap VARIABLE: ", VARIABLE)
                
                #Define pyferret variables for 'REQUEST' == 'GetMap'                
                # BBOX = environ['BBOX']
                BBOX = request.args.get('BBOX')
                BBOX = BBOX.split(',')
            
                WIDTH = int(request.args.get('WIDTH'))
                HEIGHT = int(request.args.get('HEIGHT'))

                HLIM = '/hlim=' + str(BBOX[0]) + ':' + str(BBOX[2])
                VLIM = '/vlim=' + str(BBOX[1]) + ':' + str(BBOX[3])
                
                # need to cycle through 6 BBOX coords
                # bboxArray = [ [-90, 0, 0, 90], [0, 0, 90, 90], [-180, 0, -90, 90], [-90, -90, 0, 0], 
                # [0, -90, 90, 0], [-180, -90, -90, 0] ]

                # pyferret.run('use levitus_climatology') #to load a second dataset, then use d=2 in command line
                #shade/x=-180:180/y=-90:90/lev=20v/pal=mpl_PSU_inferno temp[k=@min, d=1]

                pyferret.run('set window/aspect=1/outline=5')
                pyferret.run('go margins 0 0 0 0')    
                pyferret.run(COMMAND +  '/noaxis/nolab/nokey' + HLIM + VLIM + ' ' + VARIABLE)    
                pyferret.run('frame/format=PNG/transparent/xpixels=' + str(WIDTH) + '/file="' + tmpdir + '/' + tmpname + '"')                

            if os.path.isfile(tmpdir + '/' + tmpname):
                ftmp = open(tmpdir + '/' + tmpname, 'rb')
                img = ftmp.read()               
                ftmp.close()
                os.remove(tmpdir + '/' + tmpname)
            
            resp = Response(iter(img), status=200, mimetype='image/png')
            return resp

        except:
            return iter('Exception caught')
   

@app.route('/slippymaps', methods = ['GET', 'POST'])
def slippymaps():
    # global nbMaps
    nbMaps = 2
    listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

    return render_template('slippymaps.html', listSynchroMapsToSet=listSynchroMapsToSet, nbMaps=nbMaps, nummaps='')

    

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