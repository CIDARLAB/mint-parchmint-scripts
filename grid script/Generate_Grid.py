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

#List of control ports that control the vertical and horizontal connections respectively 
#that connect the square cell traps
verticalControlPorts = []
horizontalControlPorts = []


tempTargetList = []

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
gridSize = int(input("Please enter a grid size: "))

# Create the MINTDevice instance with a name
device = MINTDevice(name="grid_device")

########################################################################################################################################################
# Create the flow layer
flow_layer = device.create_mint_layer(ID="flow", name_postfix="FLOW", group=None, layer_type=MINTLayerType.FLOW)

# Create the control layer
control_layer = device.create_mint_layer(ID="flow", name_postfix="CONTROL", group=None, layer_type=MINTLayerType.CONTROL)

# Create the ports on the flow layer
port1 = device.add_terminal(name="p1", pin_number=1 , layer_id=flow_layer.ID)
port2 = device.add_terminal(name="p2", pin_number=1 , layer_id=flow_layer.ID)

# Create the square cell trap components and store them in an array

for i in range(1,gridSize**2+1):
    sctList.append(device.create_mint_component(name="ct"+str(i), technology="SQUARE CELL TRAP", params=trap_params, layer_ids=[flow_layer.ID]))

#Connect port to first row of cell traps
entryPortSinks = []
for row in range(1,gridSize+1):
    entryPortSinks.append(Target(sctList[row-1].ID,port="4"))

numFlowConnections+=1

flowConnections.append(device.create_mint_connection(
    name = "c"+str(numFlowConnections),
    technology="CONNECTION",
    params = flow_connection_params,
    source = Target(port1.component.ID),
    sinks = entryPortSinks,
    layer_id = flow_layer.ID
))



#Connect adjacent cell traps within a column and connect adjacent columns
for col in range(1,gridSize+1):
    #Connect cell traps within a column and place a valve on the connection
    for row in range(1,gridSize):

        numFlowConnections+=1

        #Calculate the source and sink cell trap number
        #To access the sct, it is the sctList[sctNum-1]
        SourceSCTNum = (col-1)*gridSize+row
        SinkSCTNum = (col-1)*gridSize+row+1

        flowConnections.append(device.create_mint_connection(
            name = "c"+str(numFlowConnections),
            technology = "CONNECTION",
            params = flow_connection_params,
            source = Target(sctList[SourceSCTNum-1].ID,port="3"),
            sinks = [Target(sctList[SinkSCTNum-1].ID,port="1")], 
            layer_id = flow_layer.ID
        ))

        #Place valve on the connection we just made
        numValves+=1
        valves.append(device.create_valve(
            name = "v" + str(numValves),
            technology= "VALVE",
            params = valve_params,
            layer_ids = [control_layer.ID],
            connection = flowConnections[numFlowConnections-1]
        ))
        

    #Create control port
    verticalControlPorts.append(device.add_terminal(
        name="vcp" + str(col),
        pin_number=1 ,
        layer_id=control_layer.ID))
    
    #Connect valves to control port

    tempTargetList.clear()

    for valve in valves[-(gridSize-1):]:
        tempTargetList.append(Target(valve.ID))


    numControlConnections+=1
    controlConnections.append(device.create_mint_connection(
            name = "cc"+str(numControlConnections),
            technology = "CONNECTION",
            params = flow_connection_params,
            source = Target(verticalControlPorts[-1].component.ID),
            sinks = tempTargetList, 
            layer_id = control_layer.ID
    ))




    #Connect current column to next column and place a valve on the connection
    if(col!=gridSize):
        for row in range(1,gridSize+1):
            numFlowConnections+=1

            SourceSCTNum = (col-1)*gridSize+row 
            SinkSCTNum = (col-1)*gridSize+row+gridSize

            flowConnections.append(device.create_mint_connection(
                name = "c"+str(numFlowConnections),
                technology="CONNECTION",
                params = flow_connection_params,
                source = Target(sctList[SourceSCTNum-1].ID,port="2"),
                sinks = [Target(sctList[SinkSCTNum-1].ID,port="4")],
                layer_id = flow_layer.ID
            ))

            #Place valve on the connection we just made
            numValves+=1
            valves.append(device.create_valve(
                name = "v" + str(numValves),
                technology= "VALVE",
                params = valve_params,
                layer_ids = [control_layer.ID],
                connection = flowConnections[numFlowConnections-1]
            ))

        #Create control port
        horizontalControlPorts.append(device.add_terminal(
            name="hcp" + str(col),
            pin_number=1 ,
            layer_id=control_layer.ID
            ))
        
        #Connect valves to control port

        tempTargetList.clear()

        for valve in valves[-gridSize:]:
            tempTargetList.append(Target(valve.ID))

        numControlConnections+=1

        controlConnections.append(device.create_mint_connection(
                name = "cc"+str(numControlConnections),
                technology = "CONNECTION",
                params = flow_connection_params,
                source = Target(horizontalControlPorts[-1].component.ID),
                sinks = tempTargetList, 
                layer_id = control_layer.ID
        ))


#Connect exit port to last row of cell traps
exitPortSinks = []
for row in range(1,gridSize+1):
    exitPortSinks.append(Target(sctList[gridSize*(gridSize-1) + row - 1].ID,port="2"))

numFlowConnections+=1

flowConnections.append(device.create_mint_connection(
    name = "c"+str(numFlowConnections),
    technology="CONNECTION",
    params = flow_connection_params,
    source = Target(port2.component.ID),
    sinks = exitPortSinks,
    layer_id = flow_layer.ID
))


#########################################################################################################################################################



#########################################################################################################################################################
fileName = 'grid_' + str(gridSize) + '.uf'
with open(fileName, 'w') as file:
    file.write(device.to_MINT())

with open('grid_' + str(gridSize) + ".json", 'w') as f:
    json.dump(device.device.to_parchmint_v1_2(), f, indent=2)

print("Complete")