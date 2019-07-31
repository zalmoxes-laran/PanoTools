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
from .functions import *
from bpy.types import Menu, Panel, UIList, PropertyGroup



class PANOToolsPanel:

    bl_label = "Panorama suite"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

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

class VIEW3D_PT_SetupPanel(Panel, PANOToolsPanel):
    bl_category = "Pano"
    bl_idname = "VIEW3D_PT_SetupPanel"
    bl_context = "objectmode"

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