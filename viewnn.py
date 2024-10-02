import csv
import math
import os
import re
from dash import Dash, html, dcc, Input, Output, callback
import imageio
from dash_slicer import VolumeSlicer

import pandas as pd
import numpy as np
import chart_studio.plotly as py
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

path = '/record/'
fileparse = r'^([a-zA-Z]+)(\d*)$'


"""
df_iris = px.data.iris()
fig = px.scatter(df_iris, x='sepal_width', y='sepal_length', color='species', size='petal_length', hover_data=['petal_width'])
"""
def GeneratePositions(size: int):
    edgesize = int(math.sqrt(size))
    xedgesize = edgesize
    yedgesize = edgesize
    while xedgesize * yedgesize < size:
        yedgesize += 1

    xedgepos = []
    yedgepos = []
    for y in range(yedgesize):
        for x in range(xedgesize):
            xedgepos.append(x)
            yedgepos.append(y)

    return (xedgepos, yedgepos)

def GetSimulationNumbers():
  sims = []
  obj = os.scandir(path)
  for entry in obj:
    if entry.is_dir():
      sims.append(re.split(fileparse, entry.name)[2])

  sims.sort()
  if len(sims) == 0:
      sims = ['<empty>']
  return sims


rows = []
currentrow = 0
def LoadSimulation(simnumber):
    global rows, currentrow
    with open('/record/simulation' + str(simnumber) + '/spikes/spike0.csv') as csvfile:
        csvreader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        rows = []
        for row in csvreader:
            rows.append(row)

    if len(rows) == 0:
        rows.append(np.random.randn(784))

    currentrow = 0

LoadSimulation(0)
xedgepos, yedgepos = GeneratePositions(len(rows[0]))
fig = go.Figure(data=go.Scattergl(
    x = xedgepos,
    y = yedgepos,
    dy=2,
    mode='markers',
    marker=dict(
        #color= np.random.randn(784),
        color = rows[currentrow],
        colorscale='Viridis',
        line_width=1,
        size=20
    )
))

app = Dash(__name__, update_title=None)


app.layout = [
    html.Div(className='row', children='Tensorflow Spiking Neural Networks', style={'textAlign':'center', 'fontSize':30}),
    html.Div(className='row', 
        children=[
            html.Div(children=dcc.Dropdown(GetSimulationNumbers(), GetSimulationNumbers()[0], style={'width':120, 'fontSize':18}, id='sim-dropdown')),
            html.Div()
        ]),
    html.Hr(),
    html.Div(
        children=[
            dcc.Graph(id='live-update-graph', style={'height':'900px', 'width':'1200px'}),
            dcc.Interval(
                id='interval-component',
                interval=250, # in milliseconds
                n_intervals=0)
        ],
        style={'margin':'auto'}
    )
]

@callback(Input('sim-dropdown', 'value'))
def load_new_simulation(value):
    LoadSimulation(value)


@callback(Output('live-update-graph', 'figure'), 
          Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global rows, currentrow, xedgepos, yedgepos
    fig = go.Figure(data=go.Scattergl(
        x = xedgepos,
        y = yedgepos,
        dy=2,
        mode='markers',
        marker=dict(
            #color= np.random.randn(784),
            color = rows[currentrow],
            colorscale='Viridis',
            line_width=1,
            size=18
        )
    ))
    currentrow += 1
    if currentrow >= len(rows):
        currentrow = 0
    return fig


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', dev_tools_props_check=False)

