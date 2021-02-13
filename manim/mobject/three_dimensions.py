"""Three-dimensional mobjects."""

__all__ = [
    "ThreeDVMobject",
    "ParametricSurface",
    "Sphere",
    "Cube",
    "Prism",
    "Cone",
    "Arrow3D",
    "Cylinder",
    "Line3D",
    "Torus",
]

from ..constants import *
from ..mobject.geometry import Square, Dot, Line
from ..mobject.mobject import *
from ..mobject.types.vectorized_mobject import VGroup
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.iterables import tuplify
from ..utils.space_ops import z_to_vector, normalize
from ..utils.color import *
from ..utils.space_ops import get_norm

##############


class ThreeDVMobject(VMobject):
    def __init__(self, shade_in_3d=True, **kwargs):
        super().__init__(shade_in_3d=shade_in_3d, **kwargs)


class ParametricSurface(VGroup):
    def __init__(
        self,
        func,
        u_min=0,
        u_max=1,
        v_min=0,
        v_max=1,
        resolution=32,
        surface_piece_config={},
        fill_color=BLUE_D,
        fill_opacity=1.0,
        checkerboard_colors=[BLUE_D, BLUE_E],
        stroke_color=LIGHT_GREY,
        stroke_width=0.5,
        should_make_jagged=False,
        pre_function_handle_to_anchor_scale_factor=0.00001,
        **kwargs
    ):
        VGroup.__init__(self, **kwargs)
        self.u_min = u_min
        self.u_max = u_max
        self.v_min = v_min
        self.v_max = v_max
        self.resolution = resolution
        self.surface_piece_config = surface_piece_config
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.checkerboard_colors = checkerboard_colors
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.should_make_jagged = should_make_jagged
        self.pre_function_handle_to_anchor_scale_factor = (
            pre_function_handle_to_anchor_scale_factor
        )
        self.func = func
        self.setup_in_uv_space()
        self.apply_function(lambda p: func(p[0], p[1]))
        if self.should_make_jagged:
            self.make_jagged()

    def get_u_values_and_v_values(self):
        res = tuplify(self.resolution)
        if len(res) == 1:
            u_res = v_res = res[0]
        else:
            u_res, v_res = res
        u_min = self.u_min
        u_max = self.u_max
        v_min = self.v_min
        v_max = self.v_max

        u_values = np.linspace(u_min, u_max, u_res + 1)
        v_values = np.linspace(v_min, v_max, v_res + 1)

        return u_values, v_values

    def setup_in_uv_space(self):
        u_values, v_values = self.get_u_values_and_v_values()
        faces = VGroup()
        for i in range(len(u_values) - 1):
            for j in range(len(v_values) - 1):
                u1, u2 = u_values[i : i + 2]
                v1, v2 = v_values[j : j + 2]
                face = ThreeDVMobject()
                face.set_points_as_corners(
                    [
                        [u1, v1, 0],
                        [u2, v1, 0],
                        [u2, v2, 0],
                        [u1, v2, 0],
                        [u1, v1, 0],
                    ]
                )
                faces.add(face)
                face.u_index = i
                face.v_index = j
                face.u1 = u1
                face.u2 = u2
                face.v1 = v1
                face.v2 = v2
        faces.set_fill(color=self.fill_color, opacity=self.fill_opacity)
        faces.set_stroke(
            color=self.stroke_color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
        )
        self.add(*faces)
        if self.checkerboard_colors:
            self.set_fill_by_checkerboard(*self.checkerboard_colors)

    def set_fill_by_checkerboard(self, *colors, opacity=None):
        n_colors = len(colors)
        for face in self:
            c_index = (face.u_index + face.v_index) % n_colors
            face.set_fill(colors[c_index], opacity=opacity)
        return self


# Specific shapes


class Sphere(ParametricSurface):
    def __init__(
        self,
        radius=1,
        resolution=(12, 24),
        u_min=0.001,
        u_max=PI - 0.001,
        v_min=0,
        v_max=TAU,
        **kwargs
    ):
        ParametricSurface.__init__(
            self,
            self.func,
            resolution=resolution,
            u_min=u_min,
            u_max=u_max,
            v_min=v_min,
            v_max=v_max,
            **kwargs
        )
        self.radius = radius
        self.scale(self.radius)

    def func(
        self, u, v
    ):  # FIXME: An attribute defined in manim.mobject.three_dimensions line 56 hides this method
        return np.array([np.cos(v) * np.sin(u), np.sin(v) * np.sin(u), np.cos(u)])


