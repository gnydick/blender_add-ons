from bpy import ops as O
from bpy import props as P
from bpy import types as T
from bpy import utils as U

bl_info = {
    'name': 'Sushi Slicer',
    'author': 'Gabe E. Nydick',
    'version': (0, 4, 1),
    'blender': (2, 91, 0),
    'location': 'F3: "sushi.."',
    'category': 'Object',
    'description': '''Creates SLABS amount of equal
                    height layers from an object.
                    CUT for cutting the mesh.
                    SEP for creating seperate objects.'''
}


# Bounding box vertices
# Front  Left    Bottom
# Back   Right   Top

# 0 - FLB
# 1 - FLT
# 2 - BLT
# 3 - BLB
# 4 - FRB
# 5 - FRT
# 6 - BRT
# 7 - BRB


def setup(C, props):
    if 'initialized' in props:
        pass
    props['initialized'] = {'INIT'}
    ao = C.active_object
    props['actObj'] = ao
    props['bottom'] = ao.bound_box[0][2] + ao.location.z
    props['top'] = ao.bound_box[1][2] + ao.location.z
    props['height'] = ao.bound_box[1][2] - ao.bound_box[0][2]
    props['slice_height'] = props['height'] / props['slabs']
    props['initialized'] = {'FINISHED'}


def high_plane_co(idx, C, properties):
    return (0, 0, properties['bottom'] + idx * properties['slice_height'] \
            + properties['slice_height'])


def low_plane_co(idx, C, properties):
    return 0, 0, properties['bottom'] + idx * properties['slice_height']


def cut_callback():
    O.object.mode_set(mode='OBJECT', toggle=False)


def cut(idx, C, properties):
    O.mesh.select_all(action='SELECT')
    O.mesh.bisect(plane_co=high_plane_co(idx, C, properties), plane_no=(0, 0, 1), use_fill=False)


def sep(idx, C, properties):
    O.mesh.bisect(plane_co=low_plane_co(idx, C, properties), plane_no=(0, 0, 1), use_fill=True, clear_inner=True)
    O.mesh.select_linked()
    O.mesh.duplicate()

    O.mesh.bisect(plane_co=high_plane_co(idx, C, properties), plane_no=(0, 0, 1), use_fill=True, clear_outer=True)
    O.mesh.select_linked()
    if idx < properties['slabs'] - 1:
        O.mesh.separate(type='SELECTED')
    O.mesh.select_all(action='INVERT')


def sep_callback():
    O.object.mode_set(mode='OBJECT', toggle=False)
    O.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')


def loop(C, properties):
    O.object.mode_set(mode='EDIT', toggle=False)
    O.mesh.select_all(action='SELECT')
    if properties['slice_type'] == 'CUT':
        for idx in range(0, properties['slabs'] - 1):
            cut(idx, C, properties)
        cut_callback()
    if properties['slice_type'] == 'SEP':
        for idx in range(0, properties['slabs']):
            sep(idx, C, properties)
        sep_callback()


def main(context, properties):
    setup(context, properties)
    loop(context, properties)


class SushiObjectOperator(T.Operator):
    bl_idname = "object.sushi_object_operator"
    bl_label = "Sushi Object Operator"

    slice_type: P.EnumProperty(items=[('CUT', 'Cut', ''), ('SEP', 'Separate', '')], name="Slice Type")
    slabs: P.IntProperty(name="Number of slabs")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        properties = dict(
            slabs=self.slabs,
            slice_type=self.slice_type)
        main(context, properties)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


def register():
    U.register_class(SushiObjectOperator)


def unregister():
    U.unregister_class(SushiObjectOperator)


if __name__ == "__main__":
    register()
