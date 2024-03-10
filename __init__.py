import bpy

bl_info = {
    "name": "Origin to Average Location",
    "author": "Erlandas Barauskas (Hayato)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Context Menu -> Origin to middle of selected (Vertices/Edges/Faces)",
    "description": "This will add option in edit mode, to move object origin to selected vertices/edges/faces middle position",
    "category": "3D View",
}


# noinspection PyPep8Naming
class OriginToAverageLocation_OT_MoveOriginToAverageLocation(bpy.types.Operator):
    bl_label = "Origin to middle of selected (Vertices/Edges/Faces)"
    bl_idname = "object.origin_to_average_location"
    bl_description = "Will set object origin to selected middle of vertices/edges/faces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        import numpy as np
        import mathutils

        mode = context.active_object.mode
        # we need to switch from Edit mode to Object mode so the selection gets updated
        bpy.ops.object.mode_set(mode='OBJECT')

        cached_cursor_location = context.scene.cursor.location.copy()

        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            obj_data: bpy.types.Mesh = obj.data

            selected_vertices: np.array = np.array([])
            selected_vertices.shape = (0, 3)

            for vertex in obj_data.vertices:
                if vertex.select:
                    vertex_location = obj.matrix_world @ vertex.co
                    selected_vertices = np.append(selected_vertices, [[vertex_location[0], vertex_location[1], vertex_location[2]]], axis=0)

            if len(selected_vertices) == 0:
                continue

            context.scene.cursor.location = mathutils.Vector((selected_vertices.mean(axis=0)))

            with context.temp_override(selected_editable_objects=[obj]):
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        context.scene.cursor.location = cached_cursor_location

        # back to whatever mode we were in
        bpy.ops.object.mode_set(mode=mode)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(OriginToAverageLocation_OT_MoveOriginToAverageLocation.bl_idname)


addon_keymaps = []


def register():
    bpy.utils.register_class(OriginToAverageLocation_OT_MoveOriginToAverageLocation)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)

    # Add the hotkey
    window_manager = bpy.context.window_manager
    key_configs = window_manager.keyconfigs.addon
    if key_configs:
        new_key_map = window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        new_key_map_item = new_key_map.keymap_items.new(OriginToAverageLocation_OT_MoveOriginToAverageLocation.bl_idname, type='NONE', value='PRESS')
        addon_keymaps.append((new_key_map, new_key_map_item))


def unregister():
    bpy.utils.unregister_class(OriginToAverageLocation_OT_MoveOriginToAverageLocation)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)
    pass
