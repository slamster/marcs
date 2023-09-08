from modules.face.face import Face
from modules.face.facecolors import FaceColor

class RubiksCube:
    def __init__(self):
        self.faces = {
            FaceColor.WHITE: Face(FaceColor.WHITE),
            FaceColor.GREEN: Face(FaceColor.GREEN),
            FaceColor.RED: Face(FaceColor.RED),
            FaceColor.BLUE: Face(FaceColor.BLUE),
            FaceColor.ORANGE: Face(FaceColor.ORANGE),
            FaceColor.YELLOW: Face(FaceColor.YELLOW)
        }

    def rotate_face_clockwise(self, color):
        if color in self.faces:
            face = self.faces[color]
            face.rotate_clockwise()

    def rotate_face_counterclockwise(self, color):
        if color in self.faces:
            face = self.faces[color]
            face.rotate_counterclockwise()

    def display(self):
        for color, face in self.faces.items():
            print(f'{color} face:')
            for row in face.get_face_colors():
                print(' '.join(map(str, row)))
            print('\n')

    def set_face_colors(self, color, colors):
        if color in self.faces:
            face = self.faces[color]
            face.set_face_colors(colors)

    def get_face_colors(self, color):
        if color in self.faces:
            face = self.faces[color]
            return face.get_face_colors()
