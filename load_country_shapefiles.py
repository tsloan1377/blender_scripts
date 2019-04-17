#  A script to test and familiarize myself with functions for loading data from csv into blender, and related experiments.

# Based off of load_globe_data.py, check there is something doesn't make sense...
import bpy
import math
import csv
import bmesh
import numpy as np


data_path = 'E:\Documents\Professional\Jupyter notebooks\Projects\Weather\export\shapeCoords.csv'
base_r = 3
n_rows = np.nan
file = csv.reader(open(data_path, newline=''), delimiter=',')

def GetSphere(source):
    data = list() # Placeholder for storing lat and long coordinates.
    with open(source, 'r') as csvdata:
        dataset = csv.reader(open(source, newline=''), delimiter=',')
        for row in dataset:
            data.append((float(row[0]), float(row[1])))
    csvdata.close()

    return data
    
    
def GetValues(source):
    
    data = list() # Placeholder for storing lat and long coordinates.
    with open(source, 'r') as csvdata:
        dataset = csv.reader(open(source, newline=''), delimiter=',')
        for row in dataset:
            data.append((float(row[0]), float(row[1])))
            #print(row[0], row[1])
    csvdata.close()

    return data    

def TransformData(data, values=[]):
    global n_rows
    data_sphere = list() 
    n_rows = len(data)
    data_array = np.empty([n_rows,3])
    for i in range(0,len(data)):
        latitude = data[i][1]
        longitude = data[i][0]
        
        if (len(values)>0):

            r = -base_r # Negative value creates a backwards sphere - looking at the globe from within.
        else:
            r = -base_r
        
        x = r * math.cos(math.radians(latitude)) * math.cos(math.radians(longitude))
        y = r * math.cos(math.radians(latitude)) * math.sin(math.radians(longitude))
        z = r * math.sin(math.radians(latitude))
           
        data_sphere.append(([x, y, z]))
        data_array[i,:] = [x,y,z]
   
    return data_array #data_sphere

def DrawSphere(data, values=[]):
    

    mesh = bpy.data.meshes.new("Mesh")  # add a new mesh
    obj = bpy.data.objects.new("MyObject", mesh)  # add a new object using the mesh
    
    scene = bpy.context.scene
    scene.objects.link(obj)  # put the object into the scene (link)
    scene.objects.active = obj  # set as the active object in the scene
    obj.select = True  # select object

    mesh = bpy.context.object.data
    bm = bmesh.new()    
    
    

    
    for i in range(n_rows):   
        x = data[i][0]
        y = data[i][1]
        z = data[i][2]
        
        bm.verts.new([x, y, z])  # add a new vert
        

        
    # make the bmesh the object's mesh
    bm.to_mesh(mesh)  
    bm.free()  # always do this when finished 
    
data = GetValues(data_path)
data = TransformData(data)


data = data[data[:,1].argsort()] # Sort data by y value
DrawSphere(data)