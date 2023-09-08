from modules.face.facecolors import FaceColor

class Face:
    def __init__(self, color):
        if color not in FaceColor.__members__.values():
            raise ValueError("Invalid face color")
        self.color = color
        self.grid = [[str(color) for _ in range(3)] for _ in range(3)]  # Initialize with provided color

    def rotate_clockwise(self):
        self.grid = [list(row) for row in zip(*reversed(self.grid))]  # Rotate the grid 90 degrees clockwise

    def rotate_counterclockwise(self):
        self.grid = [list(row) for row in reversed(list(zip(*self.grid)))]  # Rotate the grid 90 degrees counterclockwise

    def set_color(self, row, col, color):
        if 0 <= row < 3 and 0 <= col < 3 and color in FaceColor.__members__.values():
            self.grid[row][col] = color

    def get_color(self, row, col):
        if 0 <= row < 3 and 0 <= col < 3:
            return self.grid[row][col]

    def set_face_colors(self, colors):
        # Sanity: add check to make sure own color never changes
        if len(colors) == 3 and all(len(row) == 3 for row in colors):
            self.grid = colors

    def get_face_colors(self):
        return self.grid

    def __str__(self):
        return self.color

