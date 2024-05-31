'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by 
	Clinton Woodward <cwoodward@swin.edu.au>
	James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path


PANIC_DISTANCE = 100

AGENT_MODES = {
	pyglet.window.key._1: 'seek',
	pyglet.window.key._2: 'arrive_slow',
	pyglet.window.key._3: 'arrive_normal',
	pyglet.window.key._4: 'arrive_fast',
	pyglet.window.key._5: 'flee',
	pyglet.window.key._6: 'pursuit',
	pyglet.window.key._7: 'follow_path',
	pyglet.window.key._8: 'wander',
}

class Agent(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
		'slow': 0.9,  # Gradual deceleration
		'normal': 0.6,  # Moderate deceleration
		'fast': 0.2,  # Quick deceleration
	}

	def __init__(self, world=None, scale=10.0, mass=1.0, color = 'ORANGE', mode='wander'):
		# keep a reference to the world object
		self.world = world
		self.mode = mode
		# where am i and where am i going? random start pos
		dir = radians(random()*360)
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.force = Vector2D()  # current steering force
		self.accel = Vector2D() # current acceleration due to force
		self.mass = mass

		# data for drawing this agent
		self.color = color
		self.vehicle_shape = [
			Point2D(-10,  6),
			Point2D( 10,  0),
			Point2D(-10, -6)
		]
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

		# wander info render objects
		self.info_wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
		self.info_wander_target = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
		# add some handy debug drawing info lines - force and velocity
		self.info_force_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['BLUE'], batch=window.get_batch("info"))
		self.info_vel_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['AQUA'], batch=window.get_batch("info"))
		self.info_net_vectors = [
			ArrowLine(
				Vector2D(0,0),
				Vector2D(0,0),
				colour=COLOUR_NAMES['GREY'],
				batch=window.get_batch("info")
			),
			ArrowLine(
				Vector2D(0,0),
				Vector2D(0,0),
				colour=COLOUR_NAMES['GREY'],
				batch=window.get_batch("info")
			),
		]

		### wander details
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
		# Force and speed limiting code
		self.max_speed = 20.0 * scale
		self.max_force = 500.0

		self.near_range = 100
		self.far_range = 200

		self.near_range_circle = pyglet.shapes.Arc(
			x=self.pos.x, y=self.pos.y,
			color=COLOUR_NAMES['INVISIBLE'],
			radius=self.near_range,
			batch=window.get_batch("main")
		)

		self.far_range_circle = pyglet.shapes.Arc(
			x=self.pos.x, y=self.pos.y,
			color=COLOUR_NAMES['INVISIBLE'],
			radius=self.far_range,
			batch=window.get_batch("main")
		)

		self.is_selected = False

		# debug draw info?
		self.show_info = False

		# limits?
		self.max_speed = 20.0 * scale
		## max_force ??

		# debug draw info?
		self.show_info = False

	def calculate(self, delta):
		# calculate the current steering force
		mode = self.mode

		if mode == 'wander':
			force = self.wander(delta)

		elif mode == 'separation':
			near_range_agents = self.get_near_range_agents()
			if len(near_range_agents) == 0:
				force = self.wander(delta)
			else:
				nearest_agent = min(near_range_agents, key=lambda x: x[1])[0]
				force = self.flee(nearest_agent)

		elif mode == 'cohesion':
			near_range_agents = self.get_near_range_agents()

			if len(near_range_agents) == 0:
				force = self.wander(delta)
			else:
				total_x_vector = self.pos.x
				total_y_vector = self.pos.y
				for agent, _ in near_range_agents:
					total_x_vector += agent.pos.x
					total_y_vector += agent.pos.y
				total_x_vector /= (len(near_range_agents) + 1)
				total_y_vector /= (len(near_range_agents) + 1)
				force = self.seek(Vector2D(x=total_x_vector, y=total_y_vector))

		elif mode == 'alignment':
			far_range_agents = self.get_far_range_agents()
			if len(far_range_agents) == 0:
				force = self.wander(delta)
			else:
				total_force = self.force
				for agent, _ in far_range_agents:
					total_force += agent.force
				force = total_force.normalise() * 100

		self.force = force

		return force

	def update(self, delta):
		''' update vehicle position and orientation '''
		# calculate and set self.force to be applied
		## force = self.calculate()
		force = self.calculate(delta)  # <-- delta needed for wander
		## limit force? <-- for wander
		# ...
		# determin the new acceleration
		self.accel = force / self.mass  # not needed if mass = 1.0
		accel = self.accel
		# new velocity
		self.vel += accel * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
		self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
		self.vehicle.rotation = -self.heading.angle_degrees()

		self.vehicle.color = COLOUR_NAMES[self.color]
	def speed(self):
		return self.vel.length()

	#--------------------------------------------------------------------------

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

	def flee(self, other_agent):
		from_target = self.pos - other_agent.pos

		desiredVel = from_target.normalise() * self.max_speed
		return (desiredVel - self.vel) * 20

	def wander(self, delta):
		''' random wandering using a projected jitter circle '''
		wander_target = self.wander_target
		# this behaviour is dependent on the update rate, so this line must
		# be included when using time independent framerate.
		jitter = self.wander_jitter * delta # this time slice
		# first, add a small random vector to the target's position
		wander_target += Vector2D(uniform(-1,1) * jitter, uniform(-1,1) * jitter)
		# re-project this new vector back on to a unit circle
		wander_target.normalise()
		# increase the length of the vector to the same as the radius
		# of the wander circle
		wander_target *= self.wander_radius
		# move the target into a position wander_dist in front of the agent
		wander_dist_vector = Vector2D(self.wander_dist, 0) #also used for rendering
		target = wander_target + Vector2D(self.wander_dist, 0)
		# set the position of the Agent’s debug circle to match the vectors we’ve created
		circle_pos = self.world.transform_point(wander_dist_vector, self.pos, self.heading, self.side,)
		self.info_wander_circle.x = circle_pos.x
		self.info_wander_circle.y = circle_pos.y
		self.info_wander_circle.radius = self.wander_radius
		# project the target into world space
		world_target = self.world.transform_point(target, self.pos, self.heading, self.side)
		#set the target debug circle position
		self.info_wander_target.x = world_target.x
		self.info_wander_target.y = world_target.y
		# and steer towards it

		return self.seek(world_target)

	def get_near_range_agents(self):
		result = []

		for agent in self.world.agents:
			agent_vector = agent.pos - self.pos
			distance = agent_vector.length()
			if distance <= self.near_range and agent != self:
				result.append((agent, distance))

		return result

	def get_far_range_agents(self):
		result = []

		for agent in self.world.agents:
			agent_vector = agent.pos - self.pos
			distance = agent_vector.length()
			if distance <= self.far_range and agent != self:
				result.append((agent, distance))

		return result

	def pursuit(self, evader):
		''' this behaviour predicts where an agent will be in time T and seeks
			towards that point to intercept it. '''
		## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
		return Vector2D()
