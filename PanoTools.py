bl_info = {
    "name": "Pano Importer",
    "author": "E. Demetrescu, E. D'Annibale",
    "version": (1,0,5),
    "blender": (2, 7, 9),
    "location": "Tool Shelf panel",
    "description": "Importer for equirectangular panoramas",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools"}

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

#def variables (only for early coding)
fac = 180/pi

pivot = Vector( (0.5, 0.5) )
scale = Vector( (-1, 1) )
uvMapName = 'UVMap'

#WINDOWS
#filename='/Users/emanueldemetrescu/Dropbox/DEVELOPMENT_BLENDER_SCRIPTS/GestionePanoramiBlender/test.txt'  # enter the complete file path here
#path_dir='E:\Dropbox\DEVELOPMENT_BLENDER_SCRIPTS\GestionePanoramiBlender\4k'  # enter the complete file path here
#MAC
#filename='/Users/emanueldemetrescu/Dropbox/DEVELOPMENT_BLENDER_SCRIPTS/GestionePanoramiBlender/test3.txt'  # enter the complete file path here
#path_dir='/Users/emanueldemetrescu/Dropbox/DEVELOPMENT_BLENDER_SCRIPTS/GestionePanoramiBlender/4k/'  # enter the complete file path here
extension='jpg'

class PANOListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    name = prop.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    icon = prop.StringProperty(
           name="code for icon",
           description="",
           default="GROUP_UVS")

class PANO_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = context.scene
        layout.label(item.name, icon = item.icon)
#        layout.label(item.description, icon='NONE', icon_value=0)

class PANOToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "PANO"
    bl_label = "Panorama suite"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        row = layout.row()
        row.label(text="PANO file")
        row = layout.row()
        row.prop(context.scene, 'PANO_file', toggle = True)
        row = layout.row()
        row.prop(context.scene, 'PANO_dir', toggle = True)
        row = layout.row()
        self.layout.operator("import.pano", icon="GROUP_UVS", text='Read/Refresh PANO file')
        row = layout.row()
#        self.layout.operator("uslist_icon.update", icon="PARTICLE_DATA", text='Only icons refresh')
#        row = layout.row()
        layout.alignment = 'LEFT'
        row.template_list("PANO_UL_List", "PANO nodes", scene, "pano_list", scene, "pano_list_index")
        if scene.pano_list_index >= 0 and len(scene.pano_list) > 0:
            item = scene.pano_list[scene.pano_list_index]
            row = layout.row()
            row.label(text="Name:")
            row = layout.row()
            row.prop(item, "name", text="")
#        if obj.type in ['CAMERA']:
#            obj = context.object
#            row = layout.row()
#            row.label(text="Active camera is: " + obj.name)
#            row = layout.row()
        row = layout.row()
        self.layout.operator("view.pano", icon="ZOOM_PREVIOUS", text='Inside the Pano')
        row = layout.row()
        self.layout.operator("remove.pano", icon="ERROR", text='Remove the Pano')
        
        

        row = layout.row()
        row = layout.row()
        self.layout.operator("align.quad", icon="OUTLINER_OB_FORCE_FIELD", text='Align quad')
        row = layout.row()
        
        split = layout.split()
        # First column
        col = split.column()
        col.label(text="Lens:")
        col.prop(context.scene, 'PANO_cam_lens', toggle = True)
#        col.prop(scene, "frame_start")

        # Second column, aligned
        col = split.column(align=True)
        col.label(text="Apply")
        col.operator("set.lens", icon="FILE_TICK", text='SL')
#        col.prop(scene, "frame_start")


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

class REMOVE_pano(bpy.types.Operator):
    bl_idname = "remove.pano"
    bl_label = "Remove selected Pano"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        data = bpy.data
        context = bpy.context
        scene = context.scene
        ob_pano = data.objects[scene.pano_list[scene.pano_list_index].name]
        cam_pano = data.objects['CAM_'+scene.pano_list[scene.pano_list_index].name]
        data.objects.remove(ob_pano)
        data.objects.remove(cam_pano)
        scene.pano_list.remove(scene.pano_list_index)
        scene.pano_list_index = scene.pano_list_index - 1
        return {'FINISHED'}

class VIEW_pano(bpy.types.Operator):
    bl_idname = "view.pano"
    bl_label = "View from the inside of selected Pano"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        data = bpy.data
        context = bpy.context
        scene = context.scene
        pano_list_index = scene.pano_list_index
        current_camera_name = 'CAM_'+scene.pano_list[pano_list_index].name
        current_camera_obj = data.objects[current_camera_name]
        scene.camera = current_camera_obj
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        current_pano = data.objects[scene.pano_list[pano_list_index].name]
        scene.objects.active = current_pano
        bpy.ops.object.select_all(action='DESELECT')
#        current_pano.select = True
        return {'FINISHED'}


class VIEW_alignquad(bpy.types.Operator):
    bl_idname = "align.quad"
    bl_label = "align the quad inside the active Pano"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        data = bpy.data
        context = bpy.context
        scene = context.scene
        pano_list_index = scene.pano_list_index
        current_camera_name = 'CAM_'+scene.pano_list[pano_list_index].name
        current_camera_obj = data.objects[current_camera_name]
#        scene.camera = current_camera_obj
        current_pano = data.objects[scene.pano_list[pano_list_index].name]
        object = context.active_object


#        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
#        area.spaces[0].region_3d.view_perspective = 'CAMERA'
#
#        scene.objects.active = current_pano
#        bpy.ops.object.select_all(action='DESELECT')
#        current_pano.select = True
        set_rotation_to_bubble(context,object,current_camera_obj)

        return {'FINISHED'}


class VIEW_setlens(bpy.types.Operator):
    bl_idname = "set.lens"
    bl_label = "set the lens of the camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        data = bpy.data
        context = bpy.context
        scene = context.scene
        pano_list_index = scene.pano_list_index
        current_camera_name = 'CAM_'+scene.pano_list[pano_list_index].name
        
         
        current_camera_obj = data.objects[current_camera_name]
        current_camera_obj.data.lens = scene.PANO_cam_lens
#        scene.camera = current_camera_obj
#        current_pano = data.objects[scene.pano_list[pano_list_index].name]
#        object = context.active_object


#        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
#        area.spaces[0].region_3d.view_perspective = 'CAMERA'
#
#        scene.objects.active = current_pano
#        bpy.ops.object.select_all(action='DESELECT')
#        current_pano.select = True
#        set_rotation_to_bubble(context,object,current_camera_obj)

        return {'FINISHED'}





class PANO_import(bpy.types.Operator):
    bl_idname = "import.pano"
    bl_label = "Import Panoramas from file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        data = bpy.data
        context = bpy.context
        scene = context.scene
        lines_in_file = readfile(scene.PANO_file)
        PANO_list_clear(context)
        pano_list_index_counter = 0
        scene.game_settings.material_mode = 'GLSL'
        scene.game_settings.use_glsl_lights = False
        # Parse the array:
        for p in lines_in_file:
#            p0 = p.split('\t')  # use space as separator
            p0 = p.split(' ')  # use space as separator
            print(p0[0])
            ItemName = p0[0]
            pos_x = float(p0[1])
            pos_y = float(p0[2])
            pos_z = (float(p0[3]))
            rot_x = float(p0[4])
            rot_y = float(p0[5])
            rot_z = float(p0[6])
            for model in data.objects:
                if model.name == remove_extension(ItemName) or model.name == "CAM_"+remove_extension(ItemName):
                    data.objects.remove(model)
            sph = bpy.ops.mesh.primitive_uv_sphere_add(calc_uvs=True, size=2, location=(pos_x,pos_y,pos_z))
            just_created_obj = scene.objects.active
            just_created_obj.name = remove_extension(ItemName)
            just_created_obj.rotation_euler[2] = e2d(-90)
            bpy.ops.object.transform_apply(rotation = True)
#            just_created_obj.rotation_euler[0] = e2d(-(rot_x-90))
            just_created_obj.rotation_euler[0] = e2d(-(rot_x))
            just_created_obj.rotation_euler[1] = e2d(rot_z)
#            just_created_obj.rotation_euler[2] = e2d(180+rot_y)
            just_created_obj.rotation_euler[2] = e2d(rot_y)
            obj, uvMap = GetObjectAndUVMap( just_created_obj.name, uvMapName )
            ScaleUV( uvMap, scale, pivot )
            newmat = create_mat(just_created_obj)
            diffTex = create_tex_from_file(ItemName,scene.PANO_dir,extension)
            assign_tex2mat(diffTex,newmat)
            scene.pano_list.add()
            scene.pano_list[pano_list_index_counter].name = just_created_obj.name
#            scene.pano_list[pano_list_index_counter].icon = qui possiamo mettere una regola
            flipnormals()
            create_cam(just_created_obj.name,pos_x,pos_y,pos_z)
            pano_list_index_counter += 1
        scene.update()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PANOToolsPanel)
    bpy.utils.register_class(PANO_import)
    bpy.utils.register_class(PANOListItem)
    bpy.utils.register_class(PANO_UL_List)
    bpy.utils.register_class(VIEW_pano)
    bpy.utils.register_class(REMOVE_pano)
    bpy.utils.register_class(VIEW_alignquad)
    bpy.utils.register_class(VIEW_setlens)
    
    


