from manim import *

class MovingVertices(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        vertices = [1, 2, 3, 4]
        edges = [(1, 2), (2, 3), (3, 4), (1, 3), (1, 4)]
        g = Graph(vertices, edges)
        self.play(Create(g))
        self.wait()
        self.play(g[1].animate.move_to([1, 1, 1]),
                  g[2].animate.move_to([-1, 1, 2]),
                  g[3].animate.move_to([1, -1, -1]),
                  g[4].animate.move_to([-1, -1, 0]))
        self.wait()