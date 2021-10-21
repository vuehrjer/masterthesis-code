import cv2
from pathlib import Path

import numpy as np


class ImageStitcher:
    class InvalidStitchingParameters(ValueError):
        pass

    def __init__(self, path, calibration):
        self._load_images_from_folder(Path(path))
        self.step_size = calibration["step_size"]
        self.skip = calibration["skip"]
        self.image_width = calibration["image_width"]
        self.image_height = calibration["image_height"]
        self.height_before_cropping = self.image_height + (calibration["frames"] - 1) * calibration["step_size"]
        self.height_after_cropping = calibration["step_size"] * (calibration["frames"] - 1)
        self.cropping_height = self.height_before_cropping - self.height_after_cropping
        self.cropping_width = self.image_width - calibration["width_after_cropping"]

    def _load_images_from_folder(self, path):
        images = []
        for filename in path.iterdir():
            if filename.suffix == ".exr":
                img = cv2.imread((path / filename).as_posix(), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                img = cv2.imread((path / filename).as_posix(), 1)
            if img is not None:
                images.append(img)
        self.images = images

    def _crop_image(self, image):

        cropped_image = image[
                        int(self.cropping_height / 2):image.shape[0] - int(self.cropping_height / 2),
                        (int(self.cropping_width / 2)):(image.shape[1] - int(self.cropping_width / 2))
                        ]
        return cropped_image

    def stitch_images(self, cropped=False):
        if self.step_size * self.skip >= self.images[0].shape[0]:
            raise self.InvalidStitchingParameters("Pixelshift or Skip to big for Image Size")
        selected_images = [self.images[i][0:(self.step_size * self.skip), :]
                           for i in range(1, len(self.images)) if i % self.skip == 0]
        if cropped:
            border = np.zeros_like(self.images[0])
            selected_images.append(border[0:(self.step_size * ((len(self.images) - 1) % self.skip))])
        images_reversed = list(reversed(selected_images))
        images_reversed.append(self.images[0])
        stitched_image = cv2.vconcat(images_reversed)
        cropped_stitched_image = self._crop_image(stitched_image)
        return cropped_stitched_image


class PointCloudGenerator:
    class InvalidInputImages(ValueError):
        pass

    def __init__(self, resolution, heights, albedo):
        self.resolution = resolution
        self.heights = heights
        self.albedo = albedo

    def generate_point_cloud(self):
        arr_xy = self._get_xy()
        arr_z = self._get_z() * (-1)
        albedo = self._flatten_to_array()
        arr = np.vstack((arr_xy, arr_z, albedo)).T
        #arr = self._crop_empty_data(arr)
        return self._normalize_to_origin(arr)

    def _get_xy(self):
        arr_x = np.repeat([self.resolution * i for i in range(self.heights.shape[0])], self.heights.shape[1])
        arr_y = np.tile([self.resolution * i for i in range(self.heights.shape[1])], self.heights.shape[0])
        arr_xy = np.vstack((arr_x, arr_y))
        return arr_xy

    def _get_z(self):
        if len(self.heights.shape) == 3:
            self.heights = cv2.cvtColor(self.heights, cv2.COLOR_BGR2GRAY)
        arr_z = [self.heights[i][j] for i in range(self.heights.shape[0]) for j in range(self.heights.shape[1])]
        return np.array(arr_z)

    def _flatten_to_array(self):
        if len(self.albedo.shape) == 2:
            albedo = self.albedo.ravel(order="C")
        elif len(self.albedo.shape) == 3 and self.albedo.shape[2] == 3:
            color = []
            for i in range(3):
                color.append(self.albedo[:, :, i].ravel(order="C"))
            albedo = np.vstack((color[0], color[1], color[2]))
        else:
            raise self.InvalidInputImages
        return albedo

    @staticmethod
    def _crop_empty_data(arr):
        arr = arr[arr[:, 2] != 0]
        return arr

    @staticmethod
    def _normalize_to_origin(arr):
        arr[:, 0] -= arr[0, 0]
        arr[:, 1] -= arr[0, 1]
        return arr
