
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
  image = resources.bullet_image
  collides_with = ['Drop']

  def create_body(self, width=250, height=40, rotate=0, batch=None, **unused):
    assert batch
    self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
    self.body.position = (self.x, self.y)
    a = (-width / 2, 0)
    b = (width / 2, 0)
    radius = height / 2
    self.shapes = {
        'body': pymunk.Segment(self.body, a, b, radius),
    }
    self.shapes['body'].elasticity = 0.8
    self.shapes['body'].friction = 1.0

    self.body.angle += rotate

    # Draw our own visual instead of self.image
    self.rect = pyglet.shapes.Rectangle(
        x=self.x,
        y=self.y,
        width=width,
        height=height,
        color=(55, 55, 255),
        batch=batch,
    )
    self.rect.anchor_position = (width / 2, height / 2)

  def update(self, now, dt):
    self.rect.rotation = math.degrees(-self.body.angle) + 180


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

  max_drops = 2000
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
      game.drops.append(drop)

  # Delete fallen drops
  for drop in list(game.drops):
    if drop.body.position[1] > max_y:
      drop.delete()
      game.drops.remove(drop)

  game.obj_count_update()
 

def init(game):
  # Game state for our update() method
  game.last_drop = time.time()
  game.drops = []
  screen_width, screen_height = game.window.get_size()
  center_x = screen_width / 2

  # Set background RGBA
  pyglet.gl.glClearColor(255, 255, 255, 255)

  # Object counter
  text_opts = {
      'font_name': 'Courier New',
      'font_size': 16,
      'color': (80, 80, 120, 255),
      'x': screen_width - 200,
      'y': screen_height - 40,
      'batch': game.main_batch,
  }
  obj_count_label = pyglet.text.Label("Objects: 0", **text_opts)

  def obj_count_update():
    obj_count_label.text = f"objects: {len(game.drops)}"

  game.obj_count_update = obj_count_update

  # Throw in a floor or two
  floor1 = Floor(x=1000, y=250, rotate=10, batch=game.main_batch)
  floor2 = Floor(x=1000, y=250, rotate=-10, batch=game.main_batch)
  mega_floor = Floor(x=center_x, y=1, width=screen_width, batch=game.main_batch)
  game.add_object(floor1)
  game.add_object(floor2)
  game.add_object(mega_floor)

  # Damping makes interactions settle down nicely but also causes our asteroids to just "stop" at some point.
  #game.physics.space.damping = 0.8
  game.post_physics_step = lambda: update(game)

  game.play_song('stuff', loop=True)
