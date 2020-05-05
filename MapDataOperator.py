import os
import bpy
from bpy_extras.io_utils import ImportHelper 
from bpy.types import Operator

class MapDataOperator(Operator, ImportHelper):
    bl_idname = "tm_importer.map_data_operator"
    bl_label = "Import Map Data"

    filename_ext = ".txt"

    filter_glob: bpy.props.StringProperty(
        default = "*.json",
        options = { 'HIDDEN' }
    )

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        
        print('Selected file:', self.filepath) 
        print('File name:', filename) 
        print('File extension:', extension)

        return { 'FINISHED' }