import cv2
from pathlib import Path
from ici.evaluation.evaluator import Evaluator
import matplotlib.pyplot as plt

path = Path.cwd().parents[1]

if __name__ == "__main__":
    ground_truth = cv2.imread((path / 'Ramp' / "stitched_heights4.exr").as_posix(), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    ici = cv2.imread((path / 'Ramp' / "rampe_4lights_height.exr").as_posix(), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    evaluator = Evaluator(ici, ground_truth, 4.45, 5.0, 0.002)
    evaluator.generate_evaluation("eval4.json")
    #print(evaluator.calc_bad_pixel())