# here I register the PANO element list
    bpy.types.Scene.pano_list = prop.CollectionProperty(type = PANOListItem)
    bpy.types.Scene.pano_list_index = prop.IntProperty(name = "Index for my_list", default = 0)
    bpy.types.Scene.PANO_file = StringProperty(
      name = "TXT",
      default = "",
      description = "Define the path to the PANO file",
      subtype = 'FILE_PATH'
      )

    bpy.types.Scene.PANO_dir = StringProperty(
      name = "DIR",
      default = "",
      description = "Define the path to the PANO file",
      subtype = 'DIR_PATH'
      )

    bpy.types.Scene.PANO_cam_lens = IntProperty(
      name = "Cam Lens",
      default = 21,
      description = "Define the lens of the cameras",
#      subtype = 'FILE_PATH'
      )

def unregister():
#    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.pano_list
    del bpy.types.Scene.pano_list_index
    bpy.utils.unregister_class(REMOVE_pano)
    bpy.utils.unregister_class(PANOToolsPanel)
    bpy.utils.unregister_class(PANO_import)
    bpy.utils.unregister_class(PANOListItem)
    bpy.utils.unregister_class(PANO_UL_List)
    bpy.utils.unregister_class(VIEW_pano)
    bpy.utils.unregister_class(VIEW_alignquad)
    del bpy.types.Scene.PANO_file
    del bpy.types.Scene.PANO_dir
    bpy.utils.unregister_class(VIEW_setlens)

if __name__ == "__main__":
    register()
