#!/usr/bin/env python

from __future__ import print_function

import multiprocessing

import gunicorn.app.base
from gunicorn.six import iteritems

import os, sys
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
        
        CMDarr = fields['CMD'].split()

        CMD = CMDarr[0].strip()                     # get the ferret command to append needed qualifiers
        VARIABLE = ' '.join(CMDarr[1:])             # 1 variable or 3 variables as var2D, lon2D, lat2D for curvilinear grids

        HEIGHT = int(fields['HEIGHT'])
        WIDTH = int(fields['WIDTH'])
    
        # BBOX=xmin,ymin,xmax,ymax
        BBOX = fields['BBOX'].split(',')

        hlim = '/hlim=' + BBOX[0] + ':' + BBOX[2]
        vlim = '/vlim=' + BBOX[1] + ':' + BBOX[3]

        try:

        	pyferret.run('set window/outline=5/aspect=1')           # outline=5 is a strange setting but works otherwise get outline around polygons
        	pyferret.run('go margins 0 0 0 0')

		# Dataset and variables definition need to be pass to workers (cannot be inherited from initial call)
        	pyferret.run('use levitus_climatology')
                pyferret.run(CMD +  '/x=-180:180/y=-90:90/noaxis/nolab/nokey' + hlim + vlim + ' ' + VARIABLE)
        
		# Curvilinear case to test with:
		# python pyferretWMS_test.py 'shade/lev=(-inf)(-10,30,1)(inf)/pal=mpl_PSU_viridis VOTEMPER[k=1,l=1], NAV_LON, NAV_LAT'
		#pyferret.run('use ORCA0.25_ex1.nc')
                #pyferret.run(CMD +  '/modulo/noaxis/nolab/nokey' + hlim + vlim + ' ' + VARIABLE)
       
                tmpname = tempfile.NamedTemporaryFile(suffix='.png').name
                tmpname = os.path.basename(tmpname)
                pyferret.run('frame/format=PNG/transparent/xpixels=' + str(WIDTH) + '/file="' + tmpdir + '/' + tmpname + '"')

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
	#shutil.rmtree(tmpdir)

        super(myArbiter, self).halt()


