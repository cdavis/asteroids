
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

  @staticmethod
  def collision_Bullet_begin(arbiter, space, data):
    print(f'Asteroid.collision_Bullet_begin()  arbiter={arbiter} space={space} data={data}')
    asteroid_shape, bullet_shape = arbiter.shapes
    game = data['game']

    # This can fail because pymunk is silly.
    try:
      asteroid_obj = game.get_object_from_body(asteroid_shape.body)
      bullet_obj = game.get_object_from_body(bullet_shape.body)
    except KeyError:
      return

    radius = asteroid_obj.shapes['body'].radius

    # Create new sub-asteroids by sweeping our 'clock hand' vector vec around.
    angle = 0.0
    num_subs = 2

    if asteroid_obj.scale > 0.5:
      for i in range(num_subs):
        vec = pymunk.Vec2d(-math.cos(angle), -math.sin(angle))
        vec *= radius
        sub_asteroid = Asteroid(
            x=vec.x + asteroid_obj.x,
            y=vec.y + asteroid_obj.y,
        )
        sub_asteroid.scale = asteroid_obj.scale * 0.7
        game.add_object(sub_asteroid)
        angle += math.pi * 2 / num_subs

    asteroid_obj.delete()
    bullet_obj.delete()
    return True
 

class Bullet(GameObject):
  image = resources.bullet_image
  collides_with = ['Asteroid']

  def create_body(self, mass=1.0, radius=4, lifespan=0.5, **unused):
    self.expiration_time = time.time() + lifespan
    self.circle_body(mass, radius)

  def update(self, now, dt):
    if now > self.expiration_time:
      self.delete()


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

    # Movement settings
    self.thrust = 400.0
    self.rotate_speed = 3.0
    self.bullet_speed = 1000.0
    self.bullet_delay = 0.1
    self.brake_damping = 0.03
    self.min_velocity = 50.0
    self.max_velocity = 600.0
    self.last_fired = 0.0

    # Child sprite for the engine flame
    self.engine = pyglet.sprite.Sprite(resources.engine_image)
    self.update_engine()
    self.engine.visible = False
    self.children.append(self.engine)

  def update(self, now, dt):
    if self.keys[KEY.LEFT]:
      self.body.angle += self.rotate_speed * dt

    elif self.keys[KEY.RIGHT]:
      self.body.angle -= self.rotate_speed * dt

    elif self.keys[KEY.UP]:
      self.engine.visible = True
      direction = pymunk.Vec2d(-math.cos(self.body.angle), -math.sin(self.body.angle))
      self.body.velocity += direction * self.thrust * dt

    elif self.keys[KEY.DOWN]:
      self.body.velocity *= 1 - self.brake_damping
      if self.body.velocity.length < self.min_velocity:
        self.body.velocity = pymunk.Vec2d(0, 0)

    if not self.keys[KEY.UP]:
      self.engine.visible = False

    if self.keys[KEY.SPACE]:
      self.fire()

    self.update_engine()

  def update_engine(self):
    self.engine.rotation = self.rotation
    self.engine.x = self.x
    self.engine.y = self.y
    self.engine.scale = 1.0 + (math.sin(20 * time.time()) / 10)

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

  # Damping makes interactions settle down nicely but also causes our asteroids to just "stop" at some point.
  #game.physics.space.damping = 0.8
  game.post_physics_step = wrap_objects

  player = Player(x=max_x / 2, y=max_y / 2)
  game.add_object(player)

  for i in range(100):
    asteroid = Asteroid(x=randint(0, max_x), y=randint(0, max_y), scale=1.0)
    game.add_object(asteroid)

    # Nudge them so they move, slightly off center to add spin
    magnitude = 100
    impulse = Vec2d(magnitude * (random() - 0.5), magnitude * (random() - 0.5))
    asteroid.body.apply_impulse_at_local_point(impulse, point=(5, 5))

  game.play_song('stuff', loop=True)
