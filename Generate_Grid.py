from pymint import MINTDevice, MINTLayerType
from parchmint.target import Target
from parchmint import Device
from pymint.constraints.arrayconstraint import ArrayConstraint
from pymint.constraints.orientationconstraint import OrientationConstraint, ComponentOrientation
import json

numFlowConnections = 0
numControlConnections = 0
numControlNets = 0
numValves = 0

sctList = []
flowConnections = []
controlConnections = []
controlNets = []
valves = []

#List of control ports that control the vertical and horizontal connections respectively 
#that connect the square cell traps
verticalControlPorts = []
horizontalControlPorts = []


#Set component parameters
trap_params = {
    "chamberWidth": 100,
    "chamberLength": 100,
    "channelWidth": 100
}

tree_params = {
    "spacing": 1200,
    "flowChannelWidth": 100 
}

flow_connection_params = {
    "w": 100
}

control_connection_params = {
    "w": 100
}

valve_params = {
    "w": 300,
    "l": 100
}

#Prompt user for grid size
gridSize = int(input("Please enter a grid size: "))

# Create the MINTDevice instance with a name
device = MINTDevice(name="grid_" + str(gridSize) + "_device")

########################################################################################################################################################
# Create the flow layer
flow_layer = device.create_mint_layer(ID="flow", name_postfix="FLOW", group=None, layer_type=MINTLayerType.FLOW)

# Create the control layer
control_layer = device.create_mint_layer(ID="control", name_postfix="CONTROL", group=None, layer_type=MINTLayerType.CONTROL)

# Create the ports on the flow layer
port1 = device.add_terminal(name="p1", pin_number=1 , layer_id=flow_layer.ID)
port2 = device.add_terminal(name="p2", pin_number=1 , layer_id=flow_layer.ID)

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
    params=tree_params,
    layer_ids=[flow_layer.ID]
)
tree2 = device.create_mint_component(
    name="m2",
    technology="TREE",
    params=tree_params,
    layer_ids=[flow_layer.ID]
)

#Connect tree1 to port1 
numFlowConnections+=1

flowConnections.append(device.create_mint_connection(
    name = "c"+str(numFlowConnections),
    technology = "CONNECTION",
    params = flow_connection_params,
    source = Target(port1.component.ID),
    sinks = [Target(tree1.ID,port=1)],
    layer_id = flow_layer.ID
))

#Connect tree1 to first column of square cell traps
for row in range(1,gridSize+1):
    numFlowConnections+=1
    flowConnections.append(device.create_mint_connection(
        name = "c"+str(numFlowConnections),
        technology = "CONNECTION",
        params = flow_connection_params,
        source = Target(tree1.ID,port=1+row),
        sinks = [Target(sctList[row-1].ID,port=4)],
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

    tempTargetList = []

    for valve in valves[-(gridSize-1):]:
        tempTargetList.append(Target(valve.ID))

    numControlNets+=1
    controlNets.append(device.create_mint_connection(
            name = "n"+str(numControlNets),
            technology = "CONNECTION",
            params = control_connection_params,
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

            #Put connections between the valves on horizontal connections
            if(row!=1):
                numControlConnections+=1
                controlConnections.append(device.create_mint_connection(
                    name = "cc" + str(numControlConnections),
                    technology = "CONNECTION",
                    params = control_connection_params,
                    source = Target(valves[-2].ID),
                    sinks = [Target(valves[-1].ID)],
                    layer_id = control_layer.ID
                ))
                


        #Create control port
        horizontalControlPorts.append(device.add_terminal(
            name="hcp" + str(col),
            pin_number=1 ,
            layer_id=control_layer.ID
        ))

        #Connect the control port to the valves on the "bottom" of grid
        numControlConnections+=1
        controlConnections.append(device.create_mint_connection(
            name = "cc" + str(numControlConnections),
            technology = "CONNECTION",
            params = control_connection_params,
            source = Target(valves[-1].ID),
            sinks = [Target(horizontalControlPorts[-1].component.ID)],
            layer_id = control_layer.ID
        ))


#Connect last row of square cell traps to tree2
for row in range(1,gridSize+1):
    numFlowConnections+=1
    flowConnections.append(device.create_mint_connection(
        name = "c"+str(numFlowConnections),
        technology = "CONNECTION",
        params = flow_connection_params,
        source = Target(sctList[(gridSize)*(gridSize-1)+row-1].ID,port="2"),
        sinks = [Target(tree2.ID,port=str(row))],
        layer_id = flow_layer.ID
    ))

#Connect tree2 to port2
numFlowConnections+=1
flowConnections.append(device.create_mint_connection(
    name = "c"+str(numFlowConnections),
    technology = "CONNECTION",
    params = flow_connection_params,
    source = Target(tree2.ID,port=gridSize+1),
    sinks = [Target(port2.component.ID)],
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