from enum import Enum
import numpy as np
import cv2
import math

class FaceColor(Enum):
    WHITE = (255,255,255)
    GREEN = (0,255,0)
    RED = (255,0,0)
    BLUE = (0,0,255)
    ORANGE = (0, 165, 255)
    YELLOW = (0, 255, 255)

    def __str__(self):
        return self.name.capitalize()

    def rgb(self):
        return  self.value

    @classmethod
    def from_rgb(cls, rgb_color):
        min_distance = float('inf')
        closest_color = None

        for color in cls:
            bgr_color = (color.value[2], color.value[1], color.value[0]) # Because OpenCV sucks
            predefined_rgb = np.array(bgr_color, dtype=np.uint8)
            distance = np.linalg.norm(np.array(rgb_color, dtype=np.uint8) - predefined_rgb)
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color

            print(f"Input {rgb_color} -> FaceColor {color} -> {predefined_rgb} has distance {distance}")

        # Delta E method, it seems to suck:
        #    predefined_color_lab = rgb_to_lab(color.value)
        #    average_color_lab = rgb_to_lab(rgb_color)
        #    dE = delta_e_cie1976(average_color_lab, predefined_color_lab)
        #    if dE < min_distance:
        #        min_distance = dE
        #        closest_color = color
        
        return closest_color

    @staticmethod
    def _delta_e_lab(color1, color2):
        """
        Calculate the Delta E (perceptual color difference) between two LAB color values.
        """
        lab_color1 = cs.cspace_convert(color1, start={"name": "sRGB1"}, end={"name": "CIELab"})
        lab_color2 = cs.cspace_convert(color2, start={"name": "sRGB1"}, end={"name": "CIELab"})
        return cs.cspace_deltae(lab_color1, lab_color2, {"name": "CIELab"})
    

# Stuff that's supposed to work from colorspacious or colormath, but chatgpt is 3 years behind and I can't be arsed
def rgb_to_lab(rgb):
    # Convert RGB to LAB manually
    r, g, b = [x / 255.0 for x in rgb]
    r = gamma_correction(r)
    g = gamma_correction(g)
    b = gamma_correction(b)

    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    x = x * 100.0
    y = y * 100.0
    z = z * 100.0

    return (x, y, z)

def gamma_correction(value):
    if value <= 0.04045:
        value = value / 12.92
    else:
        value = math.pow((value + 0.055) / 1.055, 2.4)
    return value

def delta_e_cie1976(color1, color2):
    # Calculate Delta E manually in LAB space
    delta_l = color2[0] - color1[0]
    delta_a = color2[1] - color1[1]
    delta_b = color2[2] - color1[2]

    delta_e = math.sqrt(delta_l**2 + delta_a**2 + delta_b**2)
    return delta_e