class Cube(VGroup):
    def __init__(
        self,
        side_length=2,
        fill_opacity=0.75,
        fill_color=BLUE,
        stroke_width=0,
        **kwargs
    ):
        self.side_length = side_length
        super().__init__(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs
        )

    def generate_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(
                side_length=self.side_length,
                shade_in_3d=True,
            )
            face.flip()
            face.shift(self.side_length * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))

            self.add(face)


class Prism(Cube):
    def __init__(self, dimensions=[3, 2, 1], **kwargs):
        self.dimensions = dimensions
        Cube.__init__(self, **kwargs)

    def generate_points(self):
        Cube.generate_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)


class Cone(ParametricSurface):
    def __init__(
        self,
        base_radius=1,
        height=1,
        direction=Z_AXIS,
        show_base=False,
        resolution=24,
        # v will stand for phi
        v_min=0,
        v_max=TAU,
        # u will stand for r
        u_min=0,
        # u_max is calculated as a property
        checkerboard_colors=False,
        **kwargs
    ):
        self.base_radius = base_radius
        self.height = height
        self.show_base = show_base
        self.direction = direction
        ParametricSurface.__init__(
            self,
            self.func,
            v_min=v_min,
            v_max=v_max,
            u_min=u_min,
            u_max=np.sqrt(base_radius ** 2 + height ** 2),
            checkerboard_colors=checkerboard_colors,
            **kwargs
        )
        # used for rotations
        self._current_theta = 0
        self._current_phi = 0

        if self.show_base:
            self.base_circle = Dot(
                point=self.height * IN,
                radius=self.base_radius,
                color=self.fill_color,
                fill_opacity=self.fill_opacity,
            )
            self.add(self.base_circle)

        self._rotate_to_direction()

    """
	A Cone can be defined using 2 parameters: its height, and its base radius.
	The polar angle, theta, can be calculated using arctan(base_radius / height)
	The spherical radius, r, can be calculated using the pythagorean theorem.
	.. code-block::
				   |\\
				   |_\\ <-- theta
		height --> |  \\
				   |   \\ <-- r
				   |    \\
				   |     \\
				   --------
				   base_radius
	"""
    # @property
    # def u_max(self):
    # 	return np.sqrt(self.base_radius ** 2 + self.height ** 2)

    @property
    def theta(self):
        return PI - np.arctan(self.base_radius / self.height)

    def func(self, u, v):
        """Function to convert from spherical coordinates to cartesian.
        Parameters
        ---------
        u : :class:`float`
                the radius
        v : :class:`float`
                the azimuthal angle
        """
        r = u
        phi = v
        theta = self.theta
        return np.array(
            [
                r * np.sin(theta) * np.cos(phi),
                r * np.sin(theta) * np.sin(phi),
                r * np.cos(theta),
            ]
        )

    def _rotate_to_direction(self):
        x, y, z = self.direction

        r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        theta = np.arccos(z / r)

        if x == 0:
            if y == 0:  # along the z axis
                phi = 0
            else:
                phi = np.arctan(np.inf)
                if y < 0:
                    phi += PI
        else:
            phi = np.arctan(y / x)
        if x < 0:
            phi += PI

        # this is a lazy implementation of rotations
        # This un-rotates the last rotation (which is stored im memory)
        # and then calculates a rotation against the z axis
        # A better way would be to get the angle between the current direction
        # and the new one (using the dot product for example) and rotate it about
        # a 3rd vector, normal to the previous two

        # undo old rotation (in reverse order)
        self.rotate(-self._current_phi, Z_AXIS, about_point=ORIGIN)
        self.rotate(-self._current_theta, Y_AXIS, about_point=ORIGIN)
        # do new rotation
        self.rotate(theta, Y_AXIS, about_point=ORIGIN)
        self.rotate(phi, Z_AXIS, about_point=ORIGIN)
        # store values
        self._current_theta = theta
        self._current_phi = phi

    def set_direction(self, direction):
        self.direction = direction
        self._rotate_to_direction()

    def get_direction(self):
        return self._current_theta, self._current_phi


