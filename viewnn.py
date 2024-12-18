import csv
import math
import os
import re
from dash import Dash, html, dcc, Input, Output, State, Patch, ctx, callback
from dash.exceptions import PreventUpdate
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
spikefileparse = r'^([a-zA-Z]+)(\d*)\.csv$'


"""
df_iris = px.data.iris()
fig = px.scatter(df_iris, x='sepal_width', y='sepal_length', color='species', size='petal_length', hover_data=['petal_width'])
"""

# NOTE: Using global variables will mean individual sessions will interfere with each other.
#       However, it is unreasonable to load and analyze a simulation on every update, so.
xedgepos = []
yedgepos = []
simulation = []
rows = []
currentrow = 0
simulationNo = 0
populationNo = 0
simulation_loaded = False


def GeneratePositions(size: int):
    global xedgepos, yedgepos
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


def LoadSimulation():
    global rows, currentrow, simulation_loaded, simulation, simulationNo, populationNo

    population_numbers = GetPopulationNumbers()
    # simulation[population][tick][layer]

    simulation = []
    for population_number in population_numbers:
        population = []
        with open(path + 'simulation' + str(simulationNo) + '/spikes/spike' + str(population_number) + '.csv') as csvfile:
            csvreader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            for row in csvreader:
                population.append(row)
        simulation.append(population)

    simulation_loaded = True

def CalibrateValuesForViewing(values):
    result = []
    for value in values:
        result.append(float(value) * 10.0 + 10.0)

    return result


def ViewFullPopulation():
    global simulation, rows, currentrow, populationNo
    print(f'Viewing for full population {populationNo}, where simulation has {len(simulation)} populations and population {populationNo} has {"millions of"} cells')
    if len(simulation) == 0:
        return

    rows = []
    population = simulation[populationNo]
    print(f'View adding {len(population)} rows')
    for population_sample in population:
        rows.append(CalibrateValuesForViewing(population_sample))

    GeneratePositions(len(rows[0]))
    currentrow = 0
    

def ViewAcrossPopulations(cells):
    global simulation, rows, currentrow

    rows = []
    if len(simulation) == 0:
        return

    # All populations in the simulation should have the same length, choose the first.    
    ticks = len(simulation[0])

    # rows[tick][population sampled at layer[i]],
    # where i is some aggregation of cells[].
    for tick in range(ticks):
        row = []
        for population in simulation:
            population_at_tick = population[tick]
            aggregate = 0
            for cell in cells:
                aggregate |= int(population_at_tick[cell])

            row.append(aggregate)
        rows.append(CalibrateValuesForViewing(row))

    GeneratePositions(len(rows[0]))
    currentrow = 0


def GetSimulationNumbers():
  sims = []
  obj = os.scandir(path)
  for entry in obj:
    if entry.is_dir() and entry.name.startswith('simulation'):
      sims.append(re.split(fileparse, entry.name)[2])

  sims.sort(key=int)
  if len(sims) == 0:
      sims = ['<empty>']
  return sims


def GetPopulationNumbers():
  pops = []
  obj = os.scandir(path + 'simulation' + str(simulationNo) + '/spikes/')
  for entry in obj:
    if entry.is_file() and entry.name.startswith('spike'):
      pops.append(int(re.split(spikefileparse, entry.name)[2]))

  pops.sort(key=int)
  if len(pops) == 0:
      pops = ['<empty>']
  return pops



app = Dash(__name__, update_title='Spiking Neurons')


app.layout = [
    html.Div(className='row', children='Tensorflow Spiking Neural Networks', style={'textAlign':'center', 'fontSize':30}),
    html.Div(children=[
        html.Div(className='row', 
            children=[
                html.Div('Simulation', style={'padding':10, 'width':110, 'flex': '0 0 auto', 'fontSize':18}),
                html.Div('Population', style={'padding':10, 'width':110, 'flex': '0 0 auto', 'fontSize':18}),
                html.Div(style={'flex': '1 1 auto'})
            ], style={'display': 'flex', 'flexDirection': 'row'}),
        html.Div(className='row', 
            children=[
                html.Div(dcc.Dropdown(GetSimulationNumbers(), GetSimulationNumbers()[0], disabled=False, style={'width':120, 'fontSize':18, 'flex': '0 0 auto'}, id='sim-dropdown')),
                html.Div(dcc.Dropdown(GetPopulationNumbers(), GetPopulationNumbers()[0], disabled=True, style={'width':120, 'fontSize':18, 'flex': '0 0 auto'}, id='pop-dropdown')),
                html.Div(dcc.RadioItems(['Full Population', 'Across Populations'], 'Full Population', inline=True, style={'padding': 10, 'flex': '0 0 auto'}, id='orientation')),
                html.Div(html.Button('Run', disabled=True, style={'float':'left', 'width':100, 'padding': 10, 'flex': '0 0 auto'}, id='run-stop', n_clicks=0)),
                html.Div(style={'width':100, 'padding': 10, 'flex': '1 1 auto'})
            ], style={'display': 'flex', 'flexDirection': 'row'}),
    ], style={'display': 'flex', 'flexDirection': 'column'}),
    html.Div(children=[
        html.Div(
            children=[
                dcc.Graph(id='live-update-graph', style={'height':'900px', 'width':'900px'}, figure=go.Figure(data=go.Scattergl())),
                dcc.Interval(
                    id='interval-component',
                    interval=250, # in milliseconds
                    n_intervals=0,
                    disabled=True)
            ],
            style={'margin':'auto', 'flex':'1 0 auto'}
        ),
        html.Div('', style={'fontSize': 30, 'padding-top':200, 'padding-bottom':0, 'flex':'3 0 auto'}, id='simulation-tick'),
    ], style={'display': 'flex', 'flexDirection': 'row'}),
]


