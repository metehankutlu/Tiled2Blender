import bpy
from .MapDataOperator import MapDataOperator
from .ImportButtonOperator import ImportButtonOperator

class ImportPanel(bpy.types.Panel):
    bl_idname = "tiled_2_blender.import_panel"
    bl_label = "Import Tilemap"
    bl_category = "Tiled2Blender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Map data: ")

        if MapDataOperator.filepath != '':
            row = layout.row()
            row.label(text=MapDataOperator.filepath)

        row = layout.row()
        row.operator(MapDataOperator.bl_idname)

        if MapDataOperator.filepath != '':
            row = layout.row()
            row.operator(ImportButtonOperator.bl_idname)