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

#==============================================================
def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

#==============================================================
def handler_app(environ, start_response):

    fields = parse_formvars(environ)
    if environ['REQUEST_METHOD'] == 'GET':
        
        try:
		if fields['SERVICE'] != 'WMS':
			raise

        	COMMAND = fields['COMMAND']
        	VARIABLE = fields['VARIABLE'].replace('%2B','+')

        	pyferret.run('go ' + envScript)                 # load the environment (dataset to open + variables definition)

                tmpname = tempfile.NamedTemporaryFile(suffix='.png').name
                tmpname = os.path.basename(tmpname)

		#print(fields['REQUEST'] + ': ' + COMMAND + ' ' + VARIABLE)

		if fields['REQUEST'] == 'GetColorBar':
                	pyferret.run('set window/aspect=1/outline=0')
                	pyferret.run('go margins 2 4 3 3')
                	pyferret.run(COMMAND + '/set_up ' + VARIABLE)
                	pyferret.run('ppl shakey 1, 0, 0.15, , 3, 9, 1, `($vp_width)-1`, 1, 1.25 ; ppl shade')
                	pyferret.run('frame/format=PNG/transparent/xpixels=400/file="' + tmpdir + '/key' + tmpname + '"')

                	im = Image.open(tmpdir + '/key' + tmpname)
                	box = (0, 325, 400, 375)
                	area = im.crop(box)
                	area.save(tmpdir + '/' + tmpname, "PNG")

		elif fields['REQUEST'] == 'GetMap':
        		WIDTH = int(fields['WIDTH'])
        		HEIGHT = int(fields['HEIGHT'])

        		# BBOX=xmin,ymin,xmax,ymax
        		BBOX = fields['BBOX'].split(',')

        		HLIM = '/hlim=' + BBOX[0] + ':' + BBOX[2]
        		VLIM = '/vlim=' + BBOX[1] + ':' + BBOX[3]

        		pyferret.run('set window/aspect=1/outline=5')           # outline=5 is a strange setting but works otherwise get outline around polygons
        		pyferret.run('go margins 0 0 0 0')
                	pyferret.run(COMMAND +  '/noaxis/nolab/nokey' + HLIM + VLIM + ' ' + VARIABLE)
                	pyferret.run('frame/format=PNG/transparent/xpixels=' + str(WIDTH) + '/file="' + tmpdir + '/' + tmpname + '"')

		else:
			raise

                if os.path.isfile(tmpdir + '/' + tmpname):
                        ftmp = open(tmpdir + '/' + tmpname, 'rb')
                        img = ftmp.read()
                        ftmp.close()
                        os.remove(tmpdir + '/' + tmpname)
      
                start_response('200 OK', [('content-type', 'image/png')])
                return iter(img) 
    
        except:
                return iter('Exception caught')

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

else:
	if len(args) != 1:
        	parser.error("Wrong number of arguments")
		parser.print_help()

	if (mapWidth < 200 or mapWidth > 600) or (mapHeight < 200 or mapHeight > 600):
		parser.error("Map size options incorrect (200 <= size,width,height <= 600)")
		parser.print_help()
		sys.exit(1)
	
	if not os.path.isfile(envScript):
		parser.error("Environment script option missing")
		parser.print_help()
		sys.exit(1)
	
	cmdsRequested = args[0]
	
	cmds = cmdsRequested.split(';')		# get individual commands
	cmds = map(str.strip, cmds)  		# remove surrounding spaces if present
	
	nbMaps = len(cmds)
	print(str(nbMaps) + ' maps to draw')
	
	if nbMaps > 4:
		print("\n=======> Error: Maximum number of maps: 4\n")
		parser.print_help()
		sys.exit(1)
	
	# create array of dict {'command', 'variable'}
	for i,cmd in enumerate(cmds, start=1):
		# Get command
		command = cmd.split(' ')[0]			
		# Get variable
		variable = ' '.join(cmd.split(' ')[1:])
		cmdArray.append({'command': command, 'variable': variable})

#------------------------------------------------------
options = {
    'bind': '%s:%s' % ('127.0.0.1', '8000'),
    'workers': number_of_workers(),
    'worker_class': 'sync',
    'threads': 1 
}
StandaloneApplication(handler_app, options).run()

sys.exit(1)