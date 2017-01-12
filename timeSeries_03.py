#!/usr/local/bin/anaconda2/bin/python

import cgi, cgitb
cgitb.enable()

import sys
import os

import tempfile

#=======================================================
args = cgi.FieldStorage()

VAR = args["VAR"].value
XTRANS = args["XLIM"].value + "@ave"
YTRANS = args["YLIM"].value + "@ave"

#=======================================================
import pyferret

pyferret.start(journal=False, unmapped=True, quiet=True, verify=False)

pyferret.run("use /prodigfs/project/CARBON/CRESCENDO/thetao_Oyr_ALL_historical_r1i1p1_1870-2005.nc")
pyferret.run("let var=" + VAR + "[k=1,m=1,x=" + XTRANS + ",y=" + YTRANS + "]")

tmpfile = tempfile.NamedTemporaryFile(suffix='.csv').name

pyferret.run("spawn echo 'date,'" + VAR + " > " + tmpfile)
pyferret.run("list/quiet/nohead/norowlab/precision=7/format=\"comma\"/file=\"" + tmpfile + "\"/append TAX_DATESTRING(t[g=var],var,\"mon\"), var")

pyferret.stop()

#=======================================================
os.environ[ 'MPLCONFIGDIR' ] = '/tmp/'
import pandas as pd 

df = pd.read_csv(tmpfile)

df['date'] = pd.to_datetime(df['date'], format='%b-%Y')  # convert ferret dates as datetimes 
df = df.set_index('date')

# ### Plot with bokeh
colors = ["#8c564b","#1f77b4","#2ca02c","#d62728","#9467bd","#e377c2","#7f7f7f","#bcbd22","#17bec"]

import bokeh.plotting as bk
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import DatetimeTickFormatter
from bokeh.models import HoverTool, BoxAnnotation
from bokeh.embed import components

varName = df.columns[0]

source = ColumnDataSource(data=dict(
        date = df.index,
        datestr = df.index.strftime("%Y-%m"),
        var = df[varName]) )

hover1 = HoverTool(tooltips=[("date, var", "(@datestr, @var)")])
tools1 = ["pan,resize,wheel_zoom,crosshair",hover1,"reset,save"]

plot1 = figure(plot_width=600, plot_height=400, x_axis_type="datetime", min_border=10, tools=tools1, 
		title="X=" + XTRANS + ", Y=" + YTRANS )

plot1.axis[0].formatter = DatetimeTickFormatter(years="%Y", months="%b-%y", days="%d-%b-%y", hours="%H:%M")

plot1.line('date', 'var', source=source, line_alpha=1.0, line_join="round", line_color=colors[0], 
           line_width=1, legend=varName)
plot1.circle('date', 'var', source=source, size=3, color=colors[0])

plot1.background_fill_color = "beige"
plot1.background_fill_alpha = 1.0

script, div = components(plot1)

#os.remove(tmpfile)

print("Content-Type: text/html\r\n")

print(script)
print(div)

print("<button id=\"Download\">Download</button>")

