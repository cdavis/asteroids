
from random import random, randint

import pyglet
import pymunk

import resources

KEY = pyglet.window.key
Vec2d = pymunk.Vec2d


class GameObject(pyglet.sprite.Sprite):
  image = None
  collides_with = []

  def __init__(self, **kwargs):
    super().__init__(self.image, **kwargs)
    self.create_body(**kwargs)

  def create_body(self, **kwargs):
    raise NotImplementedError()

  def circle_body(self, mass, radius, elasticity=0.95, friction=0.95):
    angular_mass = pymunk.moment_for_circle(mass, 0, radius)
    self.body = pymunk.Body(mass, angular_mass)
    self.body.position = (self.x, self.y)
    self.body.elasticity = elasticity
    self.body.friction = friction
    self.shapes = {
        'body': pymunk.Circle(self.body, radius),
    }

  def update(self, dt):
    pass





class Asteroid(GameObject):
  image = resources.asteroid_image
  collides_with = ['Bullet', 'Player']

  def create_body(self, mass=1, radius=25, **unused):
    self.circle_body(mass, radius)



class Bullet(GameObject):
  image = resources.bullet_image
  collides_with = ['Asteroid']

  def create_body(self, mass=1.0, radius=4, **unused):
    self.circle_body(mass, radius)



class Player(GameObject):
  image = resources.player_image
  collides_with = ['Asteroid']

  def create_body(self, mass=1.0, radius=25, **unused):
    self.circle_body(mass, radius)

    # Child sprite for the engine flame
    self.engine = pyglet.sprite.Sprite(resources.engine_image)
    self.engine.visible = False

    # Movement settings
    self.thrust = 300.0
    self.rotate_speed = 200.0
    self.bullet_speed = 300.0

  def update(self, dt):
    if self.keys[KEY.LEFT]:
      self.body.apply_impulse_at_local_point(Vec2d(-1, 0), point=(0, 1))
      self.body.apply_impulse_at_local_point(Vec2d(1, 0), point=(0, -1))
    elif self.keys[KEY.RIGHT]:
      self.body.apply_impulse_at_local_point(Vec2d(1, 0), point=(0, 1))
      self.body.apply_impulse_at_local_point(Vec2d(-1, 0), point=(0, -1))
    elif self.keys[KEY.UP]:
      self.body.apply_impulse_at_local_point(Vec2d(1, 0), point=(0, 0))
      self.engine.visible = True
    elif self.keys[KEY.DOWN]:
      self.body.apply_impulse_at_local_point(Vec2d(-1, 0), point=(0, 0))

    if not self.keys[KEY.UP]:
      self.engine.visible = False


def configure(config):
  config.physics = 'pymunk'
  config.gravity = 0
  config.fullscreen = True
  config.vsync = True

#XXX player death
#XXX bullet spawning
#XXX asteroid death / spawning

def init(game):
  max_x, max_y = game.window.get_size()

  player = Player(x=max_x / 2, y=max_y / 2)
  game.add_object(player)

  for i in range(10):
    asteroid = Asteroid(x=randint(0, max_x), y=randint(0, max_y))
    game.add_object(asteroid)

    # Nudge them so they move, slightly off center to add spin
    magnitude = 100
    impulse = Vec2d(magnitude * (random() - 0.5), magnitude * (random() - 0.5))
    asteroid.body.apply_impulse_at_local_point(impulse, point=(5, 5))

  #game.play_song('stuff', loop=True)
