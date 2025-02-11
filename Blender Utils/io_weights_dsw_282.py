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
    "blender": (2, 80, 0),
    "location": "File > Export > Dora SkinWeight (.dsw)",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from decimal import *

def read_weight_data(context, filepath):
    vLi = []
    obj = context.active_object 
    with open(filepath, 'r') as data: 

        if 'DoraYuki Skin Weight Format' not in data.readline(): #Abort if not basic dsw format
            context.window_manager.popup_menu(abort, title="Unexpected File Format", icon='ERROR')
            return {'FINISHED'}

        gLi = data.readline().replace('\n', '').split(',') #Grab and format list of vertex groups
        order = orderGroups(context, obj.vertex_groups, gLi) #Weight group order, number, name, format check 
        
        if order is None: #Abort if group name/order mismatch between origin and destination data
            context.window_manager.popup_menu(abort, title="Mismatched Weight Groups", icon='ERROR')
            return {'FINISHED'} 

        for line in data: 
            t = [float(x) for x in line.split('|')[0].split(',')]
            t = [t[i] for i in order] #Rearanges incoming data, not destination mesh
            vLi.append(t) #Vertex weight list, reordered to match destination mesh's weight group order
            # Formatted to match: [obj.vertex_groups[0], obj.vertex_groups[1], obj.vertex_groups[2], ...]

        if len(obj.data.vertices) != len(vLi): #Abort if different vert counts
            context.window_manager.popup_menu(abort, title="Mismatched Topology Error", icon='ERROR')
            return {'FINISHED'} 
        
        if setWeights(obj, vLi): #Use incoming formatted data
        
            context.window_manager.popup_menu(zeroWarning, title="Data Warning", icon='MESH_DATA')

        return {'FINISHED'}


def abort(self, context):
    self.layout.label(text = " - Aborting")
    return

def zeroWarning(self, context):
    self.layout.label(text = "Zero weights added to vertex groups. Import Successful")    

def orderGroups(context, vGr, gLi):
    order = []
    if len(vGr) != len(gLi): #Abort. Does not assume or autofill weight groups
        return None

    for vg in vGr: #Creates list of indices for vert group order matching
        for i, lg in enumerate(gLi): 
            if lg == vg.name:
                order.append(i) 
                break

    if len(order) == len(vGr): #Aborts on name changes/typos
        return order
    else:
        return None

def setWeights(obj, vLi):
    zw = False
    vGr = obj.vertex_groups
    for g in vGr: 
        for i, v in enumerate(vLi):
            g.add([i], v[g.index], 'REPLACE') #Weights all verts 0-1, by group
            #Warning: Adds weights for all groups to vert data, even if zero

            if g.index == 0.0:
                zw = True
    return zw

def write_weight_data(context, filepath):
    obj = context.active_object
    f = open(filepath, 'w', encoding='utf-8')
    f.write(weightDat(obj))
    f.close()

    return {'FINISHED'}

def weightDat(obj):
    gStr, gLi = getGroups(obj) #order/number of groups doesn't seem to matter for DSW import
    wStr = "DoraYuki Skin Weight Format 3.00\n" + gStr + getVs(obj, gLi) # mel script checks for \n specifically
        
    return wStr
    
def getGroups(obj):
    gStr, gLi = "", []
    
    for i, gr in enumerate(obj.vertex_groups): #Str and Li from all vGroups
        if i > 0:      
            gStr += ','
        gStr += gr.name
        gLi.append(gr.name)
    return gStr + '\n', gLi

def getVs(obj, gLi):
    rStr = ''

    for v in obj.data.vertices: # itr = new line
        vLi = [] # fresh vert list 
        weight = 0
        for i, g in enumerate(gLi): # itr = weight in first entry
            for w in v.groups: # checks vert weights against vert groups
                #weight = 0
                if i == w.group:
                    weight = round(Decimal(w.weight), 6) #kinda wonky rounding system...
                    if weight == int(weight):
                        weight = int(weight)
                    break
                else:
                    weight = 0
            vLi.append(weight) # append float/str to list
        vStr = ','.join(str(e) for e in vLi) # vert list to string
        rStr += vStr + "\n" # extra data(|vCo|??|) Makes no difference when left at zeros
    return rStr

class ExportWeights(Operator, ExportHelper):
    bl_idname = "export_weights.dsw"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Weights"

    # ExportHelper mixin class uses this
    filename_ext = ".dsw"

    filter_glob: StringProperty(
            default="*.dsw",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def execute(self, context):
        return write_weight_data(context, self.filepath)

class ImportWeights(Operator, ImportHelper):
    bl_idname = "import_weights.dsw"
    bl_label = "Import Weights"

    filter_glob: StringProperty(
        default="*.dsw",
        options={'HIDDEN'},
    )
    directory: StringProperty(
        subtype='DIR_PATH',
    )

    def execute(self, context):
        return read_weight_data(context, self.filepath)




def export_menu(self, context):
    self.layout.operator(ExportWeights.bl_idname, text="Dora SkinWeight (.dsw)")

def import_menu(self, context):
    self.layout.operator(ImportWeights.bl_idname, text="Dora SkinWeight (.dsw)")


classes = (
    ExportWeights,
    ImportWeights
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(export_menu)
    bpy.types.TOPBAR_MT_file_import.append(import_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(export_menu)
    bpy.types.TOPBAR_MT_file_import.remove(import_menu)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.export_weights.dsw('INVOKE_DEFAULT') #can't do this if import/export
