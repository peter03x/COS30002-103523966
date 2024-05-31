'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent, AGENT_MODES  # Agent with seek, arrive, flee and pursuit


class World(object):

	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.target = Vector2D(cx / 2, cy / 2)
		self.selected_agent = 0
		self.agents = [Agent(self)]
		self.agents[0].is_selected = True
		self.paused = False
		self.show_info = True
		self.current_mode = "wander"

	def update(self, delta):
		if not self.paused:
			for agent in self.agents:
				agent.update(delta)

	def wrap_around(self, pos):
		''' Treat world as a toroidal space. Updates parameter object pos '''
		max_x, max_y = self.cx, self.cy
		if pos.x > max_x:
			pos.x = pos.x - max_x
		elif pos.x < 0:
			pos.x = max_x - pos.x
		if pos.y > max_y:
			pos.y = pos.y - max_y
		elif pos.y < 0:
			pos.y = max_y - pos.y
	
	def input_keyboard(self, symbol, modifiers):
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused

		elif symbol == pyglet.window.key.A:
			self.agents.append(Agent(self))

		elif symbol == pyglet.window.key.Z:
			self.current_mode = "wander"
			for agent in self.agents:
				agent.mode = "wander"

		elif symbol == pyglet.window.key.X:
			self.current_mode = "separation"
			for agent in self.agents:
				agent.mode = "separation"

		elif symbol == pyglet.window.key.C:
			self.current_mode = "cohesion"
			for agent in self.agents:
				agent.mode = "cohesion"

		elif symbol == pyglet.window.key.V:
			self.current_mode = "alignment"
			for agent in self.agents:
				agent.mode = "alignment"

	def transform_points(self, points, pos, 	forward, side, scale):
		''' Transform the given list of points, using the provided position,
			direction and scale, to object world space. '''
		# make a copy of original points (so we don't trash them)
		wld_pts = [pt.copy() for pt in points]
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# scale,
		mat.scale_update(scale.x, scale.y)
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform all the points (vertices)
		mat.transform_vector2d_list(wld_pts)
		# done
		return wld_pts

	def transform_point(self, point, pos, forward, side):
		''' Transform the given single point, using the provided position,
		and direction (forward and side unit vectors), to object world space. '''
		# make a copy of the original point (so we don't trash it)
		world_pt = point.copy()
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform the point (in place)
		mat.transform_vector2d(world_pt)
		# done
		return world_pt

	def update_selected_agent(self):
		for i in range(0, len(self.agents)):
			self.agents[i].is_selected = (i == self.selected_agent)