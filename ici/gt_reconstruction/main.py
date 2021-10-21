import os
from pathlib import Path
import cv2
import numpy as np

from ici.gt_reconstruction.generate_heightmap import ImageStitcher, PointCloudGenerator

path = Path.cwd().parents[1]

calibration = {
    "step_size": 21,
    "skip": 4,
    "frames": 50,
    "image_height": 960,
    "image_width": 960,
    "width_after_cropping": 766
}

if __name__ == "__main__":
    #height_stitcher = ImageStitcher(path / 'Stripes' / 'Area_stripes_2lights' / 'depth', calibration)
    #heightmap = height_stitcher.stitch_images(cropped=True)
    #cv2.imwrite((path / "stitched_stripes.exr").as_posix(), heightmap)
    #albedo_stitcher = ImageStitcher(path / 'Stripes' / 'Area_stripes_2lights'/ 'color', calibration)
    #albedo = albedo_stitcher.stitch_images(cropped=True)
    #cv2.imwrite((path / "stitched_stripes.png").as_posix(), albedo)
    heightmap = cv2.imread((path / "Plane" / "grid_height.exr").as_posix(), cv2.IMREAD_ANYDEPTH)
    albedo = cv2.imread((path / "stitched_perspective.png").as_posix(), 1)
    pc_generator = PointCloudGenerator(1/210, heightmap, albedo)
    pc = pc_generator.generate_point_cloud()
    np.savetxt(path / "points.csv", pc, delimiter=",")
