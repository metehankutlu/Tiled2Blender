import os
import bpy
import bmesh
import json
import sys
import imghdr
import struct
sys.path.append(os.path.dirname(__file__))
from . import pytmx
import importlib
from bpy.types import Operator
from .MapDataOperator import MapDataOperator


class ImportOperator(Operator):
    bl_idname = "tm_importer.import_operator"
    bl_label = "Import"

    def execute(self, context):

        map_data_path = MapDataOperator.filepath

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

        tiled_map = pytmx.TiledMap(map_data_path)
        for layer_index, layer in enumerate(tiled_map.visible_layers):
            tiled_map
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        image_name = os.path.basename(tile[0])
                        image_width, image_height = get_image_size(tile[0])
                        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(x, -y, layer_index * 0.001))
                        plane = bpy.context.active_object
                        bpy.context.active_object
                        me = plane.data
                        if image_name in bpy.data.materials:
                            mat = bpy.data.materials[image_name]
                        else:
                            mat = bpy.data.materials.new(name=image_name)
                            mat.use_nodes = True
                            bsdf = mat.node_tree.nodes['Principled BSDF']
                            tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
                            if image_name not in bpy.data.images:
                                bpy.ops.image.open(filepath=tile[0])
                            tex.image = bpy.data.images[image_name]
                            mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])
                            mat.node_tree.links.new(bsdf.inputs['Alpha'], tex.outputs['Alpha'])
                            mat.blend_method = 'ALPHA_BLEND'
                        if plane.data.materials:
                            plane.data.materials[0] = mat
                        else:
                            plane.data.materials.append(mat)
                        bpy.ops.object.mode_set(mode='EDIT')
                        bm = bmesh.from_edit_mesh(me)
                        uv_layer = bm.loops.layers.uv.verify()
                        bm.faces.ensure_lookup_table()
                        tile_x, tile_y, tile_width, tile_height = tile[1]
                        bm.faces[0].loops[0][uv_layer].uv = ((tile_x / tile_width) / (image_width / tile_width), 1 - (tile_y / tile_height + 1) / (image_height / tile_height))
                        bm.faces[0].loops[1][uv_layer].uv = ((tile_x / tile_width + 1) / (image_width / tile_width), 1 - (tile_y / tile_height + 1) / (image_height / tile_height))
                        bm.faces[0].loops[2][uv_layer].uv = ((tile_x / tile_width + 1) / (image_width / tile_width), 1 - (tile_y / tile_height) / (image_height / tile_height))
                        bm.faces[0].loops[3][uv_layer].uv = ((tile_x / tile_width) / (image_width / tile_width), 1 - (tile_y / tile_height) / (image_height / tile_height))
                        bmesh.update_edit_mesh(me)
                        bpy.ops.object.mode_set(mode='OBJECT')

        return { 'FINISHED' }

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height