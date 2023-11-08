from pymint import MINTDevice, MINTLayerType
from parchmint.target import Target
from parchmint import Device
from pymint.constraints.arrayconstraint import ArrayConstraint
from pymint.constraints.orientationconstraint import OrientationConstraint, ComponentOrientation
import json

numFlowChannels = 0
numControlChannels = 0
numControlNets = 0
numValves = 0

sctList = []
flowChannels = []
controlChannels = []
controlNets = []
valves = []

#List of control ports that control the vertical and horizontal channels respectively 
#that connect the square cell traps
verticalControlPorts = []
horizontalControlPorts = []

#Prompt user for grid size
gridSize = int(input("Please enter a grid size: "))

#Set component parameters
port_params = {
    "portRadius": 1980
}

trap_params = {
    "chamberWidth": 100,
    "chamberLength": 100,
    "channelWidth": 100
}

tree_in_params = {
    "spacing": 1200,
    "flowChannelWidth": 100,
    "in": 1,
    "out": gridSize
}

tree_out_params = {
    "spacing": 1200,
    "flowChannelWidth": 100,
    "in": gridSize,
    "out": 1

}

flow_channel_params = {
    "channelWidth": 100
}

control_channel_params = {
    "channelWidth": 100
}

valve_params = {
    "width": 300,
    "length": 100
}

# Create the MINTDevice instance with a name
device = MINTDevice(name="grid_" + str(gridSize) + "_device")

########################################################################################################################################################
# Create the flow layer
flow_layer = device.create_mint_layer(ID="flow", name_postfix="FLOW", group=None, layer_type=MINTLayerType.FLOW)

# Create the control layer
control_layer = device.create_mint_layer(ID="control", name_postfix="CONTROL", group=None, layer_type=MINTLayerType.CONTROL)

# Create the ports on the flow layer
port1 = device.create_mint_component(
    name = "p1",
    technology = "PORT",
    params = port_params,
    layer_ids = [flow_layer.ID]
)

port2 = device.create_mint_component(
    name = "p2",
    technology = "PORT",
    params = port_params,
    layer_ids = [flow_layer.ID]
)

# Create the square cell trap components and store them in an array
for i in range(1,gridSize**2+1):
    sctList.append(device.create_mint_component(
        name="ct"+str(i), 
        technology="SQUARE CELL TRAP", 
        params=trap_params, 
        layer_ids=[flow_layer.ID])
    )

#Create the trees
tree1 = device.create_mint_component(
    name="m1",
    technology="TREE",
    params=tree_in_params,
    layer_ids=[flow_layer.ID]
)
tree2 = device.create_mint_component(
    name="m2",
    technology="TREE",
    params=tree_out_params,
    layer_ids=[flow_layer.ID]
)

#Connect tree1 to port1 
numFlowChannels+=1

flowChannels.append(device.create_mint_connection(
    name = "c"+str(numFlowChannels),
    technology = "CHANNEL",
    params = flow_channel_params,
    source = Target(port1.ID, port=1),
    sinks = [Target(tree1.ID,port=1)],
    layer_id = flow_layer.ID
))

#Connect tree1 to first column of square cell traps
for row in range(1,gridSize+1):
    numFlowChannels+=1
    flowChannels.append(device.create_mint_connection(
        name = "c"+str(numFlowChannels),
        technology = "CHANNEL",
        params = flow_channel_params,
        source = Target(tree1.ID,port=1+row),
        sinks = [Target(sctList[row-1].ID,port=4)],
        layer_id = flow_layer.ID
    ))