#==============================================================
class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
	global tmpdir
        tmpdir = tempfile.mkdtemp()
	print('Temporary directory to remove: ', tmpdir)

	master_pid = os.getpid()
	print('---------> gunicorn master pid: ', master_pid)

	nbMaps = len(cmds)
	print(str(nbMaps) + ' maps to draw')
	listSynchroMapsToSet = list(itertools.permutations(range(1,nbMaps+1), 2))

	instance_WMS_Client = Template(template_WMS_client())
	instance_NW_Package = Template(template_nw_package())
	with open(tmpdir + '/index.html', 'wb') as f:
    		f.write(instance_WMS_Client.render(cmds=cmds, gunicornPID=master_pid, listSynchroMapsToSet=listSynchroMapsToSet,
						   mapWidth=mapWidth, mapHeight=mapHeight))
	with open(tmpdir + '/package.json', 'wb') as f:
    		f.write(instance_NW_Package.render(nbMaps=nbMaps,
						   mapWidth=mapWidth, mapHeight=mapHeight))
	
    	proc = subprocess.Popen(['nw', tmpdir])
    	print('Client nw process: ', proc.pid)
        self.options = options or {}
        self.application = app

	# Start pyferret	
        pyferret.start(journal=False, unmapped=True, quiet=True)

	# Produce colobars (keys) as 400x400 image
	for i,cmd in enumerate(cmds, start=1):
		cmd1 = cmd.split(' ')[0]			# get command and variable to append /set_up qualifier
		variable = ' '.join(cmd.split(' ')[1:])
		print(cmd1, variable)
		pyferret.run('set window/aspect=1')
        	pyferret.run('use levitus_climatology')
		pyferret.run('go margins 2 4 3 3')
		pyferret.run(cmd1 + '/set_up ' + variable)
		pyferret.run('ppl shakey 1, 0, 0.15, , 3, 9, 1, `($vp_width)-1`, 1, 1.25 ; ppl shade')
		pyferret.run('frame/format=PNG/transparent/xpixels=400/file="' + tmpdir + '/key' + str(i) + '.png"')
		im = Image.open(tmpdir + '/key' + str(i) + '.png')
		box = (0, 325, 400, 375)	
		area = im.crop(box)
		area.save(tmpdir + '/skey' + str(i) + '.png', "PNG")

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
def template_WMS_client():

    return '''
<!doctype html>
<html>
<head>
    <meta charset='utf-8'>
    <title>Slippy map with WMS from pyferret</title>

    <link rel='stylesheet' href='http://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-rc.3/leaflet.css' />
    <script src='http://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-rc.3/leaflet.js'></script>

    <style type='text/css'>
        html, body { font-family: 'arial' }
        .mapContainer { display: inline-block ; margin-left: 20px; margin-top: 10px;}
        .cmd { font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width:  {{ mapWidth }}px; }
        .map { width: {{ mapWidth }}px; height: {{ mapHeight }}px; }
        .key { text-align: center; margin: auto; }
        .key img { width: {{ mapWidth }}px; height: auto; max-width: 400px; }
    </style>
</head>

<body>

{% for cmd in cmds %}
<div class='mapContainer'>
   <div id='cmd{{ loop.index }}' class='cmd' title='{{ cmd }}'>{{ cmd }}</div>
   <div id='map{{ loop.index }}' class='map'></div>
   <div id='key{{ loop.index }}' class='key'><img src='skey{{ loop.index }}.png'></img></div>
</div>
{% endfor %}

<script type='text/javascript'>
/*
 * Extends L.Map to synchronize the interaction on one map to one or more other maps.
 */

(function () {
    var NO_ANIMATION = {
        animate: false,
        reset: true
    };

    L.Map = L.Map.extend({
        sync: function (map, options) {
            this._initSync();
            options = L.extend({
                noInitialSync: false,
                syncCursor: false,
                syncCursorMarkerOptions: {
                    radius: 10,
                    fillOpacity: 0.3,
                    color: '#da291c',
                    fillColor: '#fff'
                }
            }, options);

            // prevent double-syncing the map:
            if (this._syncMaps.indexOf(map) === -1) {
                this._syncMaps.push(map);
            }

            if (!options.noInitialSync) {
                map.setView(this.getCenter(), this.getZoom(), NO_ANIMATION);
            }
            if (options.syncCursor) {
                map.cursor = L.circleMarker([0, 0], options.syncCursorMarkerOptions).addTo(map);

                this._cursors.push(map.cursor);

                this.on('mousemove', this._cursorSyncMove, this);
                this.on('mouseout', this._cursorSyncOut, this);
            }
            return this;
        },

        _cursorSyncMove: function (e) {
            this._cursors.forEach(function (cursor) {
                cursor.setLatLng(e.latlng);
            });
        },

        _cursorSyncOut: function (e) {
            this._cursors.forEach(function (cursor) {
                // TODO: hide cursor in stead of moving to 0, 0
                cursor.setLatLng([0, 0]);
            });
        },


        // unsync maps from each other
        unsync: function (map) {
            var self = this;

            if (this._syncMaps) {
                this._syncMaps.forEach(function (synced, id) {
                    if (map === synced) {
                        self._syncMaps.splice(id, 1);
                        if (map.cursor) {
                            map.cursor.removeFrom(map);
                        }
                    }
                });
            }
            this.off('mousemove', this._cursorSyncMove, this);
            this.off('mouseout', this._cursorSyncOut, this);

            return this;
        },

        // Checks if the maps is synced with anything
        isSynced: function () {
            return (this.hasOwnProperty('_syncMaps') && Object.keys(this._syncMaps).length > 0);
        },

        // overload methods on originalMap to replay interactions on _syncMaps;
        _initSync: function () {
            if (this._syncMaps) {
                return;
            }
            var originalMap = this;

            this._syncMaps = [];
            this._cursors = [];

            L.extend(originalMap, {
                setView: function (center, zoom, options, sync) {
                    if (!sync) {
                        originalMap._syncMaps.forEach(function (toSync) {
                            toSync.setView(center, zoom, options, true);
                        });
                    }
                    return L.Map.prototype.setView.call(this, center, zoom, options);
                },

                panBy: function (offset, options, sync) {
                    if (!sync) {
                        originalMap._syncMaps.forEach(function (toSync) {
                            toSync.panBy(offset, options, true);
                        });
                    }
                    return L.Map.prototype.panBy.call(this, offset, options);
                },

                _onResize: function (event, sync) {
                    if (!sync) {
                        originalMap._syncMaps.forEach(function (toSync) {
                            toSync._onResize(event, true);
                        });
                    }
                    return L.Map.prototype._onResize.call(this, event);
                }
            });

            originalMap.on('zoomend', function () {
                originalMap._syncMaps.forEach(function (toSync) {
                    toSync.setView(originalMap.getCenter(), originalMap.getZoom(), NO_ANIMATION);
                });
            }, this);

            originalMap.dragging._draggable._updatePosition = function () {
                L.Draggable.prototype._updatePosition.call(this);
                var self = this;
                originalMap._syncMaps.forEach(function (toSync) {
                    L.DomUtil.setPosition(toSync.dragging._draggable._element, self._newPos);
                    toSync.eachLayer(function (layer) {
                        if (layer._google !== undefined) {
                            layer._google.setCenter(originalMap.getCenter());
                        }
                    });
                    toSync.fire('moveend');
                });
            };
        }
    });
})();
</script>

<script type='text/javascript'>

//===============================================
var crs = L.CRS.EPSG4326;

{% for cmd in cmds %}
//===============================================
var wmspyferret{{ loop.index }} = L.tileLayer.wms('http://localhost:8000', {
	cmd: '{{ cmd }}',
    	crs: crs,
	format: 'image/png',
	transparent: true,
	attribution: 'pyferret',
    	uppercase: true
});
var frontiers{{ loop.index }} = L.tileLayer.wms('http://www.globalcarbonatlas.org:8080/geoserver/GCA/wms', {
	layers: 'GCA:GCA_frontiersCountryAndRegions',
	format: 'image/png',
    	crs: crs,
	transparent: true
});

var map{{ loop.index }} = L.map('map{{ loop.index }}', {
    layers: [wmspyferret{{ loop.index }}, frontiers{{ loop.index }}],
    crs: crs,
    center: [0, 0],
    zoom: 2 
});
{% endfor %}

//===============================================
// Set up synchro between maps
{% for synchro in listSynchroMapsToSet -%}
map{{ synchro[0] }}.sync(map{{ synchro[1] }});
{% endfor %}

//===============================================
var exec = require('child_process').exec,child;

process.stdout.write('Starting NW application\\n');
process.on('exit', function (){
    process.stdout.write('Exiting from NW application, now killing the gunicorn server\\n');
    process.kill({{ gunicornPID }});			// kill gunicorn server
});

</script>

</body>
</html>
'''

