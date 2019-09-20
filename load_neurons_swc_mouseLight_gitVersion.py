# A script to run in Blender 2.8 to load a collection of neurons from MouseLight. 
# Data can be downloaded from 

# This script largely using code from Martin Pyka's SWC2Blender package, that I wasn't able to have running in Blender 2.8 without some modifications. 
http://www.martinpyka.de/swc-neuromorph-org-importer-for-blender/

# Whereas the original script loads each segment of the neuron as an individual curve, 
# I've added functions to combine the curves for each neuron, to convert them to a mesh and decimate by 
# A factor of DEC_RATIO. 

# For each neuron, I added an emission material which has its strength driven by random noise.

import bpy
import random
import os
import math
from datetime import datetime

scale_f = 1000  # factor to downscale the data

#read swc file '''
# Janelia
path = 'my_path/Janelia/MouseLight/'

#ration to decimate each mesh (simplifies when loading many)
DEC_RATIO = 0.01


# Function definitions

def load_neuron(this_neuron):
    
    neuron_file = path + this_neuron# +'.swc'

    f = open(neuron_file)
    lines = f.readlines()
    f.close()

    # find starting point '''
    x = 0
    while lines[x][0] is '#':
        x += 1
        
    # Create a dictionary with the first item '''
    #data = lines[x].strip().split(' ')   # Space as separator for Allen BigNeuron
    data = lines[x].strip().split('\t')   # Tab as separator for Janelia Mouselight
    neuron = {float(data[0]): [float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6])]}
    x += 1
        
    # Read the rest of the lines to the dictionary '''
    for l in lines[x:]:
        #data = l.strip().split(' ') # Space as separator for Allen BigNeuron
        data = l.strip().split('\t')# Tab as separator for Janelia Mouselight
        neuron[float(data[0])] = [float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6])]
        
    bpy.ops.object.empty_add(type='ARROWS', location=(0.0, 0.0, 0.0), rotation=(0, 0, 0))
    a = bpy.context.selected_objects[0]    
    a.name = this_neuron



    last = -10.0

    # Create object '''
    for key, value in neuron.items():
        
        if value[-1] == -1:
            continue
        
        if value[0] == 10:
            continue

        if (value[-1] != last):
             # trace the origins
            tracer = bpy.data.curves.new('tracer','CURVE')
            tracer.dimensions = '3D'
            spline = tracer.splines.new('BEZIER')

            curve = bpy.data.objects.new('curve',tracer)
            bpy.context.collection.objects.link(curve)   # Since 2.8, this is the way to do this
                 
            # render ready curve
            tracer.resolution_u = 8
            tracer.bevel_resolution = 8 # Set bevel resolution from Panel options
            tracer.fill_mode = 'FULL'
            tracer.bevel_depth = 0.001 # Set bevel depth from Panel options
            
            # move nodes to objects
            p = spline.bezier_points[0]
            p.co = [neuron[value[-1]][3] / scale_f, neuron[value[-1]][2] / scale_f, neuron[value[-1]][1] / scale_f]
            p.handle_right_type='VECTOR'
            p.handle_left_type='VECTOR'
            
            if (last > 0):
                spline.bezier_points.add(1)            
                p = spline.bezier_points[-1]
                p.co = [value[3]/scale_f, value[2]/scale_f, value[1]/scale_f]
                p.handle_right_type='VECTOR'
                p.handle_left_type='VECTOR'

            curve.parent = a
        
        if value[-1] == last:
            spline.bezier_points.add(1)
            p = spline.bezier_points[-1]
            p.co = [value[3]/scale_f, value[2]/scale_f, value[1]/scale_f]
            p.handle_right_type='VECTOR'
            p.handle_left_type='VECTOR'
        
        last = key


def combine_curves(this_neuron):
    context = bpy.context
    scene = context.scene
    o = bpy.context.scene.objects[curr_neuron]  
    # deselect all
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = o
    # select all children recursively
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    # select parent too
    o.select_set(state=True)
    context.view_layer.objects.active = context.selected_objects[1]    
    # join them
    bpy.ops.object.join()
    


def mesh_and_decimate(this_neuron, DEC_RATIO):
    
    o = bpy.context.scene.objects[curr_neuron] 
    
    for child in o.children:
        # Convert to mesh
        bpy.ops.object.convert(target='MESH')    
        
        # Decimate the mesh
        modifierName='DecimateMod'
        modifier=child.modifiers.new(modifierName,'DECIMATE')
        modifier.ratio=DEC_RATIO
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        
        

def color_heir(ob, mat):     #, levels=10):
    for child in ob.children:
        #activeObject = bpy.context.active_object #Set active object to variable (This gets the scene level active object (parent)
        #print(child.name,activeObject.name)       
        child.data.materials.append(mat) #add the material to the object 



#
# Control flow
#

# Load a single neuron
#curr_neuron = 'AA0001'
#load_neuron(curr_neuron)

# Load a list of neurons
#neurons = ['AA0001.swc','AA0002.swc', 'AA0003.swc']

neurons = os.listdir(path)    # Process all swc files in a folder

for i in range(len(neurons)):    # The way I can do it so it's easier to hack to test smaller numbers
    curr_neuron = neurons[i]           # Remember to remove this if doing the loop in a more pythonic way. (Using: for curr_neuron in neurons)
    #print(curr_neuron)
    
    # In each case below, curr_neuron is a string
    load_neuron(curr_neuron)
    combine_curves(curr_neuron)
    mesh_and_decimate(curr_neuron, DEC_RATIO)
    #bpy.context.scene.objects[curr_neuron].select_set(True) # Select neuron (parent empty) by name.
    
    # Get the object identified by the string
    ob = bpy.context.scene.objects[curr_neuron]
    
    # Rotate the neuron.
    ob.rotation_euler[0] = math.radians(90)
    print(i,curr_neuron, 'at: ', datetime.now())
    
    # Do material in same loop
    
    mat = bpy.data.materials.new(name=curr_neuron) #set new material to variable
    mat.diffuse_color = (random.random(), random.random(), random.random(), 1) # Simplest method is to create diffuse colored shader.
    
    # Extra steps for the material to create an emission shader.
    

    # get the nodes
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
        
    # clear all nodes to start clean
    nodes.clear()
    
    # create emission node
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_emission.inputs[0].default_value = (random.random(),random.random(),random.random(),1)  # green RGBA
    node_emission.inputs[1].default_value = 0 # strength
    node_emission.location = 0,0
    
    # create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')   
    node_output.location = 400,0   
    
    # link nodes
    links = mat.node_tree.links
    link = links.new(node_emission.outputs[0], node_output.inputs[0])

    # Keyframe the default value of the emission (like when inputting manually)
    node_emission.inputs[1].keyframe_insert('default_value', frame=1)
    
    # Get the Fcurve and add some noise.
    fcurve = mat.node_tree.animation_data.action.fcurves[0]
    mod = fcurve.modifiers.new("NOISE")
    # Change the fcurve settings.
    mod.scale = 10 # Scaling the time (determines how quickly changes happen
    mod.strength = 5 # Amplitude
    mod.phase = random.uniform(0, 1000)   # The random seed: (Could try using this to make neighboring neurons closer in their firing patterns.
    mod.offset = 0 # Translate the signal in time (may be useful for hebbian synapses)
    mod.depth = 0 # How complex is the signal.
   
    # Apply the material to each of the children of the object (in this case individual segments of the neuron (empty))
    for child in ob.children:
        
        child.data.materials.append(mat) #add the material to the object 

