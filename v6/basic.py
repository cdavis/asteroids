#!/usr/bin/env python3

import logging
import sys

import pyglet

from settings import ConfigError, build_config


class Game:
  def __init__(self, config):
    self.config = config

    self.window = pyglet.window.Window(
        fullscreen=config.fullscreen,
        width=config.window_width,
        height=config.window_height,
        vsync=config.vsync)

  def update(self, dt):
    ms = int(dt * 1000)
    logging.debug(f'update: dt ms={ms}')






def main():
  # Get our config from CLI args
  try:
    config = build_config()
  except ConfigError as error:
    print(error)
    return 1

  # Configure logging
  logging.basicConfig(
      format="{levelname:.1}{asctime}.{msecs:03.0f} {filename}:{lineno}] {message}",
      style='{',
      datefmt="%m%d %H:%M:%S",  # glog-ish strftime format
      level=logging.DEBUG if config.debug else logging.INFO)

  # Run our game
  game = Game(config)
  seconds_per_frame = 1 / config.fps  # delay between game updates
  pyglet.clock.schedule_interval(game.update, seconds_per_frame)
  pyglet.app.run()


if __name__ == '__main__':
  sys.exit(main() or 0)
