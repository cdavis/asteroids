import pyglet
import pymunk


class CollisionTyped(type):
  """This metaclass for GameObject lets us allocate a unique collision ID to
  each GameObject subclass."""
  __map = {}

  def __new__(cls, name, bases, dct):
    new = super().__new__(cls, name, bases, dct)

    if name != 'GameObject':
      new.collision_type = len(CollisionTyped.__map) + 1
      assert new.collision_type not in CollisionTyped.__map
      CollisionTyped.__map[new.collision_type] = new

    return new


class GameObject(pyglet.sprite.Sprite, metaclass=CollisionTyped):
  # pyglet resource
  image = None

  # Names of all the GameObject subclasses we can collide with
  collides_with = []

  def __init__(self, **kwargs):
    sprite_flags = 'x y blend_src blend_dest batch group usage subpixel'.split()
    sprite_kwargs = {key: kwargs[key] for key in sprite_flags if key in kwargs}
    super().__init__(self.image, **sprite_kwargs)
    self.create_body(**kwargs)

  def create_body(self, **kwargs):
    raise NotImplementedError()

  def circle_body(self, mass, radius, elasticity=0.8, friction=1.0):
    angular_mass = pymunk.moment_for_circle(mass, 0, radius)
    self.body = pymunk.Body(mass, angular_mass)
    self.body.position = (self.x, self.y)
    self.shapes = {
        'body': pymunk.Circle(self.body, radius),
    }
    self.shapes['body'].elasticity = elasticity
    self.shapes['body'].friction = friction
    self.shapes['body'].collision_type = self.collision_type

  def update(self, dt):  # TODO: current time
    pass
