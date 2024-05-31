import pyglet

from random import randrange

from vector2d import Vector2D
from graphics import COLOUR_NAMES, window
from world import World


class Obstacle(object):

    def __init__(self, world=None, x=100., y=100., radius=30.0):
        self.world = world
        self.pos = Vector2D(x, y)
        self.radius = radius

        self.circle = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=self.radius,
            color=COLOUR_NAMES['LIGHT_GREEN'],
            batch=window.get_batch("main")
        )

        self.target = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=7.0,
            color=COLOUR_NAMES['INVISIBLE'],
            batch=window.get_batch("main")
        )

        self.circle_emphasise = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=self.radius,
            color=COLOUR_NAMES['INVISIBLE'],
            batch=window.get_batch("main")
        )

    def is_safe(self):
        hunter = self.world.hunter
        safe_distance = 150 + self.radius * 2
        distance = (self.pos - hunter.pos).length()
        is_safe = distance < safe_distance

        if is_safe:
            self.circle.color = COLOUR_NAMES['RED']

        else:
            self.circle.color = COLOUR_NAMES['AQUA']

        return is_safe

    def update(self, delta):
        self.is_safe()

    def reset(self, world):
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))