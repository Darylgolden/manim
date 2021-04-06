from manim import *
from manim.opengl import *

class Test(Scene):
    def construct(self):
        circle = OpenGLCircle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        square = OpenGLSquare(fill_opacity=0, stroke_opacity=1, stroke_color=RED, stroke_width=5, draw_stroke_behind_fill=False)

        self.play(FadeIn(square))
        self.wait()