import os
import matplotlib.pyplot as plt
import numpy as np
from parselog import ArrayBuilder

class DataPrep:
    baseFolder = '/record/'
    indexFilename = 'index.json'
    connectionsFolder = 'connections/'
    spikesFolder = 'spikes/'
    activationsFolder = 'activations/'

    spikeSourceFilename = 'fullspike.dat'
    connectionSourceFilename = 'fullconnections.dat'
    activationSourceFilename = 'fullactivations.dat'

    def __init__(self, simulationNumber):
        self.simulationNumber = simulationNumber
        self.simulationExists = os.path.exists(self.MakeSimulationPath())
        self.index = {}


    def MakeSimulationPath(self):
        return DataPrep.baseFolder + 'simulation' + str(self.simulationNumber) + '/'
    
    def MakeIndexFilePath(self):
        return self.MakeSimulationPath() + DataPrep.indexFilename

    def MakeConnectionsPath(self):
        return self.MakeSimulationPath() + DataPrep.connectionsFolder
    
    def MakeSpikesPath(self):
        return self.MakeSimulationPath() + DataPrep.spikesFolder
    
    def MakeActivationsPath(self):
        return self.MakeSimulationPath() + DataPrep.activationsFolder
    
    def EnsureConversion(self):
        if not self.simulationExists:
            print(f'No folder for simulation {self.simulationNumber} exists')
            return
        
        if os.path.exists(self.MakeIndexFilePath()):
            return
        

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
