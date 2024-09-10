from dash import Dash, html, dcc
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

fig = go.Figure(data=go.Scattergl(
    x = np.random.randn(100000),
    y = np.random.randn(100000),
    dy=2,
    mode='markers',
    marker=dict(
        color= np.random.randn(100000),
        colorscale='Viridis',
        line_width=1,
        size=30
    )
))
app = Dash(__name__, update_title=None)


app.layout = [
    html.Div(className='row', children='A big scatter plot', style={'textAlign':'center', 'fontSize':30}),
    html.Hr(),
    html.Div(
        children=[
            dcc.Graph(figure=fig, style={'height':'900px'})
        ])
]


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', dev_tools_props_check=False)

