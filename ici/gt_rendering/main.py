import argparse
import os
from pathlib import Path
import bpy
import sys

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from ici.gt_rendering.blender_engine import BlenderEngine
from ici.gt_rendering.automated_rendering import AreaRenderer, LineRenderer

blender = BlenderEngine()
renderer_dict = {"area": AreaRenderer(Path(os.getcwd()), blender, dict(img_amount=50, displacement=0.1)),
                 "line": LineRenderer(Path(os.getcwd()), blender, dict(img_amount=5, displacement=0.0047619))}


class IllegalArgumentError(ValueError):
    pass


def get_renderer_from_argument(arg):
    if arg not in renderer_dict:
        raise IllegalArgumentError
    return renderer_dict[arg]


if __name__ == "__main__":
    renderer_from_filename = bpy.path.basename(bpy.context.blend_data.filepath).split("_")[-1].split(".")[0]
    renderer = renderer_dict[renderer_from_filename]
    renderer.cleanup()
    renderer.create_animation()
    renderer.render()
    renderer.move_output()
