game = None

from enum import Enum
import pyglet
from world import World
from graphics import window
from agent import Agent  # Agent with seek, arrive, flee and pursuit
from obstacle import Obstacle

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])
		#add obstacles
		self.world.obstacles = [
			Obstacle(self.world),
			Obstacle(self.world, x=430., y=120., radius=20.),
			Obstacle(self.world, x=500., y=450., radius=20.),
			Obstacle(self.world, x=210., y=590., radius=30.),
			Obstacle(self.world, x=760., y=870., radius=40.)]

		# unpause the world ready for movement
		self.world.paused = False

	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)