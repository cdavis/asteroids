#!/usr/bin/env python3

import logging
from math import sqrt
from random import randint

import pyglet
from pyglet.gl import *

import settings


KEY = pyglet.window.key


class Game:
  def __init__(self, config):
    self.config = config
    self.window = pyglet.window.Window(fullscreen=True)
    self.keys = pyglet.window.key.KeyStateHandler()
    self.window.push_handlers(self.keys, self.on_draw)
    self.main_batch = pyglet.graphics.Batch()
    self.objects = []

  def setup(self):
    """Override this in subclass to create shapes and stuff."""

  def add_object(self, obj):
    self.objects.append(obj)

  def run(self):
    self.setup()
    pyglet.clock.schedule_interval(self.update, 1 / self.config.fps)
    pyglet.app.run()

  def update(self, dt):
    print(f'update() dt={dt}')

    #if self.keys[KEY.A]:
    #  text_buf.input('a')

    for obj in self.objects:
      obj.update()

  def on_draw(self):
    self.window.clear()
    self.main_batch.draw()


class Block:
  WIDTH = 32
  HEIGHT = 32

  def __init__(self, x, y, id, batch):
    self.x = int(x)
    self.y = int(y)
    self.id = id
    self.square = pyglet.shapes.Rectangle(
        x=self.x * self.WIDTH,
        y=self.y * self.HEIGHT,
        width=self.WIDTH,
        height=self.HEIGHT,
        color=(0, 0, 0),
        batch=batch,
    )

  def update(self):
    # Scale behavior based on size
    area = self.square.width * self.square.height
    max_area = 32 * 32
    area_frac = float(area) / max_area

    r, g, b = self.square.color

    # Nudge each color up to some amount n
    n = randint(1, 7)
    new_r = r + randint(-n, n)
    new_g = g + randint(-n, n)
    new_b = b + randint(-n, n)

    # Bump overall brightness up to some amount
    brightness = r + g + b
    avg_brightness = 3 * (255 / 2)
    if brightness < avg_brightness:
        new_r += randint(-5, 15)
        new_g += randint(-5, 15)
        new_b += randint(-5, 15)

    # Clamping
    new_r = max(0, min(255, new_r))
    new_g = max(0, min(255, new_g))
    new_b = max(0, min(255, new_b))

    self.square.color = (new_r, new_g, new_b)

    # Size change
    s = randint(1, 3)
    new_w = self.square.width + randint(-s, s)
    new_h = self.square.height + randint(-s, s)
    self.square.width = max(0, min(32, new_w))
    self.square.height = max(0, min(32, new_h))


class ShapeJump(Game):
  def setup(self):
    # Hard-code a test level, eventually just load this from a data file instead.
    self.blocks = set()

    # Start with floor of 100 blocks
    for x in range(100):
      for y in range(1, 45):
        block_id = '^' if abs(x - 17) < 3 else '#'
        block = Block(x, y, block_id, batch=self.main_batch)
        self.add_object(block)
        self.blocks.add(block)



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

  game = ShapeJump(config)
  game.run()


if __name__ == '__main__':
  main()