@callback(Output('run-stop', 'children'),
          Output('run-stop', 'disabled'),
          Output('sim-dropdown', 'disabled'),
          Output('pop-dropdown', 'disabled'),
          Output('interval-component', 'disabled'),
          Output('pop-dropdown', 'options'),
          Input('sim-dropdown', 'value'),
          Input('pop-dropdown', 'value'),
          Input('run-stop', 'children'),
          Input('run-stop', 'n_clicks'),
          Input('orientation', 'value'))
def handle_user(sim_value, pop_value, run_stop_value, run_stop_clicks, orientation):
    global simulationNo, populationNo, simulation_loaded

    selection_id = ctx.triggered_id

    new_runstop_button_value = run_stop_value
    disable_runstop_button = True   # Stays true on initial callback, when selection_id is None.
    disable_sim_dropdown = False
    disable_pop_dropdown = True     # Stays true on initial callback, when selection_id is None.
    disable_timer = True
    print(f'selection_id = {selection_id}')
    if selection_id == 'sim-dropdown':
        print(f'Loading simulation {sim_value}')

        if sim_value is None:
            sim_value = 0

        simulationNo = sim_value
        LoadSimulation()
        disable_pop_dropdown = False
        print(f'Simulation {sim_value} loaded')
    elif selection_id == 'pop-dropdown':
        print(f'Viewing population {pop_value}')

        if pop_value is None:
            pop_value = 0

        populationNo = pop_value
        if orientation == 'Full Population':
            ViewFullPopulation()
        elif orientation == 'Across Populations':
            ViewAcrossPopulations([0,1])

        if run_stop_value == 'Stop':        # Running
            disable_sim_dropdown = True
            disable_timer = False

        disable_runstop_button = False
        disable_pop_dropdown = False
    elif selection_id == 'run-stop':
        if run_stop_value == 'Run':
            print(f'Running simulation {simulationNo}, population {populationNo}')

            new_runstop_button_value = 'Stop'
            disable_runstop_button = False
            disable_sim_dropdown = True
            disable_pop_dropdown = False    # Allow population changes while running.
            disable_timer = False
            simulation_loaded = True
        elif run_stop_value == 'Stop':
            print(f'Stopping simulation {simulationNo}, population {populationNo}')

            new_runstop_button_value = 'Run'
            disable_runstop_button = True
            disable_sim_dropdown = False
            disable_pop_dropdown = False
            disable_timer = True
        else:
            new_runstop_button_value = 'Run'
    elif selection_id == 'orientation':
        print(f'Changing orientation to {orientation}')

        if orientation == 'Full Population':
            ViewFullPopulation()
            simulation_loaded = True
        elif orientation == 'Across Populations':
            ViewAcrossPopulations([0,1])
            simulation_loaded = True

        if run_stop_value == 'Stop':        # Running
            disable_sim_dropdown = True
            disable_timer = False

        disable_runstop_button = False
        disable_pop_dropdown = False

    return new_runstop_button_value, disable_runstop_button, disable_sim_dropdown, disable_pop_dropdown, disable_timer, GetPopulationNumbers()


@callback(Output('simulation-tick', 'children'),
          Output('live-update-graph', 'figure'), 
          Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global rows, currentrow, xedgepos, yedgepos, simulation_loaded
    if len(rows) == 0:
        raise PreventUpdate

    if simulation_loaded:
        print(f'Fresh simulation, return new figure')
        fig = go.Figure(data=go.Scattergl(
            x = xedgepos,
            y = yedgepos,
            dy=2,
            mode='markers',
            marker=dict(
                #color= np.random.randn(784),
                color = rows[currentrow],
                size = rows[currentrow],
                colorscale='Viridis',
                cmin=0.0,
                cmax=20.0,
                line_width=1
            )
        ))
        simulation_loaded = False
    else:
        fig = Patch()
        updated_marker = dict(
                #color= np.random.randn(784),
                color = rows[currentrow],
                size = rows[currentrow],
                colorscale='Viridis',
                cmin=0.0,
                cmax=20.0,
                line_width=1
            )
        fig['data'][0]['marker'] = updated_marker

    visiblerow = currentrow
    currentrow += 1
    if currentrow >= len(rows):
        currentrow = 0
    return f'Tick: {visiblerow} {rows[visiblerow][0]}', fig


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', dev_tools_props_check=False)

