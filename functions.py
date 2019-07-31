import bpy

import os
import math
from math import pi
from mathutils import Vector
import bpy.props as prop
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       IntProperty
                       )

# AGGIUNTA DI MODULO PER GIRARE LE UV

def GetObjectAndUVMap( objName, uvMapName ):
    try:
        obj = bpy.data.objects[objName]

        if obj.type == 'MESH':
            uvMap = obj.data.uv_layers[uvMapName]
            return obj, uvMap
    except:
        pass

    return None, None

#Scale a 2D vector v, considering a scale s and a pivot point p
def Scale2D( v, s, p ):
    return ( p[0] + s[0]*(v[0] - p[0]), p[1] + s[1]*(v[1] - p[1]) )

#Scale a UV map iterating over its coordinates to a given scale and with a pivot point
def ScaleUV( uvMap, scale, pivot ):
    for uvIndex in range( len(uvMap.data) ):
        uvMap.data[uvIndex].uv = Scale2D( uvMap.data[uvIndex].uv, scale, pivot )


#### fine modulo girare UV

def set_rotation_to_bubble(context,object,pano):
#    bpy.ops.object.select_all(action='DESELECT')
#    object.select = True
#    context.scene.objects.active = object
    bpy.ops.object.constraint_add(type='COPY_ROTATION')
    context.object.constraints["Copy Rotation"].target = pano
    bpy.ops.object.visual_transform_apply()
    bpy.ops.object.constraints_clear()

    bpy.ops.object.constraint_add(type='LIMIT_DISTANCE')
    bpy.context.object.constraints["Limit Distance"].target = pano
    bpy.context.object.constraints["Limit Distance"].distance = 1.6
    bpy.context.object.constraints["Limit Distance"].limit_mode = 'LIMITDIST_ONSURFACE'
    bpy.ops.object.visual_transform_apply()
    bpy.ops.object.constraints_clear()



def PANO_list_clear(context):
    scene = context.scene
    scene.pano_list.update()
    list_lenght = len(scene.pano_list)
    for x in range(list_lenght):
        scene.pano_list.remove(0)
    return

def e2d(float_value):
    return (float_value/fac)

def create_tex_from_file(ItemName,path_dir,extension):
    realpath = path_dir + ItemName #+ '.' + extension
    try:
        img = bpy.data.images.load(realpath)
    except:
        raise NameError("Cannot load image %s" % realpath)
    # Create image texture from image
    diffTex = bpy.data.textures.new('TEX_'+ItemName, type = 'IMAGE')
    diffTex.image = img
    return diffTex

def create_mat(ob):
    context = bpy.context
    scene = context.scene

    ob = scene.objects.active
    mat = bpy.data.materials.new(name="MAT_"+ob.name) #set new material to variable
    ob.data.materials.append(mat)
    mat.use_transparency = True
    mat.alpha = 0.75 #add the material to the object
    return mat

def assign_tex2mat(DiffTex,newmat):
    mtex = newmat.texture_slots.add()
    mtex.texture = DiffTex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True
    mtex.use_map_color_emission = True
    mtex.emission_color_factor = 0.5
    mtex.use_map_density = True
    mtex.mapping = 'FLAT'
    mtex.alpha_factor = 0

def readfile(filename):
    f=open(filename,'r') # open file for reading
    arr=f.readlines()[2:]  # store the entire file in a variable
    f.close()
    return arr

def remove_extension(string):
    return string.replace(".jpg", "")

def flipnormals():
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    # Operation in edit mode
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


def create_cam(name,pos_x,pos_y,pos_z):
  # create camera data
    cam_data = bpy.data.cameras.new('CAM_'+name)
    cam_data.draw_size = 0.15
    cam_data.lens = bpy.context.scene.PANO_cam_lens
    # create object camera data and insert the camera data
    cam_ob = bpy.data.objects.new('CAM_'+name, cam_data)
    # link into scene
    bpy.context.scene.objects.link(cam_ob)
    cam_ob.location.x = pos_x
    cam_ob.location.y = pos_y
    cam_ob.location.z = pos_z
    cam_ob.rotation_euler.x = e2d(90)