class Cylinder(ParametricSurface):
    def __init__(
        self,
        resolution=24,
        radius=1,
        height=2,
        direction=Z_AXIS,
        center_point=ORIGIN,
        # v will is the azimuthal angle
        v_min=0,
        v_max=TAU,
        show_ends=True,
    ):
        self.height = height
        self.radius = radius
        ParametricSurface.__init__(
            self,
            self.func,
            resolution=resolution,
            u_min=-self.height / 2,
            u_max=self.height / 2,
            v_min=v_min,
            v_max=v_max,
        )
        if show_ends:
            self.add_bases()
        self.set_direction(direction)

    def func(self, u, v):
        """Function to convert from cylindrical coordinates to cartesian.
        Parameters
        ---------
        u : :class:`float`
                the height
        v : :class:`float`
                the azimuthal angle
        """
        height = u
        phi = v
        r = self.radius
        return np.array([r * np.cos(phi), r * np.sin(phi), height])

    def add_bases(self):
        self.base_top = Dot(
            point=self.u_max * IN,
            radius=self.radius,
            color=self.fill_color,
            fill_opacity=self.fill_opacity,
            shade_in_3d=True,
        )
        self.base_bottom = Dot(
            point=self.u_min * IN,
            radius=self.radius,
            color=self.fill_color,
            fill_opacity=self.fill_opacity,
            shade_in_3d=True,
        )
        self.add(self.base_top, self.base_bottom)

    def _rotate_to_direction(self):
        x, y, z = self.direction

        r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        theta = np.arccos(z / r)

        if x == 0:
            if y == 0:  # along the z axis
                phi = 0
            else:  # along the x axis
                phi = np.arctan(np.inf)
                if y < 0:
                    phi += PI
        else:
            phi = np.arctan(y / x)
        if x < 0:
            phi += PI

        self.rotate(theta, Y_AXIS, about_point=ORIGIN)
        self.rotate(phi, Z_AXIS, about_point=ORIGIN)

    def set_direction(self, direction):
        self.direction = direction
        self._rotate_to_direction()


class Line3D(Cylinder):
    def __init__(self, start=LEFT, end=RIGHT, width=0.02, color=None, **kwargs):
        self.set_start_and_end_attrs(start, end)
        super().__init__(
            height=get_norm(self.vect), radius=width, direction=self.direction, **kwargs
        )
        self.shift((self.start + self.end) / 2)
        if color != None:
            self.set_color(color)

    def set_start_and_end_attrs(self, start, end):
        # If either start or end are Mobjects, this
        # gives their centers
        rough_start = self.pointify(start)
        rough_end = self.pointify(end)
        self.vect = rough_end - rough_start
        self.length = get_norm(self.vect)
        self.direction = normalize(self.vect)
        # Now that we know the direction between them,
        # we can the appropriate boundary point from
        # start and end, if they're mobjects
        self.start = self.pointify(start, self.direction)
        self.end = self.pointify(end, -self.direction)

    def pointify(self, mob_or_point, direction=None):
        if isinstance(mob_or_point, Mobject):
            mob = mob_or_point
            if direction is None:
                return mob.get_center()
            else:
                return mob.get_boundary_point(direction)
        return np.array(mob_or_point)

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_direction(self):
        return self.direction


class Arrow3D(Line3D):
    def __init__(
        self, start=LEFT, end=RIGHT, height=0.5, base_radius=0.25, color=WHITE, **kwargs
    ):
        self.set_start_and_end_attrs(start, end)

        VGroup.__init__(self, **kwargs)

        self.length = get_norm(self.vect)
        self.line = Line3D(
            start, end - height * self.direction
        )  # end adjusted so that thet tip does not extend out of the cone
        self.line.set_color(color)

        self.cone = Cone(
            direction=self.direction, base_radius=base_radius, height=height, **kwargs
        )
        self.cone.shift(end)
        self.cone.set_color(color)
        self.add(self.line, self.cone)


class Torus(ParametricSurface):
    def __init__(
        self, R=3, r=1, u_min=0, u_max=TAU, v_min=0, v_max=TAU, resolution=24, **kwargs
    ):
        self.R = R
        self.r = r
        ParametricSurface.__init__(
            self,
            self.func,
            u_min=u_min,
            u_max=u_max,
            v_min=v_min,
            v_max=v_max,
            resolution=resolution,
            **kwargs
        )

    def func(self, u, v):
        P = np.array([np.cos(u), np.sin(u), 0])
        return (self.R - self.r * np.cos(v)) * P - np.sin(v) * OUT
