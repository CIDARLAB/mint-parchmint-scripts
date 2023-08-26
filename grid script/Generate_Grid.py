from pymint import MINTDevice, MINTLayerType
from parchmint.target import Target
from parchmint import Device
import json

numFlowConnections = 0
numControlConnections = 0
numValves = 0

sctList = []
flowConnections = []
controlConnections = []
valves = []

#Set component parameters
trap_params = {
    "chamberWidth": 100,
    "chamberLength": 100,
    "channelWidth": 100
}

flow_connection_params = {
    "w": 100
}

valve_params = {
    "w": 300,
    "l": 100
}

#Prompt user for grid size
gridSize = int(input("Please enter a grid size:"))

# Create the MINTDevice instance with a name
device = MINTDevice(name="grid_device")

########################################################################################################################################################
# Create the flow layer
flow_layer = device.create_mint_layer(ID="flow", name_postfix="FLOW", group=None, layer_type=MINTLayerType.FLOW)

# Create the ports on the flow layer
port1 = device.add_terminal(name="p1", pin_number=1 , layer_id=flow_layer.ID)
port2 = device.add_terminal(name="p2", pin_number=1 , layer_id=flow_layer.ID)

# Create the square cell trap components and store them in an array

for i in range(1,gridSize**2+1):
    sctList.append(device.create_mint_component(name="ct"+str(i), technology="SQUARE CELL TRAP", params=trap_params, layer_ids=[flow_layer.ID]))

#Connect port to first tree and first tree to first row of cell traps
numFlowConnections+=1

for row in range(1,gridSize+1):
    numFlowConnections+=1

#Connect adjacent cell traps within a row and connect adjacent rows
for row in range(1,gridSize+1):
    #Connect cell traps within a row
    for col in range(1,gridSize):
        numFlowConnections+=1

        #Calculate the source and sink cell trap number
        #To access the sct, it is the sctList[sctNum-1]
        SourceSCTNum = (row-1)*gridSize+col
        SinkSCTNum = (row-1)*gridSize+col+1

        controlConnections.append(device.create_mint_connection(
            name = "c"+str(numFlowConnections),
            technology = "CONNECTION",
            params = flow_connection_params,
            source = Target(sctList[SourceSCTNum-1].ID,port="2"),
            sinks = [Target(sctList[SinkSCTNum-1].ID,port="4")], 
            layer_id = flow_layer.ID
        ))

    #Connect current row to next row
    if(row!=gridSize):
        for col in range(1,gridSize+1):
            numFlowConnections+=1

            SourceSCTNum = (row-1)*gridSize+col 
            SinkSCTNum = (row-1)*gridSize+col+gridSize

            controlConnections.append(device.create_mint_connection(
                name = "c"+str(numFlowConnections),
                technology="CONNECTION",
                params = flow_connection_params,
                source = Target(sctList[SourceSCTNum-1].ID,port="3"),
                sinks = [Target(sctList[SinkSCTNum-1].ID,port="1")],
                layer_id = flow_layer.ID
            ))


#########################################################################################################################################################
# Create the control layer
control_layer = device.create_mint_layer(ID="flow", name_postfix="CONTROL", group=None, layer_type=MINTLayerType.CONTROL)

#Place Valves

#Calculate the connection number, 
#to access that connection: flowConnections[connection# - gridSize - 1]
#because we skipped the tree connections


# for row in range(1,gridSize+1):
#     for col in range(1,gridSize):

#         #Calculate connection number
#         cNumber = 2+2*row*gridSize-row-gridSize+col

#         numValves+=1
#         valves.append(device.create_valve(
#             name = "v" + str(numValves),
#             technology= "VALVE",
#             params = valve_params,
#             layer_ids = [control_layer.ID],
#             connection = flowConnections[cNumber - gridSize - 1]
#         ))

#     if(row!=gridSize):
#         for col in range(1,gridSize+1):

#             #Calculate connection number
#             cNumber = 1+2*row*gridSize-row+col

#             numValves+=1
#             valves.append(device.create_valve(
#             name = "v" + str(numValves),
#             technology= "VALVE",
#             params = valve_params,
#             layer_ids = [control_layer.ID],
#             connection = flowConnections[cNumber - gridSize - 1]
#         ))



#########################################################################################################################################################
fileName = 'grid_' + str(gridSize) + '.uf'
with open(fileName, 'w') as file:
    file.write(device.to_MINT())

print("Code generation complete.")


with open('grid_' + str(gridSize)+ "v2" + ".json", 'w') as f:
    json.dump(device.device.to_parchmint_v1_2(), f, indent=2)

with open('grid_' + str(gridSize) + ".json", 'w') as f:
    json.dump(device.to_parchmint(), f, indent=2)