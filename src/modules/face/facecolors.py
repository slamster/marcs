from enum import Enum

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

