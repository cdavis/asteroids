#!/usr/bin/env python3

import math
import importlib
import logging
import sys

import pyglet
import pymunk

import physics
import resources
import settings


class Game:
  def __init__(self, config):
    self.config = config

    physics_class = physics.IMPLEMENTATIONS[config.physics]
    self.physics = physics_class(config)

    self.window = pyglet.window.Window(
        fullscreen=config.fullscreen,
        width=config.window_width,
        height=config.window_height,
        vsync=config.vsync)

    self.fps_display = pyglet.window.FPSDisplay(window=self.window)
    self.main_batch = pyglet.graphics.Batch()
    self.keys = pyglet.window.key.KeyStateHandler()
    self.window.push_handlers(self, self.keys)
    self.player = pyglet.media.Player()

    # Keep track of how far real time is ahead of our physics so we can catch
    # up our simulation gracefully.
    self.uncomputed_time = 0.0

    # Module init creates game objects and stuff.
    module = importlib.import_module(config.module_name)
    module.init(self)

  def add_object(self, obj): #XXX collision masking?
    """Add an object to the game. The object must by a pyglet Sprite that has
    a pymunk .body and .shapes. Maybe something also about collision mask???
    """
    logging.debug(f'Game.add_object() obj={obj}')
    obj.batch = self.main_batch
    self.physics.add_object(obj)

  def run(self):
    seconds_per_frame = 1 / self.config.fps  # delay between game updates
    pyglet.clock.schedule_interval(self.update, seconds_per_frame)

    # Put our song on the jukebox, on repeat.
    song = resources.SONGS[self.config.song]
    self.player.queue(song)
    self.player.loop = True
    self.player.play()

    pyglet.app.run()

  def update(self, dt):
    logging.debug(f'Game.update: dt={int(dt * 1000)}ms')
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
      obj.position = obj.body.position

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
