from enum import Enum

class FaceColor(Enum):
    WHITE = 'White'
    GREEN = 'Green'
    RED = 'Red'
    BLUE = 'Blue'
    ORANGE = 'Orange'
    YELLOW = 'Yellow'

    def __str__(self):
        return self.value

