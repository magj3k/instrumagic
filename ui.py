from kivy.graphics import Color, Line, Rectangle
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup

class Obj(InstructionGroup):
    def __init__(self, shape, color = (1.0, 1.0, 1.0), texture_path = ""):
        super(Obj, self).__init__()

        self.shape = shape
        self.color = Color(color[0], color[1], color[2])
        self.add(self.color)
        self.add(self.shape)

        # rectangles only
        self.texture_path = texture_path
        if isinstance(self.shape, Rectangle) and self.texture_path != "":
            self.shape.texture = Image(self.texture_path).texture

    def on_update(self, dt):
        self.remove(self.color)
        self.remove(self.shape)
        
        self.add(self.color)
        self.add(self.shape)

    def change_texture(self, new_texture_path):
        if isinstance(self.shape, Rectangle):
            if new_texture_path != self.texture_path:
                self.texture_path = new_texture_path
                if self.texture_path != "":
                    self.shape.texture = Image(self.texture_path).texture

class String(InstructionGroup):
    def __init__(self, start_pt, end_pt, color = (1.0, 1.0, 1.0), visual_dampening = 1.0, line_width = 2.0):
        super(String, self).__init__()

        self.start = (start_pt[0], start_pt[1])#start_pt
        self.end = (end_pt[0], end_pt[1])#end_pt
        self.middle = self.compute_middle()
        self.initial_middle = self.middle

        self.color = Color(color[0], color[1], color[2])
        self.line_width = line_width
        self.line = Line(bezier=[self.start[0], self.start[1], self.middle[0], self.middle[1], self.end[0], self.end[1]], width = self.line_width)
        self.add(self.color)
        self.add(self.line)

        self.visual_dampening = visual_dampening

    def compute_middle(self):
        return ( ((self.end[0] + self.start[0]) * 0.5), ((self.end[1] + self.start[1]) * 0.5) )

    def on_update(self, dt):
        self.remove(self.color)
        self.remove(self.line)

        self.add(self.color)
        self.line = Line(bezier=[self.start[0], self.start[1], self.middle[0], self.middle[1], self.end[0], self.end[1]], width = self.line_width)
        self.add(self.line)

class SolidLine(InstructionGroup):
    def __init__(self, start_pt, end_pt, color = (1.0, 1.0, 1.0), line_width = 2.0):
        super(SolidLine, self).__init__()

        self.start = (start_pt[0], start_pt[1])#start_pt
        self.end = (end_pt[0], end_pt[1])#end_pt

        self.color = Color(color[0], color[1], color[2])
        self.line_width = line_width
        self.line = Line(bezier=[self.start[0], self.start[1], self.end[0], self.end[1]], width = self.line_width)
        self.add(self.color)
        self.add(self.line)

    def on_update(self, dt):
        self.remove(self.color)
        self.remove(self.line)
        
        self.add(self.color)
        self.line = Line(bezier=[self.start[0], self.start[1], self.end[0], self.end[1]], width = self.line_width)
        self.add(self.line)
