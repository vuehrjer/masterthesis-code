from ici.gt_rendering.automated_rendering import RenderEngine, Point
import bpy


class BlenderEngine(RenderEngine):
    def __init__(self):
        self._planes = bpy.data.collections["Test_Objects"].all_objects
        #self._plane = bpy.context.scene.objects.get("Plane")
        self._num_frames = 0

    @property
    def num_frames(self):
        return self._num_frames

    def get_start_point(self):
        return [Point(plane.location[0], plane.location[1], plane.location[2]) for plane in self._planes]

    def set_animation(self, animations):
        self._num_frames = len(animations[0])
        for plane_number, animation in enumerate(animations):
            for frame, pos in enumerate(animation):
                bpy.context.scene.frame_set(frame)
                self._planes[plane_number].location = [pos.x, pos.y, pos.z]
                self._planes[plane_number].keyframe_insert(data_path="location", frame=frame)

    def get_collections(self):
        return bpy.data.collections

    def render_frame(self, frame, out_file):
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = out_file.as_posix()
        bpy.ops.render.render(animation=False, write_still=True)





