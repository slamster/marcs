from enum import Enum
import numpy as np
import cv2
import math
from skimage.color import rgb2lab, deltaE_ciede2000

class FaceColor(Enum):
    WHITE = (255,255,255)
    GREEN = (0,255,0)
    RED = (255,38,38)
    BLUE = (0,0,255)
    ORANGE = (255, 128, 0)
    YELLOW = (255, 255, 0)

    def __str__(self):
        return self.name.capitalize()

    def rgb(self):
        return  self.value

    @classmethod
    def from_rgb(cls, input_color):
        min_distance = float('inf')

        #input_color = (rgb_color[2], rgb_color[1], rgb_color[0])
        closest_color = None

        for color in cls:
            rgb_color = (color.value[0], color.value[1], color.value[2]) # Because OpenCV sucks
            predefined_rgb = np.array(rgb_color, dtype=np.int16)
            np_input_color = np.array(input_color, dtype=np.int16)
            np_diff = np.array(input_color, dtype=np.int16) - predefined_rgb
            distance = np.linalg.norm(np.array(input_color, dtype=np.int16) - predefined_rgb)
            print(f"Input {input_color} -> {np_input_color} -> FaceColor {color}: {predefined_rgb} has diff {np_diff} => distance {distance}")
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color

        return closest_color

    @classmethod
    def from_rgb2(cls, input_color):
        min_distance = float('inf')
        closest_color = None

        for color in cls:
            rgb_color = (color.value[0], color.value[1], color.value[2])
            predefined_rgb = np.array(rgb_color, dtype=np.int16)
            np_input_color = np.array(input_color, dtype=np.int16)

            lab_predefined = rgb2lab(predefined_rgb)
            lab_input = rgb2lab(np_input_color)

            distance = deltaE_ciede2000(lab_predefined, lab_input)
            print(f"Input {input_color} -> {np_input_color} -> FaceColor {color}: => {lab_input} vs {lab_predefined} has delta E {distance}")
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color

        return closest_color
