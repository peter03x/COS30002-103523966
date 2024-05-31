'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by
    Clinton Woodward <cwoodward@swin.edu.au>
    James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''
from time import sleep
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from path import Path
import time


class Agent(object):
    DECELERATION_SPEEDS = {
        'slow': 0.9,  # Gradual deceleration
        'normal': 0.6,  # Moderate deceleration
        'fast': 0.2,  # Quick deceleration
    }

    # NOTE: Class Object (not *instance*) variables!
    def __init__(self, world=None, scale=30.0, mass=1.0, color='ORANGE', mode='patrol'):
        self.world = world
        self.mode = mode
        dir = radians(random() * 360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)
        self.force = Vector2D()
        self.accel = Vector2D()
        self.mass = mass

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
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = scale  # Adjusted to use the scale directly
        self.wander_radius = scale  # Same as above
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        self.max_speed = 20.0 * scale
        self.max_force = 400.0
        self.is_selected = False
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
        self.vehicle.x = self.pos.x + self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y + self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()

    def speed(self):
        return self.vel.length()

    # --------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return desired_vel - self.vel


class Hunter(Agent):
    def __init__(self, world=None, scale=10, mass=1.0, color='BLUE', mode='patrol'):
        super().__init__(world, scale, mass, color)
        self.mode = mode
        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 2.0
        self.max_ammo = 30
        self.ammo = 30
        self.FSM = FSM(self)
        self.projectiles = []

    def randomise_path(self):
        cx = self.world.cx  # width
        cy = self.world.cy  # height
        num_pts = 10
        looped = True
        margin = min(cx, cy) * (1 / 6)  # use this for padding in the next line ...
        self.path.create_random_path(num_pts, margin, margin, cx - margin, cy - margin,
                                     looped)  # you have to figure out the parameters

    def follow_path(self, move_mode):
        if self.path.is_finished():
            # Apply the Arrive behavior at the final point
            return self.arrive(self.path.current_pt(), 'slow')
        else:
            # Check if close enough to current waypoint to switch to the next
            if self.current_waypoint_distance() < self.waypoint_threshold:
                self.path.inc_current_pt()
            # Apply the Seek behavior to move to the current waypoint
            if move_mode == "seek":
                return self.seek(self.path.current_pt())
            elif move_mode == "arrive fast":
                return self.arrive(self.path.current_pt(), 'fast')
            elif move_mode == "arrive":
                return self.arrive(self.path.current_pt(), 'normal')
            else:
                return self.arrive(self.path.current_pt(), 'slow')

    def current_waypoint_distance(self):
        # This method calculates the distance to the current waypoint
        # Assuming self.pos is the position of the agent (you might need to adjust this based on your setup)
        return (self.path.current_pt() - self.pos).length()

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

    def calculate(self, delta):

        target_pos = Vector2D(self.world.target.x, self.world.target.y)

        accel = Vector2D()

        if self.mode == "patrol":
            accel = self.FSM.exec(target_pos)
        elif self.mode == "attack":
            accel = Vector2D()
            self.vel = Vector2D()
            self.FSM.exec(target_pos)

        self.accel = accel

        return accel

    def update(self, delta):
        self.accel = self.calculate(delta) / self.mass

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
        self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
        self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
        self.vehicle.rotation = -self.heading.angle_degrees()

        i = 0
        while i < len(self.projectiles):

            nearest_target = None
            nearest_target_distance = float('inf')
            for prey in self.world.preys:
                target_distance = (self.projectiles[i].pos - prey.pos).length()
                if target_distance < nearest_target_distance:
                    nearest_target = prey
                    nearest_target_distance = target_distance

            if nearest_target_distance < nearest_target.collision_range:
                nearest_target.health = max(0, nearest_target.health - 20)
                del self.projectiles[i]

            elif (self.projectiles[i].pos.x > self.world.cx or self.projectiles[i].pos.x < 0
                  or self.projectiles[i].pos.y > self.world.cy or self.projectiles[i].pos.y < 0):
                del self.projectiles[i]

            else:
                i += 1

class Projectile(Agent):
    def __init__(self, world=None, color='BLUE', x=0., y=0., accel=Vector2D()):
        super().__init__(world, 5., 1.0, color)
        self.accel = accel

        self.pos = Vector2D(x=x, y=y)

        self.vehicle = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=10.0,
            color=COLOUR_NAMES[color],
            batch=window.get_batch("main")
        )

    def calculate(self):
        raise ValueError("This should not be called.")

    def update(self, delta):
        # new velocity
        self.vel += self.accel * delta

        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()

        self.vehicle.x = self.pos.x
        self.vehicle.y = self.pos.y

