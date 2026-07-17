
import numpy as np

class RobustScaleIntensity:
    def __init__(self, dtype=np.float):
        self.dtype = dtype
    def __call__(self, img):
        med = np.median(img)
        iqr = np.percentile(img, 75) - np.percentile(img, 25)
        return (img - med) / iqr
