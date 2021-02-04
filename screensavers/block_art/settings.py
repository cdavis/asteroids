import argparse
import random

#import physics
#import resources


class ConfigError(Exception):
  """Your config is bad and you should feel bad."""


def build_config():
  """This function returns an object that has all the settings used by the
  game engine accessible as attributes."""

  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action='store_true')

  parser.add_argument(
      '--fps',
      type=int,
      default=60,
      help='Game updates per second')

  parser.add_argument('--fullscreen', action='store_true')
  parser.add_argument('--vsync', action='store_true')

  parser.add_argument(
      '--window-width',
      type=int,
      default=1024)

  parser.add_argument(
      '--window-height',
      type=int,
      default=768)

  #parser.add_argument(
  #    '--physics',
  #    default='pymunk',
  #    choices=sorted(physics.IMPLEMENTATIONS),
  #    help='Which physics engine to use')

  parser.add_argument(
      '--gravity',
      default=900,
      type=int,
      help='How strong gravity is')

  #parser.add_argument(
  #    '--song',
  #    default=random.choice(list(resources.SONGS)),
  #    choices=sorted(resources.SONGS),
  #    help='Select your jam.')

  config = parser.parse_args()

  # Validate the config is good before returning it, raise useful error message.
  if config.fullscreen:
    config.window_width = None
    config.window_height = None

  return config