#Connect adjacent cell traps within a column and connect adjacent columns
for col in range(1,gridSize+1):
    #Connect cell traps within a column and place a valve on the channel
    for row in range(1,gridSize):

        numFlowChannels+=1

        #Calculate the source and sink cell trap number
        #To access the sct, it is the sctList[sctNum-1]
        SourceSCTNum = (col-1)*gridSize+row
        SinkSCTNum = (col-1)*gridSize+row+1

        flowChannels.append(device.create_mint_connection(
            name = "c"+str(numFlowChannels),
            technology = "CHANNEL",
            params = flow_channel_params,
            source = Target(sctList[SourceSCTNum-1].ID,port="3"),
            sinks = [Target(sctList[SinkSCTNum-1].ID,port="1")], 
            layer_id = flow_layer.ID
        ))

        #Place valve on the channel we just made
        numValves+=1
        valves.append(device.create_valve(
            name = "v" + str(numValves),
            technology= "VALVE",
            params = valve_params,
            layer_ids = [control_layer.ID],
            connection = flowChannels[numFlowChannels-1]
        ))
        

    #Create control port
    
    verticalControlPorts.append(device.create_mint_component(
        name="vcp" + str(col),
        technology="PORT",
        params=port_params,
        layer_ids=[control_layer.ID]
    ))
    
    #Connect valves to control port

    tempTargetList = []

    for valve in valves[-(gridSize-1):]:
        tempTargetList.append(Target(valve.ID,port=1))

    numControlNets+=1
    controlNets.append(device.create_mint_connection(
            name = "n"+str(numControlNets),
            technology = "CHANNEL",
            params = control_channel_params,
            source = Target(verticalControlPorts[-1].ID,port=1),
            sinks = tempTargetList, 
            layer_id = control_layer.ID
    ))


    #Connect current column to next column and place a valve on the connection
    if(col!=gridSize):
        for row in range(1,gridSize+1):
            numFlowChannels+=1

            SourceSCTNum = (col-1)*gridSize+row 
            SinkSCTNum = (col-1)*gridSize+row+gridSize

            flowChannels.append(device.create_mint_connection(
                name = "c"+str(numFlowChannels),
                technology="CHANNEL",
                params = flow_channel_params,
                source = Target(sctList[SourceSCTNum-1].ID,port="2"),
                sinks = [Target(sctList[SinkSCTNum-1].ID,port="4")],
                layer_id = flow_layer.ID
            ))

            #Place valve on the channel we just made
            numValves+=1
            valves.append(device.create_valve(
                name = "v" + str(numValves),
                technology= "VALVE",
                params = valve_params,
                layer_ids = [control_layer.ID],
                connection = flowChannels[numFlowChannels-1]
            ))

            #Put channels between the valves on horizontal channels
            if(row!=1):
                numControlChannels+=1
                controlChannels.append(device.create_mint_connection(
                    name = "cc" + str(numControlChannels),
                    technology = "CHANNEL",
                    params = control_channel_params,
                    source = Target(valves[-2].ID,port=1),
                    sinks = [Target(valves[-1].ID,port=1)],
                    layer_id = control_layer.ID
                ))
                


        #Create control port
        horizontalControlPorts.append(device.create_mint_component(
            name = "hcp" + str(col),
            technology = "PORT",
            params = port_params,
            layer_ids = [control_layer.ID]
        ))

        #Connect the control port to the valves on the "bottom" of grid
        numControlChannels+=1
        controlChannels.append(device.create_mint_connection(
            name = "cc" + str(numControlChannels),
            technology = "CHANNEL",
            params = control_channel_params,
            source = Target(valves[-1].ID,port=1),
            sinks = [Target(horizontalControlPorts[-1].ID,port=1)],
            layer_id = control_layer.ID
        ))


#Connect last row of square cell traps to tree2
for row in range(1,gridSize+1):
    numFlowChannels+=1
    flowChannels.append(device.create_mint_connection(
        name = "c"+str(numFlowChannels),
        technology = "CHANNEL",
        params = flow_channel_params,
        source = Target(sctList[(gridSize)*(gridSize-1)+row-1].ID,port="2"),
        sinks = [Target(tree2.ID,port=str(row))],
        layer_id = flow_layer.ID
    ))

#Connect tree2 to port2
numFlowChannels+=1
flowChannels.append(device.create_mint_connection(
    name = "c"+str(numFlowChannels),
    technology = "CHANNEL",
    params = flow_channel_params,
    source = Target(tree2.ID,port=gridSize+1),
    sinks = [Target(port2.ID,port=1)],
    layer_id = flow_layer.ID
))



#########################################################################################################################################################
#Constraints
cpb1 = ArrayConstraint(verticalControlPorts)
cpb2 = ArrayConstraint(horizontalControlPorts)

device.add_constraint(cpb1)
device.add_constraint(cpb2)


#Make the tree horizontal
oc = OrientationConstraint()
oc.add_component_orientation_pair(tree1,ComponentOrientation.HORIZONTAL)
oc.add_component_orientation_pair(tree2,ComponentOrientation.HORIZONTAL)
device.add_constraint(oc)

#########################################################################################################################################################
fileName = 'grid_' + str(gridSize) + '.mint'
with open(fileName, 'w') as file:
    file.write(device.to_MINT())

with open('grid_' + str(gridSize) + ".json", 'w') as f:
    json.dump(device.device.to_parchmint_v1_2(), f, indent=2)

print("Complete")