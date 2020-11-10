
from random import randint

import pyglet
import pymunk

import resources


class Floor(pyglet.sprite.Sprite):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, img=resources.asteroid_image, **kwargs)
    self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
    self.shapes = {
        'floor': pymunk.Segment(self.body, (0, 0), (2000, 0), 30),
    }
    self.shapes['floor'].elasticity = 0.95
    self.shapes['floor'].friction = 0.95


class Asteroid(pyglet.sprite.Sprite):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, img=resources.asteroid_image, **kwargs)
    mass = 0.01
    radius = 25
    angular_mass = pymunk.moment_for_circle(mass, 0, radius)
    self.body = pymunk.Body(mass, angular_mass)
    self.body.position = (kwargs['x'], kwargs['y'])
    self.body.elasticity = 0.95
    self.body.friction = 0.95
    self.shapes = {
        'body': pymunk.Circle(self.body, radius),
    }



def init(game):
  max_x, max_y = game.window.get_size()

  for i in range(10):
    asteroid = Asteroid(x=randint(0, max_x), y=randint(0, max_y))
    asteroid.rotation = randint(0, 360)
    game.add_object(asteroid)

  floor = Floor(x=0, y=0)
  game.add_object(floor)
