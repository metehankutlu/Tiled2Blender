import bpy
from bpy.types import Operator


class ImportButtonOperator(Operator):
    bl_idname = "tiled_2_blender.import_operator"
    bl_label = "Import"

    def execute(self, context):
        bpy.ops.tiled_2_blender.timer_operator('INVOKE_DEFAULT')
        return { 'FINISHED' }