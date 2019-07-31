'''
Creative commons BY-NC 2018 Emanuel Demetrescu

Created by EMANUEL DEMETRESCU 2018-2019
emanuel.demetrescu@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Pano Importer",
    "description": "Importer for equirectangular panoramas",
    "author": "E. Demetrescu, E. D'Annibale",
    "version": (1, 0, 6),
    "blender": (2,80, 0),
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools",
    }

# load and reload submodules
##################################

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

from . import (
        UI,
        functions,
        )

from .functions import *
from bpy.utils import register_class, unregister_class

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


# register
##################################

classes = (
    UI.REMOVE_pano,
    UI.VIEW_pano,
    UI.VIEW_alignquad,
    UI.VIEW_setlens,
    UI.PANO_import,
    UI.VIEW3D_PT_SetupPanel, 
    PANO_UL_List,
    PANOListItem
    )

    #bpy.utils.register_class(PANOToolsPanel)

    #bpy.types.INFO_HT_header.append(draw_item)

def register():
    for cls in classes:
            bpy.utils.register_class(cls)

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
    for cls in classes:
        bpy.utils.unregister_class(cls)
