"""
QuickWire 1.0.0

A lightweight viewport utility for Blender 5.2+ that toggles wireframe
visibility for one, several, or all visible geometry objects using
customizable keyboard shortcuts.

Original concept:
    Toggle Object Wire v0.1
    Meshlogic (2017)

Modernized and redesigned:
    Sir Doug Fir & ChatGPT (2026)

Keyboard Shortcuts
------------------
Backslash (\)          Toggle Active Object
Shift + \              Toggle Selected Objects
Ctrl + \               Toggle All Visible Objects

Design Philosophy
-----------------
QuickWire is intentionally keyboard-driven.

It does not add:
    - N-panel tabs
    - viewport panels
    - buttons
    - icons
    - interface clutter

Designed for fast topology inspection during:
    - modeling
    - rigging
    - character work
    - hard-surface workflows

QuickWire operates on geometry objects only.
Armatures and scene-control objects are intentionally excluded.
"""


bl_info = {
    "name": "QuickWire",
    "author": "Sir Doug Fir & ChatGPT",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "location": "3D View",
    "description": (
        "Toggle wireframe visibility for one, several, or all visible "
        "geometry objects using customizable keyboard shortcuts."
    ),
    "category": "3D View",
}


import bpy

from bpy.types import Operator, AddonPreferences
from bpy.props import BoolProperty


# ------------------------------------------------------------
# Geometry scope
#
# QuickWire affects geometry objects only.
#
# Included:
#   MESH
#   CURVE
#   SURFACE
#   FONT
#   META
#
# Excluded:
#   ARMATURE
#   CAMERA
#   LIGHT
#   EMPTY
# ------------------------------------------------------------

SUPPORTED_TYPES = {
    'MESH',
    'CURVE',
    'SURFACE',
    'FONT',
    'META',
}


def is_supported_object(obj):
    return obj and obj.type in SUPPORTED_TYPES


def get_preferences(context):
    addon = context.preferences.addons.get(__name__)

    if addon:
        return addon.preferences

    return None


def get_active_wire_state(context):

    obj = context.active_object

    if is_supported_object(obj):
        return obj.show_wire

    return False


def set_wire_state(objects, state, context):

    prefs = get_preferences(context)

    for obj in objects:

        if not is_supported_object(obj):
            continue

        obj.show_wire = state

        if prefs and prefs.toggle_all_edges:
            obj.show_all_edges = state


# ------------------------------------------------------------
# Operators
# ------------------------------------------------------------

class QUICKWIRE_OT_toggle_active(Operator):

    bl_idname = "quickwire.toggle_active"
    bl_label = "Toggle Active Object Wire"
    bl_description = (
        "Toggle wireframe visibility for the active geometry object"
    )

    def execute(self, context):

        obj = context.active_object

        if not is_supported_object(obj):
            return {'CANCELLED'}

        obj.show_wire = not obj.show_wire

        prefs = get_preferences(context)

        if prefs and prefs.toggle_all_edges:
            obj.show_all_edges = obj.show_wire

        return {'FINISHED'}


class QUICKWIRE_OT_toggle_selected(Operator):

    bl_idname = "quickwire.toggle_selected"
    bl_label = "Toggle Selected Objects Wire"
    bl_description = (
        "Toggle wireframe visibility for selected geometry objects"
    )

    def execute(self, context):

        objects = [
            obj for obj in context.selected_objects
            if is_supported_object(obj)
        ]

        if not objects:
            return {'CANCELLED'}

        state = not get_active_wire_state(context)

        set_wire_state(objects, state, context)

        return {'FINISHED'}


class QUICKWIRE_OT_toggle_visible(Operator):

    bl_idname = "quickwire.toggle_visible"
    bl_label = "Toggle Visible Objects Wire"
    bl_description = (
        "Toggle wireframe visibility for all visible geometry objects"
    )

    def execute(self, context):

        objects = [
            obj
            for obj in context.scene.objects
            if not obj.hide_get()
            and is_supported_object(obj)
        ]

        if not objects:
            return {'CANCELLED'}

        state = not get_active_wire_state(context)

        set_wire_state(objects, state, context)

        return {'FINISHED'}
    
# ------------------------------------------------------------
# Add-on Preferences
# ------------------------------------------------------------

class QUICKWIRE_Preferences(AddonPreferences):

    # For a single-file add-on, Blender expects __name__
    bl_idname = __name__

    toggle_all_edges: BoolProperty(
        name="Toggle All Edges with Wireframe",
        description=(
            "Also toggle Blender's All Edges display when "
            "wireframe visibility changes"
        ),
        default=True,
    )

    def draw(self, context):

        layout = self.layout

        layout.label(text="QuickWire Settings")

        layout.prop(
            self,
            "toggle_all_edges"
        )


# ------------------------------------------------------------
# Keyboard shortcuts
# ------------------------------------------------------------

addon_keymaps = []


def register_keymaps():

    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(
        name="3D View",
        space_type="VIEW_3D"
    )


    # Backslash (\)
    # Toggle active object

    kmi = km.keymap_items.new(
        "quickwire.toggle_active",
        type='BACK_SLASH',
        value='PRESS'
    )

    addon_keymaps.append((km, kmi))


    # Shift + Backslash (\)
    # Toggle selected objects

    kmi = km.keymap_items.new(
        "quickwire.toggle_selected",
        type='BACK_SLASH',
        value='PRESS',
        shift=True
    )

    addon_keymaps.append((km, kmi))


    # Ctrl + Backslash (\)
    # Toggle all visible objects

    kmi = km.keymap_items.new(
        "quickwire.toggle_visible",
        type='BACK_SLASH',
        value='PRESS',
        ctrl=True
    )

    addon_keymaps.append((km, kmi))


def unregister_keymaps():

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()


# ------------------------------------------------------------
# Registration
# ------------------------------------------------------------

classes = (

    QUICKWIRE_OT_toggle_active,
    QUICKWIRE_OT_toggle_selected,
    QUICKWIRE_OT_toggle_visible,

    QUICKWIRE_Preferences,

)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    register_keymaps()


def unregister():

    unregister_keymaps()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()