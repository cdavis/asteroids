
import logging
import math
from random import random, randint
import time

import pyglet
import pymunk

from objects import GameObject
import resources

KEY = pyglet.window.key
Vec2d = pymunk.Vec2d


class Asteroid(GameObject):
  image = resources.asteroid_image
  collides_with = ['Bullet', 'Player']

  def create_body(self, mass=1, radius=25, **unused):
    self.circle_body(mass, radius)

  #@staticmethod
  #def collision_Bullet_begin(arbiter, space, data):
  #  #print(f'Asteroid.collision_Bullet_begin()  arbiter={arbiter} space={space} data={data}')
  #  return True

  #@staticmethod
  #def collision_Player_begin(arbiter, space, data):
  #  #print(f'xAsteroid.collision_Player_begin()  arbiter={arbiter} space={space} data={data}')
  #  return True


class Bullet(GameObject):
  image = resources.bullet_image
  collides_with = ['Asteroid']

  def create_body(self, mass=1.0, radius=4, **unused):
    self.circle_body(mass, radius)



class Player(GameObject):
  image = resources.player_image
  collides_with = ['Asteroid']

  def create_body(self, mass=1.0, radius=25, **unused):
    #self.circle_body(mass, radius)
    self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    self.body.position = (self.x, self.y)
    self.shapes = {
        'body': pymunk.Circle(self.body, radius),
    }

    # Child sprite for the engine flame
    self.engine = pyglet.sprite.Sprite(resources.engine_image)
    self.engine.visible = False
    # XXX pyglet has to know to draw it, in the batch, etc. pymunk dont care. i dont care.
    # XXX Ah yes this is physics.objects not space.bodies... that is where the sprite drawing loop draws from (so maybe
    # I need to have it also look at obj.children ?

    # Movement settings
    self.thrust = 400.0
    self.rotate_speed = 3.0
    self.bullet_speed = 500.0
    self.bullet_delay = 0.1
    self.brake_damping = 0.03
    self.min_velocity = 50.0
    self.max_velocity = 600.0
    self.last_fired = 0.0

  def update(self, dt):
    if self.keys[KEY.LEFT]:
      self.body.angle += self.rotate_speed * dt

    elif self.keys[KEY.RIGHT]:
      self.body.angle -= self.rotate_speed * dt

    elif self.keys[KEY.UP]:
      self.engine.visible = True
      direction = pymunk.Vec2d(-math.cos(self.body.angle), -math.sin(self.body.angle))
      #direction /= direction.length
      self.body.velocity += direction * self.thrust * dt

    elif self.keys[KEY.DOWN]:
      self.body.velocity *= 1 - self.brake_damping
      if self.body.velocity.length < self.min_velocity:
        self.body.velocity = pymunk.Vec2d(0, 0)

    if not self.keys[KEY.UP]:
      self.engine.visible = False

    if self.keys[KEY.SPACE]:
      self.fire()

  def fire(self):
    now = time.time()
    if now - self.last_fired > self.bullet_delay:
      # Pyglet uses negative degrees
      angle_radians = -math.radians(self.rotation)

      # Create bullet in front of the ship
      ship_radius = self.image.width / 2
      bullet_x = self.x + math.cos(angle_radians) * ship_radius
      bullet_y = self.y + math.sin(angle_radians) * ship_radius
      new_bullet = Bullet(x=bullet_x, y=bullet_y)

      # Give it some speed
      direction = pymunk.Vec2d(-math.cos(self.body.angle), -math.sin(self.body.angle))
      new_bullet.body.velocity = direction * self.bullet_speed

      self.game.add_object(new_bullet)
      self.last_fired = now


def configure(config):
  config.physics = 'pymunk'
  config.gravity = 0
  config.fps = 120
  config.fullscreen = True
  config.window_width = None
  config.window_height = None
  config.vsync = True

#XXX player death
#XXX asteroid death / spawning

def init(game):
  min_x, min_y = 0, 0
  max_x, max_y = game.window.get_size()

  def wrap_around(body):
    new_x, new_y = body.position
    if new_x > max_x:
      new_x = min_x
    elif new_x < min_x:
      new_x = max_x
    if new_y > max_y:
      new_y = min_y
    elif new_y < min_y:
      new_y = max_y

    if body.position != (new_x, new_y):
      body.position = (new_x, new_y)
      return True

  def wrap_objects():
    for body in game.physics.space.bodies:
      if wrap_around(body):
        game.physics.space.reindex_shapes_for_body(body)

  game.physics.space.damping = 0.8
  game.post_physics_step = wrap_objects

  player = Player(x=max_x / 2, y=max_y / 2)
  game.add_object(player)

  for i in range(100):
    asteroid = Asteroid(x=randint(0, max_x), y=randint(0, max_y))
    game.add_object(asteroid)

    # Nudge them so they move, slightly off center to add spin
    magnitude = 100
    impulse = Vec2d(magnitude * (random() - 0.5), magnitude * (random() - 0.5))
    asteroid.body.apply_impulse_at_local_point(impulse, point=(5, 5))

  game.play_song('stuff', loop=True)
