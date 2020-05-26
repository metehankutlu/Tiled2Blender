import os
import bpy
import bmesh
import json
import sys
import imghdr
import struct
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
from . import pytmx
import importlib
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty
from .MapDataOperator import MapDataOperator

class TimerOperator(Operator):
    bl_idname = 'tiled_2_blender.timer_operator'
    bl_label = 'Timer Operator'

    map_data_path: StringProperty()
    layer_index: IntProperty()
    tile_index: IntProperty()
    x: IntProperty()
    y: IntProperty()
    gid: IntProperty()
    tiled_map = None
    layers = None
    cur_layer = None
    is_tile_layer = None


    def execute(self, context):
        tile = self.tiled_map.get_tile_image_by_gid(self.gid)
        if tile:
            image_name = os.path.basename(tile[0])
            image_width, image_height = get_image_size(tile[0])
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(self.x, -self.y, self.layer_index * 0.001))
            plane = bpy.context.active_object
            bpy.context.active_object
            me = plane.data
            if image_name in bpy.data.materials:
                mat = bpy.data.materials[image_name]
            else:
                mat = bpy.data.materials.new(name=image_name)
                mat.blend_method = 'BLEND'
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes['Principled BSDF']
                tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
                if image_name not in bpy.data.images:
                    bpy.ops.image.open(filepath=tile[0])
                tex.image = bpy.data.images[image_name]
                mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])
                mat.node_tree.links.new(bsdf.inputs['Alpha'], tex.outputs['Alpha'])
            if plane.data.materials:
                plane.data.materials[0] = mat
            else:
                plane.data.materials.append(mat)
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(me)
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.ensure_lookup_table()
            tile_x, tile_y, tile_width, tile_height = tile[1]
            bottom_left = ((tile_x / tile_width) / (image_width / tile_width), 1 - (tile_y / tile_height + 1) / (image_height / tile_height))
            bottom_right = ((tile_x / tile_width + 1) / (image_width / tile_width), 1 - (tile_y / tile_height + 1) / (image_height / tile_height))
            top_right = ((tile_x / tile_width + 1) / (image_width / tile_width), 1 - (tile_y / tile_height) / (image_height / tile_height))
            top_left = ((tile_x / tile_width) / (image_width / tile_width), 1 - (tile_y / tile_height) / (image_height / tile_height))
            flipped_horizontally, flipped_vertically, flipped_diagonally = tile[2]
            if flipped_diagonally:
                bottom_right, top_left = top_left, bottom_right
            if flipped_horizontally:
                bottom_left, bottom_right = bottom_right, bottom_left
                top_right, top_left = top_left, top_right
            if flipped_vertically:
                bottom_left, top_left = top_left, bottom_left
                bottom_right, top_right = top_right, bottom_right
            bm.faces[0].loops[0][uv_layer].uv = bottom_left
            bm.faces[0].loops[1][uv_layer].uv = bottom_right
            bm.faces[0].loops[2][uv_layer].uv = top_right
            bm.faces[0].loops[3][uv_layer].uv = top_left
            bmesh.update_edit_mesh(me)
            bpy.ops.object.mode_set(mode='OBJECT')
        return { 'FINISHED' }

    def modal(self, context, event):
        if self.layer_index < len(self.layers):
            self.cur_layer = self.layers[self.layer_index]
            if isinstance(self.cur_layer, pytmx.TiledTileLayer):
                self.cur_layer = list(self.cur_layer)
            else:
                self.tile_index = 0
                self.layer_index += 1
                return {'PASS_THROUGH'}
            if self.tile_index < len(self.cur_layer):
                self.x, self.y, self.gid, = self.cur_layer[self.tile_index]
                self.execute(context)
                self.tile_index += 1
            else:
                self.tile_index = 0
                self.layer_index += 1
        else:
            self.cancel(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def invoke(self, context, event):
        self.map_data_path = MapDataOperator.filepath
        self.tiled_map = pytmx.TiledMap(self.map_data_path)
        self.layers = list(self.tiled_map.visible_layers)
        self.cur_layer = self.layers[self.layer_index]
        self.is_tile_layer = isinstance(self.cur_layer, pytmx.TiledTileLayer)
        self.cur_layer = list(self.cur_layer)
        self.layer_index = 0
        self.tile_index = 0

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

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