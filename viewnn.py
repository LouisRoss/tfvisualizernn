import math
from dash import Dash, html, dcc, Input, Output, callback
import imageio
from dash_slicer import VolumeSlicer

import pandas as pd
import numpy as np
import chart_studio.plotly as py
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

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


xedgepos, yedgepos = GeneratePositions(784)
fig = go.Figure(data=go.Scattergl(
    x = xedgepos,
    y = yedgepos,
    dy=2,
    mode='markers',
    marker=dict(
        color= np.random.randn(784),
        colorscale='Viridis',
        line_width=1,
        size=20
    )
))
app = Dash(__name__, update_title=None)


app.layout = [
    html.Div(className='row', children='Tensorflow Spiking Neural Networks', style={'textAlign':'center', 'fontSize':30}),
    html.Hr(),
    html.Div(
        children=[
            dcc.Graph(id='live-update-graph', style={'height':'900px', 'width':'900px'}),
            dcc.Interval(
                id='interval-component',
                interval=200, # in milliseconds
                n_intervals=0)
        ],
        style={'margin':'auto'}
    )
]


@callback(Output('live-update-graph', 'figure'), 
          Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    fig = go.Figure(data=go.Scattergl(
        x = xedgepos,
        y = yedgepos,
        dy=2,
        mode='markers',
        marker=dict(
            color= np.random.randn(784),
            colorscale='Viridis',
            line_width=1,
            size=20
        )
    ))
    return fig


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', dev_tools_props_check=False)

