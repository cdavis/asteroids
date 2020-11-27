#!/usr/bin/env python3

import math
import importlib
import logging
import sys

import pyglet
import pymunk

from objects import GameObject
import physics
import resources
import settings


class Game:
  def __init__(self, config):
    self.config = config

    # Load our game module, let it customize the config
    self.module = importlib.import_module(config.module_name)
    self.module.configure(config)

    game_object_classes = {}
    for obj in vars(self.module).values():
      try:
        if issubclass(obj, GameObject) and obj is not GameObject:
          game_object_classes[obj.__name__] = obj
      except TypeError:
        continue

    self.object_by_body = {}
    physics_class = physics.IMPLEMENTATIONS[config.physics]
    self.physics = physics_class(self, game_object_classes)

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

    self.module.init(self)

  def add_object(self, obj):
    """Add an object to the game. The object must by a pyglet Sprite that has
    a pymunk .body and .shapes. Maybe something also about collision mask???
    """
    logging.debug(f'Game.add_object() obj={obj}')
    self.object_by_body[obj.body] = obj
    obj.game = self
    obj.batch = self.main_batch
    obj.keys = self.keys
    self.physics.add_object(obj)

  def remove_object(self, obj):
    logging.debug(f'Game.remove_object() obj={obj}')
    self.physics.remove_object(obj)
    del self.object_by_body[obj.body]

  def get_object_from_body(self, body):
    return self.object_by_body[body]

  def play_song(self, name, loop=False):
    song_source = resources.SONGS[name]
    self.player.queue(song_source)
    self.player.loop = loop
    self.player.play()

  def run(self):
    seconds_per_frame = 1 / self.config.fps  # delay between game updates
    pyglet.clock.schedule_interval(self.update, seconds_per_frame)
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
      self.post_physics_step()

    # Update sprite positions/angles from physics shapes
    for obj in self.physics.objects:
      logging.debug(f'updating obj {obj}: body.angle={obj.body.angle} pos.x={obj.body.position.x} pos.y={obj.body.position.y}')
      obj.rotation = math.degrees(-obj.body.angle) + 180
      obj.position = obj.body.position
      obj.update(dt)

    # spawn new game objects
    # remove dead game objects
    # detect game win / loss conditions
    # update hud

  def post_physics_step(self):
    """Override this to do whatever you want."""

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
