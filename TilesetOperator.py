import os
import bpy
from bpy_extras.io_utils import ImportHelper 
from bpy.types import Operator

class TilesetOperator(Operator, ImportHelper):
    bl_idname = "tm_importer.tileset_operator"
    bl_label = "Import Tileset"

    filter_glob: bpy.props.StringProperty(
        default = "*.jpg;*.jpeg;*png;*tiff;",
        options = { 'HIDDEN' }
    )

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        
        print('Selected file:', self.filepath) 
        print('File name:', filename) 
        print('File extension:', extension)

        return { 'FINISHED' }