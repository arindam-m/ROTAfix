'''
This program is free software; you can redistribute it and
or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see http://www.gnu.org/licenses
'''

# Inspired from this idea: https://youtu.be/NEUa1IA7NBQ

# <pep8-80 compliant>

bl_info = {
    "name": "ROTAfix",
    "description": (
    "Can do few quick needed fixes for your rotated object"
    ),
    "author": "Arindam Mondal",
    "version": (280, 7, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Edit Mode > Sidebar > Utilities",
    "category": "Object"
    }

import bpy
from math import pi
from bpy.types import (
                        PropertyGroup,
                        Operator,
                        Panel
                        )

from bpy.props import (
                        EnumProperty,
                        BoolProperty,
                        PointerProperty
                        )


def fix_alignment(context):

    auto_perspective_flag = False

    bcpi = bpy.context.preferences.inputs

    if bcpi.use_auto_perspective:
        bcpi.use_auto_perspective = False
        auto_perspective_flag = True

    init_perps_ortho = []

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if space.region_3d.is_perspective:
                        init_perps_ortho = 'PERPS'
                    else:
                        init_perps_ortho = 'ORTHO'

    main_obj = bpy.context.active_object
    main_obj_name = main_obj.name

    main_obLoc_X = main_obj.location[0]
    main_obLoc_Y = main_obj.location[1]
    main_obLoc_Z = main_obj.location[2]

    bcs = bpy.context.scene
    cursorLoc_X = bcs.cursor.location[0]
    cursorLoc_Y = bcs.cursor.location[1]
    cursorLoc_Z = bcs.cursor.location[2]
    bpy.ops.view3d.snap_cursor_to_selected()

    bpy.ops.object.mode_set()

    # bpy.ops.view3d.view_persportho()

    bpy.ops.object.empty_add(align = 'VIEW')
    init_view_mt = bpy.context.active_object
    # bpy.ops.view3d.view_lock_to_active()

    bpy.ops.object.select_all(action = 'DESELECT')
    main_obj.select_set(True)
    bpy.context.view_layer.objects.active = main_obj
    bpy.ops.object.mode_set(mode = 'EDIT')

    csf = context.scene.fix_align

    bpy.ops.view3d.view_axis(
        type = csf.view_side,
        align_active = True
    )

    if csf.rot_values_to == 'RETAIN':

        bpy.context.object.vertex_groups.new(name = 'to_align')
        bpy.ops.object.vertex_group_assign()

        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.mesh.primitive_plane_add()
        bpy.context.object.vertex_groups.new(name = 'temp_mesh')
        bpy.ops.object.vertex_group_assign()

        A = set(bpy.data.objects[:])
        bpy.ops.mesh.separate(type='SELECTED')
        B = set(bpy.data.objects[:])
        new_obj = A ^ B
        temp_obj_name = [ob.name for ob in new_obj]
        bcv = bpy.context.view_layer
        temp_mesh_ob = bcv.objects[temp_obj_name[0]]

        # bpy.context.object.vertex_groups.active_index -= 1

    bpy.ops.object.mode_set()

    bpy.ops.object.empty_add(align = 'VIEW')
    temp_empty = bpy.context.active_object

    if csf.rot_values_to == 'RESTORE':
        restoreRot_X = temp_empty.rotation_euler[0]
        restoreRot_Y = temp_empty.rotation_euler[1]
        restoreRot_Z = temp_empty.rotation_euler[2]

    bpy.ops.object.select_all(action = 'DESELECT')
    main_obj.select_set(True)
    temp_empty.select_set(True)
    bpy.context.view_layer.objects.active = temp_empty
    bpy.ops.object.parent_set()

    bpy.ops.object.select_all(action = 'DESELECT')
    temp_empty.select_set(True)
    bpy.ops.object.rotation_clear()

    if csf.rot_values_to != 'RESTORE':

        if csf.view_side == 'FRONT':
            bpy.ops.transform.rotate(
                value = pi,
                orient_axis = 'X',
            )

        elif csf.view_side == 'LEFT':
            bpy.ops.transform.rotate(
                value = pi,
                orient_axis = 'Y',
            )
            bpy.ops.transform.rotate(
                value = pi / 2,
                orient_axis = 'Z',
            )

        elif csf.view_side == 'RIGHT':
            bpy.ops.transform.rotate(
                value = pi / 2,
                orient_axis = 'Z',
            )

        elif csf.view_side == 'BOTTOM':
            bpy.ops.transform.rotate(
                value = pi,
                orient_axis = 'Z',
            )

    bpy.ops.object.select_all(action = 'DESELECT')
    main_obj.select_set(True)
    bpy.ops.object.parent_clear(type = 'CLEAR_KEEP_TRANSFORM')

    if csf.rot_values_to == 'RESTORE':
        clear_loc_flag = False
        if csf.clear_loc:
            clear_loc_flag = True
            csf.clear_loc = False

    # if csf.clear_loc:
    #     bpy.ops.object.location_clear()

    else:
        bpy.ops.view3d.snap_selected_to_cursor()

    bpy.ops.object.transform_apply(
        location = False,
        rotation = True,
        scale = False
    )

    if csf.rot_values_to == 'RESTORE':
        main_obj.rotation_euler[0] = restoreRot_X
        main_obj.rotation_euler[1] = restoreRot_Y
        main_obj.rotation_euler[2] = restoreRot_Z

    bpy.ops.object.select_all(action = 'DESELECT')
    temp_empty.select_set(True)
    bpy.ops.object.delete()

    if csf.rot_values_to == 'RETAIN':

        bpy.ops.object.select_all(action = 'DESELECT')
        temp_mesh_ob.select_set(True)
        main_obj.select_set(True)
        bpy.context.view_layer.objects.active = main_obj
        bpy.ops.view3d.snap_selected_to_active()
        bpy.context.view_layer.objects.active = temp_mesh_ob
        bpy.ops.object.join()
        bpy.context.object.name = main_obj_name
        bpy.context.object.data.name = main_obj_name
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all( action = 'DESELECT' )
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.vertex_group_remove()
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove()
        bpy.ops.object.mode_set()

        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    bpy.ops.object.select_all(action = 'DESELECT')
    init_view_mt.select_set(True)
    bpy.context.view_layer.objects.active = init_view_mt

    bpy.ops.view3d.view_axis(
        type = 'TOP',
        align_active = True
    )

    # bpy.ops.view3d.view_lock_clear()
    bpy.ops.object.delete()
    # bpy.ops.view3d.view_persportho()

    bpy.ops.object.select_all(action = 'DESELECT')

    if csf.rot_values_to == 'RETAIN':
        main_obj = temp_mesh_ob

    main_obj.select_set(True)
    bpy.context.view_layer.objects.active = main_obj

    main_obj.location[0] = main_obLoc_X
    main_obj.location[1] = main_obLoc_Y
    main_obj.location[2] = main_obLoc_Z

    if csf.clear_loc:
        bpy.ops.object.location_clear()
        bpy.ops.view3d.view_selected()

        # bpy.ops.view3d.view_axis(type = 'FRONT')

    bcs.cursor.location[0] = cursorLoc_X
    bcs.cursor.location[1] = cursorLoc_Y
    bcs.cursor.location[2] = cursorLoc_Z

    if csf.rot_values_to == 'RESTORE':
        if clear_loc_flag:
            csf.clear_loc = True

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if space.region_3d.is_perspective:
                        if init_perps_ortho == 'ORTHO':
                            bpy.ops.view3d.view_persportho()
                    else:
                        if init_perps_ortho == 'PERPS':
                            bpy.ops.view3d.view_persportho()

    csf = context.scene.fix_align
    bpy.ops.object.mode_set(mode = csf.mode_switch)

    if auto_perspective_flag:
        bcpi.use_auto_perspective = True


class GLOBAL_PG_props_settings(PropertyGroup):

    rot_values_to : EnumProperty(
        name = "- Rotational Values To -",
        description = "Values To",
        items = [(
        'NONE',
        "Uniform",
        "Rotional values will be applied during the alignment."
        ),
        (
        'RESTORE',
        "Retrieve",
        "Restore the rotational values, if it has been applied."
        ),
        (
        'RETAIN',
        "Preserve",
        "Retain rotational values even after making it aligned."
        )],
        default = 'NONE',
        options = {'HIDDEN'}
    )

    mode_switch : EnumProperty(
        name = "- Modes -",
        description = "Operation ends with this mode",
        items = [('OBJECT', "Object Mode", ""),
                ('EDIT', "Edit Mode", ""),
                ('SCULPT', "Sculpt Mode", "")],
        default = 'EDIT',
        options = {'HIDDEN'}
    )

    view_side : EnumProperty(
        name = "- View Axexs -",
        description = "Align Object on View Axis",
        items = [('TOP', "Top", ""),
                ('FRONT', "Front", ""),
                ('RIGHT', "Right", ""),
                ('LEFT', "Left", ""),
                ('BACK', "Back", ""),
                ('BOTTOM', "Bottom", "")],
        default = 'TOP',
        options = {'HIDDEN'}
    )

    clear_loc : BoolProperty(
        name = "Move to Global Origin:",
        description = (
        "Move the object to World Space Origin after the alignment"
        ),
        default = False,
        options = {'HIDDEN'}
    )


class OBJECT_OT_align_object_fix(Operator):
    '''Rotated object will be fixed within these defined parameters'''
    bl_idname = "object.fix_object_alignment"
    bl_label = "Lets ROTAfix!"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        fix_alignment(context)
        return {'FINISHED'}


class OBJECT_PT_align_object_fix(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Utilities"
    bl_label = "ROTAfix"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        layout.label(text = 'Rotational Values :')
        csf = context.scene.fix_align
        layout.prop(
            csf,
            "rot_values_to",
            text = ' ',
            expand = True
        )

        layout.use_property_split = True
        layout.prop(csf, "view_side", text = "Align View :")
        layout.prop(csf, "mode_switch", text = "Op Ends In :")

        # row = layout.row()
        # row.use_property_split = True
        # row.label(text = 'Op Ends In :')
        # row.use_property_split = False
        # sub = row.row()
        # sub.scale_x = 0.9
        # row.prop(csf, "mode_switch", text = "")

        # row = layout.row()
        layout.use_property_split = True
        layout.label(text = 'Main Operator :')
        box = layout.box()
        col = box.column()
        col.operator("object.fix_object_alignment")


class OBJECT_PT_align_object_fix_subpanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Additional Settings"
    bl_parent_id = "OBJECT_PT_align_object_fix"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        csf = context.scene.fix_align
        layout.prop(csf, "clear_loc",)


classes = (
    GLOBAL_PG_props_settings,
    OBJECT_OT_align_object_fix,
    OBJECT_PT_align_object_fix,
    OBJECT_PT_align_object_fix_subpanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.fix_align = PointerProperty(
        type = GLOBAL_PG_props_settings
    )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del(bpy.types.Scene.fix_align)

if __name__ == "__main__":
    register()
