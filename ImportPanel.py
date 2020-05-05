import bpy

class ImportPanel(bpy.types.Panel):
    bl_idname = "tm_importer.import_panel"
    bl_label = "Import Tilemap"
    bl_category = "TM Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Map data: ")

        row = layout.row()
        row.operator('tm_importer.map_data_operator', text='Import Map Data')

        layout.label(text="Tileset: ")

        row = layout.row()
        row.operator('tm_importer.tileset_operator', text='Import Tileset')