class Prey(Agent):
    def __init__(self, world=None, scale=10.0, mass=1.0, color='ORANGE'):
        super().__init__(world, scale, mass, color)

        self.collision_range = 20

        self.max_health = 150
        self.health = self.max_health
        self.update_count = 0

    def calculate(self, delta):
        accel = self.wander(delta)

        self.accel = accel

        return accel

    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
        wander_target = self.wander_target
        # this behaviour is dependent on the update rate, so this line must
        # be included when using time independent framerate.
        jitter = self.wander_jitter * delta  # this time slice
        # first, add a small random vector to the target's position
        wander_target += Vector2D(uniform(-1, 1) * jitter, uniform(-1, 1) * jitter)
        # re-project this new vector back on to a unit circle
        wander_target.normalise()
        # increase the length of the vector to the same as the radius
        # of the wander circle
        wander_target *= self.wander_radius
        # move the target into a position wander_dist in front of the agent
        wander_dist_vector = Vector2D(self.wander_dist, 0)  # also used for rendering
        target = wander_target + Vector2D(self.wander_dist, 0)
        # set the position of the Agent’s debug circle to match the vectors we’ve created
        # project the target into world space
        world_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        # and steer towards it

        return self.seek(world_target)

    def update(self, delta):

        super().update(delta)
        if self.health <= 0.:
            self.collision_range = 0.
            self.vehicle.color = COLOUR_NAMES["INVISIBLE"]
            if self.update_count < 1:
                self.world.total_target_left -= 1
                self.world.target_destroyed += 1
                self.update_count += 1

class FSM(Agent):
    def __init__(self, hunter):
        self.hunter = hunter
        self.patrol_modes = ["seek", "arrive fast", "arrive", "arrive slowly"]
        self.attack_modes = ["single", "burst", "automatic", "reload"]
        self.mode_index = 0
        self.firing_interval = 0.2  # Delay between shots in seconds

    def fire_projectile(self, accel):
        self.hunter.projectiles.append(
            Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y,
                       accel.copy().normalise() * 1000.))
        self.hunter.ammo -= 1

    def burst_fire(self, accel, shots_left):
        if shots_left > 0 and self.hunter.ammo > 0:
            self.fire_projectile(accel)
            pyglet.clock.schedule_once(lambda dt: self.burst_fire(accel, shots_left - 1), self.firing_interval)

    def automatic_fire(self, accel):
        if self.hunter.ammo > 0:
            self.fire_projectile(accel)
            pyglet.clock.schedule_once(lambda dt: self.automatic_fire(accel), self.firing_interval)

    def reload_ammo(self):
        while self.hunter.ammo < self.hunter.max_ammo:
            self.hunter.ammo += 1


    def current_state(self):
        # Existing conditions
        self.mode = self.hunter.mode

        if self.mode == 'patrol':
            if self.hunter.world.target_destroyed % 4 == 0:
                self.mode_index = 0
            elif self.hunter.world.target_destroyed % 4 == 1:
                self.mode_index = 1
            elif self.hunter.world.target_destroyed % 4 == 2:
                self.mode_index = 2
            elif self.hunter.world.target_destroyed % 4 == 3:
                self.mode_index = 3
            return self.patrol_modes[self.mode_index]
        else:
            if self.hunter.world.total_target_left >= 7 and self.hunter.ammo > 0:
                self.mode_index = 0
            elif (self.hunter.world.total_target_left >= 3 and
                  self.hunter.world.total_target_left < 7) and self.hunter.ammo > 3:
                self.mode_index = 1
            elif self.hunter.world.total_target_left < 3 and self.hunter.ammo > 0:
                self.mode_index = 2
            else:
                self.mode_index = 3

            return self.attack_modes[self.mode_index]

    def exec(self, target_pos):
        self.mode = self.hunter.mode

        if self.mode == 'patrol':
            if self.hunter.world.target_destroyed % 4 == 0:
                self.mode_index = 0
            elif self.hunter.world.target_destroyed % 4 == 1:
                self.mode_index = 1
            elif self.hunter.world.target_destroyed % 4 == 2:
                self.mode_index = 2
            elif self.hunter.world.target_destroyed % 4 == 3:
                self.mode_index = 3
            return self.hunter.follow_path(self.patrol_modes[self.mode_index])
        else:
            if self.hunter.world.total_target_left >= 7 and self.hunter.ammo > 0:
                self.mode_index = 0
            elif (
                    self.hunter.world.total_target_left >= 3 and
                    self.hunter.world.total_target_left < 7) and self.hunter.ammo > 3:
                self.mode_index = 1
            elif self.hunter.world.total_target_left < 3 and self.hunter.ammo > 0:
                self.mode_index = 2
            else:
                self.mode_index = 3

            projectile_accel = target_pos - self.hunter.pos

            if len(self.hunter.projectiles) < 1:
                if self.current_state() == 'single':
                    self.fire_projectile(projectile_accel)

                elif self.current_state() == 'burst':
                    self.burst_fire(projectile_accel, 3)  # Fire 3 shots
                elif self.current_state() == 'automatic':
                    self.automatic_fire(projectile_accel)  # Simulate 3 seconds of firing
                elif self.current_state() == 'reload':
                    self.reload_ammo()