#==============================================================
def template_nw_package():

    return '''
{
  "name": "Slippy maps from pyferret",
  "main": "index.html",
  "window": {
          "toolbar": false,
          "width": {{ nbMaps*mapWidth + 100 }},
          "height": {{ mapHeight + 100 }} 
          }
}
'''

#==============================================================
from optparse import OptionParser

parser = OptionParser(usage="%prog [--width=400] [--height=400] 'cmd; cmd'", version="%prog 0.9.0")
parser.add_option("--width", type="int", dest="width", default=400, help="300 < map width <= 600")
parser.add_option("--height", type="int", dest="height", default=400, help="300 < map height <= 600")

(options, args) = parser.parse_args()

if options.width < 300 or options.width > 600 or options.height < 300 or options.height > 600 :
	parser.print_help()
	sys.exit(1)

mapWidth =  options.width
mapHeight = options.height
cmdsRequested = args[0]

cmds = cmdsRequested.split(';')		# get individual commands
cmds = map(str.strip, cmds)  		# remove surrounding spaces if present

tmpdir = ''

options = {
    'bind': '%s:%s' % ('127.0.0.1', '8000'),
    'workers': number_of_workers(),
    'worker_class': 'sync',
    'threads': 1 
}
StandaloneApplication(handler_app, options).run()

sys.exit(1)

