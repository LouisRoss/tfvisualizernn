import os
import json
import csv
import matplotlib.pyplot as plt
import numpy as np
from parselog import ArrayBuilder

class DataPrep:
    baseFolder = '/record/'
    indexFilename = 'index.json'
    connectionsFolder = 'connections/'
    spikesFolder = 'spikes/'
    activationsFolder = 'activations/'

    connectionSourceFilename = 'fullconnections.dat'
    spikeSourceFilename = 'fullspike.dat'
    activationSourceFilename = 'fullactivations.dat'

    connectionBaseFilename = 'connection'
    spikeBaseFilename = 'spike'
    activationBaseFilename = 'activation'

    def __init__(self, simulationNumber):
        self.simulationNumber = simulationNumber
        self.simulationExists = os.path.exists(self.MakeSimulationPath())
        self.index = {
            'simulation': simulationNumber,
            'populations': 4,
            'connections': [
            ],
            'spikes': [
                './' + DataPrep.spikesFolder + DataPrep.spikeBaseFilename + str(1) + '.csv',
                './' + DataPrep.spikesFolder + DataPrep.spikeBaseFilename + str(2) + '.csv',
                './' + DataPrep.spikesFolder + DataPrep.spikeBaseFilename + str(3) + '.csv',
                './' + DataPrep.spikesFolder + DataPrep.spikeBaseFilename + str(4) + '.csv'
            ],
            'activations': [
                './' + DataPrep.activationsFolder + DataPrep.activationBaseFilename + str(1) + '.csv',
                './' + DataPrep.activationsFolder + DataPrep.activationBaseFilename + str(2) + '.csv',
                './' + DataPrep.activationsFolder + DataPrep.activationBaseFilename + str(3) + '.csv',
                './' + DataPrep.activationsFolder + DataPrep.activationBaseFilename + str(4) + '.csv'
            ]
        }


    def MakeSimulationPath(self):
        # The base path for all input and output files in this simulation.
        return DataPrep.baseFolder + 'simulation' + str(self.simulationNumber) + '/'
    
    def MakeIndexFilePath(self):
        # The index file describing all generated output files as well as some simulation parameters.
        return self.MakeSimulationPath() + DataPrep.indexFilename

    # Paths to input files.
    def MakeConnectionsSourceFilePath(self):
        return self.MakeSimulationPath() + DataPrep.connectionSourceFilename
    
    def MakeSpikesSourceFilePath(self):
        return self.MakeSimulationPath() + DataPrep.spikeSourceFilename
    
    def MakeActivationsSourceFilePath(self):
        return self.MakeSimulationPath() + DataPrep.activationSourceFilename

    # Paths to output files.    
    def MakeConnectionOutputFilePath(self, population):
        if not os.path.exists(self.MakeSimulationPath() + DataPrep.connectionsFolder):
            os.makedirs(self.MakeSimulationPath() + DataPrep.connectionsFolder)
        return self.MakeSimulationPath() + DataPrep.connectionsFolder + DataPrep.connectionBaseFilename + str(population) + '.csv'

    def MakeSpikeOutputFilePath(self, population):
        if not os.path.exists(self.MakeSimulationPath() + DataPrep.spikesFolder):
            os.makedirs(self.MakeSimulationPath() + DataPrep.spikesFolder)
        return self.MakeSimulationPath() + DataPrep.spikesFolder + DataPrep.spikeBaseFilename + str(population) + '.csv'

    def MakeActivationOutputFilePath(self, population):
        if not os.path.exists(self.MakeSimulationPath() + DataPrep.activationsFolder):
            os.makedirs(self.MakeSimulationPath() + DataPrep.activationsFolder)
        return self.MakeSimulationPath() + DataPrep.activationsFolder + DataPrep.activationBaseFilename + str(population) + '.csv'

    def EnsureConversion(self):
        if not self.simulationExists:
            print(f'No folder for simulation {self.simulationNumber} exists')
            return
        
        if os.path.exists(self.MakeIndexFilePath()):
            self.index = json.loads(self.MakeIndexFilePath())
            return
        

    def BuildConnections(self, debug=False):
        builder = ArrayBuilder(self.MakeConnectionsSourceFilePath())
        builder.Build(debug=debug)
        linedata = builder.linedata

        # Build an array of population arrays.
        populationCount = len(linedata)
        if populationCount > self.index['populations']:
            self.index['populations'] = populationCount 

        for pop in range(populationCount):
            connectionFile = self.MakeConnectionOutputFilePath(pop)
            self.index['connections'].append(connectionFile)
            with open(connectionFile, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                for line in linedata[pop]:
                    csvwriter.writerow(line)
"""
builder = ArrayBuilder('data/fullspike.csv')
builder.Build(debug=False)
linedata = builder.linedata

data = []
population = 0
print(f'Shape: {linedata.shape}')
for iteration in range(len(linedata)):
    data.append([])

for iteration in range(len(linedata)):
    #print(f'{iteration[0][0][0]}\n')
    print(f'{linedata[iteration][population]}\n')

    for pop in range(8):
        data[pop].append(linedata[iteration][population+pop])

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(10,50), layout="constrained")
print(axs)

pop = 0
for ax in axs.flat:
    ax.imshow(data[pop])
    pop += 1

plt.show()
"""
