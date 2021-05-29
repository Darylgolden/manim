from manim import *
from manim.opengl import *

class Test(Scene):
    def construct(self):
        square = Square(fill_opacity=0, stroke_opacity=1)

        self.add(square)
        self.wait()