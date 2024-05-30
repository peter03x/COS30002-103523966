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

class Agent(object):

	def __init__(self, world=None, scale=30.0, mass=1.0, color='ORANGE', mode='wander'):
		# keep a reference to the world object
		self.world = world
		self.mode = mode
		# where am i and where am i going? random start pos
		dir = radians(random() * 360)
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.force = Vector2D()  # current steering force
		self.accel = Vector2D()  # current acceleration due to force
		self.mass = mass

		# data for drawing this agent
		self.color = color
		self.vehicle_shape = [
			Point2D(-10, 6),
			Point2D(10, 0),
			Point2D(-10, -6)
		]
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x + self.vehicle_shape[1].x, self.pos.y + self.vehicle_shape[1].y,
			self.pos.x + self.vehicle_shape[0].x, self.pos.y + self.vehicle_shape[0].y,
			self.pos.x + self.vehicle_shape[2].x, self.pos.y + self.vehicle_shape[2].y,
			color=COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

		### wander details
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
		# Force and speed limiting code
		self.max_speed = 20.0 * scale
		self.max_force = 500.0

		self.is_selected = False

		# debug draw info?
		self.show_info = False

		# limits?
		self.max_speed = 20.0 * scale
		self.max_force = 400.0
		## max_force ??

		# debug draw info?
		self.show_info = True

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
		return desired_vel - self.vel

	def flee(self, obstacle):
		from_target = self.pos - obstacle.pos

		desired_vel = from_target.normalise() * self.max_speed
		return desired_vel - self.vel

	def pursuit(self, evader):
		''' this behaviour predicts where an agent will be in time T and seeks
			towards that point to intercept it. '''
		## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
		return Vector2D()

class Hunter(Agent):
	def __init__(self, world=None, mass=1.0, color='BLUE'):
		super().__init__(world, 0, mass, color)
		self.mode = "rifle"
		self.projectile = None
		self.pos = Vector2D(self.world.cx / 2, 100.)
		self.heading = Vector2D(0., 1.)

	def projectile_speed(self):
		if self.mode == "rifle" :
			return 3.0
		elif self.mode == "hand gun":
			return 3.0
		elif self.mode == "rocket" :
			return 1.5
		elif self.mode == "hand grenade":
			return 1.

	def projectile_power(self):
		if self.mode == "hand gun":
			return 2
		elif self.mode == "rifle":
			return 3
		elif self.mode == "hand grenade":
			return 10
		elif self.mode == "rocket":
			return 20
	def inaccuracy_rate(self):
		if self.mode == "hand gun":
			return 1.5
		elif self.mode == "rifle":
			return 0
		elif self.mode == "hand grenade":
			return 1.7
		elif self.mode == "rocket":
			return 0

	def calculate(self, delta):

		accel = self.attack()

		self.accel = accel

		return accel

	def attack(self):
		colliding_time = 1. / self.projectile_speed()
		prey = self.world.prey
		return (2 * (prey.pos - self.pos) + 2 * colliding_time * (
					prey.vel - self.vel) + prey.accel * colliding_time * colliding_time) / (
					colliding_time * colliding_time)
	#The way to get acceleration of the projectile was figured out from a youtube video: https://www.youtube.com/watch?v=m9jNpzk71ow


	def shoot(self):
		if not self.projectile:
			self.projectile = Projectile(self.world, self.color, self.inaccuracy_rate(), self.pos.x, self.pos.y, self.attack())

	def update(self, delta):
		self.calculate(delta)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
		self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
		self.vehicle.rotation = -self.heading.angle_degrees()

		if self.projectile:
			self.projectile.update(delta)

			prey_to_projectile_distance = (self.world.prey.pos - self.projectile.pos).length()
			if prey_to_projectile_distance <= self.world.prey.collision_range:
				self.world.prey.health = max(0, self.world.prey.health - self.projectile_power())
				self.projectile = None

			elif self.projectile.pos.x > self.world.cx or self.projectile.pos.x < 0 or self.projectile.pos.y > self.world.cy or self.projectile.pos.y < 0:
				self.projectile = None


class Projectile(Agent):

	def __init__(self, world=None, color='BLUE', inaccuracy_rate=0.1, x=0., y=0., accel=Vector2D()):
		super().__init__(world, 5., 1.0, color)
		self.accel = accel
		self.inaccuracy_rate = inaccuracy_rate
		self.pos = Vector2D(x=x, y=y)

		self.vehicle = pyglet.shapes.Circle(
			x=self.pos.x, y=self.pos.y,
			radius=10.0,
			color=COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

	def calculate(self):
		raise ValueError("This should not be called.")

	def update(self, delta):
		# new velocity
		self.vel += self.accel * delta

		# Slightly rotate velocity if the mode is Hand gun or hand generade
		# To rotate the a vector(x, y) by an angle alpha to become new vector (x', y'), we have the formula:
		# x' = x * cos(alpha) - y * sin(alpha)
		# y' = x * sin(alpha) + y * cos(alpha)

		new_x_vel = self.vel.x * cos(self.inaccuracy_rate * delta) - self.vel.y * sin(
			self.inaccuracy_rate * delta)
		new_y_vel = self.vel.y * sin(self.inaccuracy_rate * delta) + self.vel.y * cos(
			self.inaccuracy_rate * delta)
		self.vel = Vector2D(new_x_vel, new_y_vel)

		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()

		self.vehicle.x = self.pos.x
		self.vehicle.y = self.pos.y

class Prey(Agent):
	def __init__(self, world=None, scale=40.0, mass=1.0, color='ORANGE'):
		super().__init__(world, scale, mass, color)

		self.collision_range = 20

		self.max_health = 150
		self.health = self.max_health

		self.destination = "First"

		self.first_destination_pos = Vector2D(x=500, y=450)
		self.second_destination_pos = Vector2D(x=200, y=450)

		self.pos = (self.first_destination_pos + self.second_destination_pos) / 2

		self.first_destination = pyglet.shapes.Star(
			self.first_destination_pos.x, self.first_destination_pos.y,
			20, 1, 5,
			color=COLOUR_NAMES['GREEN'],
			batch=window.get_batch("main")
		)

		self.second_destination = pyglet.shapes.Star(
			self.second_destination_pos.x, self.second_destination_pos.y,
			20, 1, 5,
			color=COLOUR_NAMES['YELLOW'],
			batch=window.get_batch("main")
		)

	def update_first_destination(self, x, y):

		distance = (self.second_destination_pos - Vector2D(x=x, y=y)).length()

		if distance >= 100:
			self.first_destination_pos.x = x
			self.first_destination_pos.y = y

			self.first_destination.x = x
			self.first_destination.y = y

	def update_second_destination(self, x, y):

		distance = (self.first_destination_pos - Vector2D(x=x, y=y)).length()

		if distance >= 100:
			self.second_destination_pos.x = x
			self.second_destination_pos.y = y

			self.second_destination.x = x
			self.second_destination.y = y

	def calculate(self, delta):

		distance_to_first_destination = (self.first_destination_pos - self.pos).length()
		distance_to_second_destination = (self.second_destination_pos - self.pos).length()

		accel = self.accel

		if self.destination == "First":
			accel = self.seek(self.first_destination_pos)
		elif self.destination == "Second":
			accel = self.seek(self.second_destination_pos)

		if distance_to_first_destination < self.collision_range:
			self.destination = "Second"

		elif distance_to_second_destination < self.collision_range:
			self.destination = "First"

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

	def update(self, delta):

		super().update(delta)




