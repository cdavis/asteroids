
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
  collides_with = ['Drop', 'Floor']

  def create_body(self, mass=1, radius=4, **unused):
    self.circle_body(mass, radius)


class Floor(GameObject):
  image = resources.floor_image
  collides_with = ['Drop']

  def create_body(self, width=250, height=40, a_tilt=0, **unused):
    self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
    self.body.position = (self.x, self.y)
    a = (-width / 2, a_tilt)
    b = (width / 2, -a_tilt)
    radius = height / 2
    self.shapes = {
        'body': pymunk.Segment(self.body, a, b, radius),
    }
    self.shapes['body'].elasticity = 0.8
    self.shapes['body'].friction = 1.0

  def draw_shapes(self):
    # Since we have no image, draw the body shapes
    self.line = pyglet.shapes.Line(a,b,c,d,
        width=15,
        color=(255, 40, 60),
        batch=self.batch,
    )


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
  drops_per_second = 20
  seconds_per_drop = 1 / drops_per_second
  drop_spawn = (1000, 500)
  drop_scale = 50.0

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

  # Set background RGBA
  pyglet.gl.glClearColor(255, 255, 255, 255)

  # Throw in a floor or two
  floor1 = Floor(x=1000, y=250, a_tilt=25)
  floor2 = Floor(x=1000, y=250, a_tilt=-25)
  game.add_object(floor1)
  game.add_object(floor2)

  # Damping makes interactions settle down nicely but also causes our asteroids to just "stop" at some point.
  #game.physics.space.damping = 0.8
  game.post_physics_step = lambda: update(game)

  game.play_song('stuff', loop=True)
