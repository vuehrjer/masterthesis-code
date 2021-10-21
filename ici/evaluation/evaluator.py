import math

import cv2
import numpy as np
import json


class Evaluator:
    def __init__(self, ici, ground_truth, foreground, background, threshold):
        self.ground_truth = ground_truth
        self.ici = ici
        self._foreground = foreground
        self._background = background
        self._threshold = threshold

    def get_difference_map(self):
        diff = abs(self.ici - self.ground_truth)
        #diff = cv2.normalize(diff, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        cv2.imwrite("diff_map.exr", diff)

    def calc_rms(self):
        squared_differences = np.square(self.ground_truth - self.ici)
        error_sum = squared_differences.sum()
        return math.sqrt(error_sum / self.ground_truth.size) * 100

    def calc_bad_pixel(self):
        difference = abs(self.ici - self.ground_truth)
        bad_pixels = np.sum(difference > self._threshold)
        return bad_pixels / self.ground_truth.size * 100

    def calc_bumpiness(self):
        diff = self.ici - self.ground_truth
        hessian_matrix = np.zeros((len(diff) - 2, len(diff[0]) - 2, 4))
        for i in range(1, len(diff) - 1):
            for j in range(1, len(diff[0]) - 1):
                hessian_matrix[i - 1, j - 1, 0] = (diff[i + 1, j] - 2 * diff[i, j] + diff[i - 1, j])
                hessian_matrix[i - 1, j - 1, 1] = (diff[i, j + 1] - 2 * diff[i, j] + diff[i, j - 1])
                hessian_matrix[i - 1, j - 1, 2] = (diff[i + 1, j + 1] - diff[i - 1, j + 1] - diff[i + 1, j - 1] +
                                                   diff[i - 1, j - 1])
                hessian_matrix[i - 1, j - 1, 3] = hessian_matrix[i - 1, j - 1, 2]
        frobenius_norm_matrix = np.sqrt(np.square(hessian_matrix).sum(axis=2))
        # squared_derivatives = np.square(frobenius_norm_matrix)
        bumpiness = frobenius_norm_matrix.sum() / frobenius_norm_matrix.size
        return bumpiness * 100

    def calc_fg_fattening(self):
        ground_truth = np.copy(self.ground_truth)
        mask = ground_truth < (self._foreground + self._background) / 2
        ground_truth[mask] = None
        foreground = np.size(mask) - np.sum(mask)
        if foreground == 0:
            return 0
        else:
            fgf = 0
            for i, row in enumerate(ground_truth):
                for j, column in enumerate(row):
                    if not np.isnan(column):
                        value = self.ici[i, j]
                        if value < (self._foreground + self._background) / 2:
                            fgf += 1
            return fgf / foreground * 100

    def calc_fg_thinning(self):
        ground_truth = self.ground_truth.copy()
        mask = ground_truth > (self._foreground + self._background) / 2
        ground_truth[mask] = None
        background = np.size(mask) - np.sum(mask)
        if background == 0:
            return 0
        else:
            fgt = 0
            for i, row in enumerate(ground_truth):
                for j, column in enumerate(row):
                    if not np.isnan(column):
                        value = self.ici[i, j]
                        if value > (self._foreground + self._background) / 2:
                            fgt += 1
            return fgt / background * 100

    def generate_evaluation(self, filename):
        self.get_difference_map()
        eval_dict = {"RMS": self.calc_rms(), "Badpixel": self.calc_bad_pixel(), "Bumpiness": self.calc_bumpiness(),
                     "FG_Thinning": self.calc_fg_thinning(), "FG_Fatting": self.calc_fg_fattening()}
        with open(filename, "w") as write_file:
            json.dump(eval_dict, write_file, indent=4)
