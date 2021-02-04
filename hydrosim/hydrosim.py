
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


class Drop(GameObject):
  image = resources.bullet_image
  collides_with = ['Drop']

  def create_body(self, mass=1, radius=1, **unused):
    self.circle_body(mass, radius)

  @staticmethod
  def collision_Bullet_begin(arbiter, space, data):
    asteroid_shape, bullet_shape = arbiter.shapes
    game = data['game']

    # This can fail because pymunk is silly.
    try:
      asteroid_obj = game.get_object_from_body(asteroid_shape.body)
      bullet_obj = game.get_object_from_body(bullet_shape.body)
    except KeyError:
      return False

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
 

def configure(config):
  config.physics = 'pymunk'
  config.fps = 120
  config.fullscreen = True
  config.window_width = None
  config.window_height = None
  config.vsync = True


def update(game):
  # Settings and stuff
  min_x, min_y = 0, 0
  max_x, max_y = game.window.get_size()

  max_drops = 100
  drops_per_second = 2
  seconds_per_drop = 1 / drops_per_second
  drop_spawn = (1000, 500)
  drop_scale = 1.0

  # Drop spawner
  if time.time() - game.last_drop > seconds_per_drop:
    game.last_drop = time.time()

    if len(game.drops) < max_drops:
      drop = Drop(x=drop_spawn[0], y=drop_spawn[1], scale=drop_scale)
      game.add_object(drop)

  # Delete fallen drops
  for drop in list(game.drops):
    if drop.body.position[1] > max_y:
      drop.delete()
      game.drops.remove(drop)
 

def init(game):
  # Game state for our update() method
  game.last_drop = time.time()
  game.drops = []

  # Damping makes interactions settle down nicely but also causes our asteroids to just "stop" at some point.
  #game.physics.space.damping = 0.8
  game.post_physics_step = lambda: update(game)

  game.play_song('stuff', loop=True)
