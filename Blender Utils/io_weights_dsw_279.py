# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Export: Dora SkinWeight (.dsw)",
    "description": "Export vertex weights to Dora Skin Weight v3.0 format",
    "author": "Me",
    "version": (0, 0),
    "blender": (2, 78, 0),
    "location": "File > Export > Dora SkinWeight (.dsw)",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from decimal import *

def write_some_data(context, filepath):
    obj = bpy.context.active_object
    f = open(filepath, 'w', encoding='utf-8')
    f.write(weightDat(obj))
    f.close()

    return {'FINISHED'}

def getVs(obj, gLi):
    rStr = ''
    for v in obj.data.vertices: # itr = new line
        vLi = [] # fresh vert list 
        for i, g in enumerate(gLi): # itr = weight in first entry
            for w in v.groups: # checks vert weights against vert groups
                if i == w.group:
                    weight = round(Decimal(w.weight), 6) #kinda wonky rounding system...
                    if weight == int(weight):
                        weight = int(weight)
                    break
                else:
                    weight = 0
            vLi.append(weight) # append float/str to list
        vStr = ','.join(str(e) for e in vLi) # vert list to string
        rStr += vStr + "\n" # garbage data(|vCo|??|) Makes no difference when left at zeros
    return rStr
    
def getGroups(obj):
    gStr, gLi = "", []
    
    for i, gr in enumerate(obj.vertex_groups): #Str and Li from all vGroups
        if i > 0:      
            gStr += ','
        gStr += gr.name
        gLi.append(gr.name)
    return gStr + '\n', gLi


def weightDat(obj):
    gStr, gLi = getGroups(obj) #need to find out if the order/number of groups actually matters
    wStr = "DoraYuki Skin Weight Format 3.00\n" + gStr + getVs(obj, gLi) # mel script checks for \n specifically
        
    
    return wStr

class ExportWeights(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_weights.dsw"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Weights"

    # ExportHelper mixin class uses this
    filename_ext = ".dsw"

    filter_glob = StringProperty(
            default="*.dsw",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def execute(self, context):
        return write_some_data(context, self.filepath)


def menu_dat(self, context):
    self.layout.operator(ExportWeights.bl_idname, text="Dora SkinWeight (.dsw)")


def register():
    bpy.utils.register_class(ExportWeights)
    bpy.types.INFO_MT_file_export.append(menu_dat)# change to v group panel?


def unregister():
    bpy.utils.unregister_class(ExportWeights)
    bpy.types.INFO_MT_file_export.remove(menu_dat)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_weights.dsw('INVOKE_DEFAULT')
