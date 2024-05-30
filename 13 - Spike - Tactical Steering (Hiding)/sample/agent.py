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
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform

PANIC_DISTANCE = 100



class Agent(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
		'slow': 0.9,  # Gradual deceleration
		'normal': 0.6,  # Moderate deceleration
		'fast': 0.2,  # Quick deceleration
	}

	def __init__(self, world=None, scale=30.0, mass=1.0, color='ORANGE'):
		# keep a reference to the world object
		self.world = world
		dir = radians(random() * 360)
		# where am i and where am i going? random start pos
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
		self.color = color
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size

		self.accel = Vector2D() # current acceleration due to force
		self.mass = mass
		self.max_speed = scale * 10

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

	def calculate(self, delta):
		raise NotImplementedError("This method should be overridden.")
	def update(self, delta):
		''' update vehicle position and orientation '''
		# calculate and set self.force to be applied
		## force = self.calculate()
		force = self.calculate(delta)  # <-- delta needed for wander
		## limit force? <-- for wander
		# ...
		# determine the new acceleration
		self.accel = force / self.mass  # not needed if mass = 1.0
		# new velocity
		self.vel += self.accel * delta
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

	def speed(self):
		return self.vel.length()

	#--------------------------------------------------------------------------

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

	def nearby_obstacle(self):
		for obstacle in self.world.obstacles:
			if self.is_near_obstacle(obstacle):
				return obstacle

		return None

	def is_near_obstacle(self, obstacle):
		from_target = self.pos - obstacle.pos
		distance = from_target.length()
		alert_distance = obstacle.radius + 20.0

		return distance < alert_distance

	def flee(self, obstacle):
		from_target = self.pos - obstacle.pos

		desiredVel = from_target.normalise() * self.max_speed
		return (desiredVel - self.vel)

	def arrive(self, target_pos, speed):
		''' this behaviour is similar to seek() but it attempts to arrive at
			the target position with a zero velocity'''
		decel_rate = self.DECELERATION_SPEEDS[speed]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)



	def pursuit(self, evader):
		''' this behaviour predicts where an agent will be in time T and seeks
			towards that point to intercept it. '''
		## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
		return Vector2D()

class Hunter(Agent):
	def __init__(self, world=None, scale=20.0, mass=5.0, color='BLUE'):

		super().__init__(world, scale, mass, color)
		self.color = color
		self.mode = "wander"
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

	def calculate(self, delta):
		self.mode = "wander"
		accel = self.wander(delta)

		nearby_obstacle = self.nearby_obstacle()
		# Flee the near obstacle
		nearby_obstacle = self.nearby_obstacle()

		if nearby_obstacle:
			accel = self.flee(nearby_obstacle)

		self.accel = accel

		return accel or Vector2D(0, 0)  # Ensure a Vector2D is returned even if all fails

	def target_distance(self):
		target = self.world.prey

		target_distance = (self.pos - target.pos).length()

		return target_distance

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

class Prey(Agent):
	def __init__(self, world=None, scale=30.0, mass=1.0, color='ORANGE'):
		super().__init__(world, scale, mass, color)
		self.mode = "idle"

	def calculate(self, delta):
		if not self.is_alerted():
			self.mode = "idle"
			target_pos = self.pos

		else:
			self.mode = "hide"
			best_obstacle = self.best_obstacle_to_go()

			to_best_obstacle_pos = best_obstacle.pos - self.pos
			to_behind_best_obstacle_pos = to_best_obstacle_pos.copy().normalise() * (sqrt(to_best_obstacle_pos.copy().x * to_best_obstacle_pos.copy().x + to_best_obstacle_pos.copy().y * to_best_obstacle_pos.copy().y) + 10.0 + best_obstacle.radius)

			behind_best_obstacle_pos = to_behind_best_obstacle_pos + self.pos
			target_pos = behind_best_obstacle_pos

			for obstacle in self.world.obstacles:
				obstacle.target.color = COLOUR_NAMES['INVISIBLE']
				obstacle.circle_emphasize.color = COLOUR_NAMES['INVISIBLE']

			best_obstacle.color = COLOUR_NAMES[self.color]
			best_obstacle.target.color = COLOUR_NAMES[self.color]
			best_obstacle.circle_emphasize.color = COLOUR_NAMES[self.color]
			best_obstacle.target.x = behind_best_obstacle_pos.x
			best_obstacle.target.y = behind_best_obstacle_pos.y

		accel = self.seek(target_pos)

		# Flee the near obstacle
		nearby_obstacle = self.nearby_obstacle()

		if nearby_obstacle:
			accel = self.flee(nearby_obstacle)

		self.accel = accel

		return accel

	def best_obstacle_to_go(self):
		max_distance = float("-inf")
		nearest_obstacle = self.world.obstacles[0]
		for obstacle in self.world.obstacles:

			if obstacle.is_safe():

				from_target = self.world.hunter.pos - obstacle.pos
				distance = from_target.length()

				if distance > max_distance:
					max_distance = distance
					nearest_obstacle = obstacle

		return nearest_obstacle
	def is_alerted(self):
		hunter = self.world.hunter
		alert_distance = 150
		hunter_distance = (self.pos - hunter.pos).length()
		return hunter_distance < alert_distance



