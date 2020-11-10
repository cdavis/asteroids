#!/usr/bin/env python3

import math
import logging
import sys

import pyglet
import pymunk

import physics
import resources
import settings


class Floor(pyglet.sprite.Sprite):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, img=resources.asteroid_image, **kwargs)
    self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
    self.circle = pymunk.Segment(self.body, (0, 0), (2000, 0), 30)
    self.scale = 0.00001


class Asteroid(pyglet.sprite.Sprite):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, img=resources.asteroid_image, **kwargs)
    mass = 1
    radius = 50
    inertia = pymunk.moment_for_circle(mass, 0, radius)
    self.body = pymunk.Body(mass, inertia)
    self.body.position = (kwargs['x'], kwargs['y'])
    self.body.elasticity = 1.0
    self.circle = pymunk.Circle(self.body, radius)


class Game:
  def __init__(self, config):
    self.config = config

    physics_impl_class = physics.IMPLEMENTATIONS[config.physics]
    self.physics = physics_impl_class(config)

    self.window = pyglet.window.Window(
        fullscreen=config.fullscreen,
        width=config.window_width,
        height=config.window_height,
        vsync=config.vsync)

    self.fps_display = pyglet.window.FPSDisplay(window=self.window)
    self.main_batch = pyglet.graphics.Batch()
    self.keys = pyglet.window.key.KeyStateHandler()
    self.window.push_handlers(self, self.keys)

    # Keep track of how far rendering is ahead of physics so we can catch
    # up our simulation gracefully.
    self.uncomputed_time = 0.0

    asteroid = Asteroid(x=1000, y=2000, batch=self.main_batch)
    floor = Floor(x=0, y=0, batch=self.main_batch)
    self.physics.add_object(asteroid)
    self.physics.add_object(floor)

  def run(self):
    seconds_per_frame = 1 / self.config.fps  # delay between game updates
    pyglet.clock.schedule_interval(self.update, seconds_per_frame)
    resources.theme_song.play()
    pyglet.app.run()

  def update(self, dt):
    logging.debug(f'Game.update: dt ms={int(dt * 1000)}')
    self.uncomputed_time += dt

    # To keep the physics behavior nice and stable we should *always* pass the
    # same dt value to physics.step(). But because this function gets called
    # with various delays we have to track uncomputed time explicitly.
    physics_dt = 1 / self.config.fps
    while self.uncomputed_time > physics_dt:
      logging.debug('physics step')
      self.physics.step(physics_dt)
      self.uncomputed_time -= physics_dt

    # Update sprite positions/angles from physics shapes
    for obj in self.physics.objects:
      logging.debug(f'updating obj {obj}: body.angle={obj.body.angle} pos.x={obj.body.position.x} pos.y={obj.body.position.y}')
      obj.rotation = math.degrees(-obj.body.angle) + 180
      obj.position = (obj.body.position.x, obj.body.position.y)

    # spawn new game objects
    # remove dead game objects
    # detect game win / loss conditions
    # update hud

  def on_draw(self):
    logging.debug('Game.on_draw')
    self.window.clear()
    self.main_batch.draw()
    self.fps_display.draw()



def main():
  try:
    config = settings.build_config()
  except settings.ConfigError as error:
    print(error)
    return 1

  # Do not touch the sacred GLOG format.
  logging.basicConfig(
      format="{levelname:.1}{asctime}.{msecs:03.0f} {filename}:{lineno}] {message}",
      style='{',
      datefmt="%m%d %H:%M:%S",
      level=logging.DEBUG if config.debug else logging.INFO)

  game = Game(config)
  game.run()

if __name__ == '__main__':
  sys.exit(main() or 0)
