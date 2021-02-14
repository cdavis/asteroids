import pyglet
import pymunk
import logging


class CollisionTyped(type):
  """This metaclass for GameObject lets us allocate a unique collision ID to
  each GameObject subclass."""
  __map = {}

  def __new__(cls, name, bases, dct):
    new = super().__new__(cls, name, bases, dct)

    if name != 'GameObject':
      new.collision_type = 2 ** len(CollisionTyped.__map)
      print(f'AWESOME NEW POWER OF 2: {name} class collision_type={new.collision_type}')
      assert new.collision_type not in CollisionTyped.__map
      CollisionTyped.__map[new.collision_type] = new

    return new


class GameObject(pyglet.sprite.Sprite, metaclass=CollisionTyped):
  # pyglet resource
  image = None

  # Names of all the GameObject subclasses we can collide with
  collides_with = []

  def __init__(self, **kwargs):
    self.children = []
    sprite_flags = 'x y blend_src blend_dest batch group usage subpixel'.split()
    sprite_kwargs = {key: kwargs[key] for key in sprite_flags if key in kwargs}
    super().__init__(self.image, **sprite_kwargs)
    self.create_body(**kwargs)

  def body_kwargs(self):
    """Override this method to return a dict of **kwargs, which will be passed
    to the pymunk.Body() constructor, allowing you to customize self.body."""
    return {}

  def create_body(self, **gameobj_ctor_kwargs):
    # Our **kwargs come from whatever the application code passes to construct
    # their GameObject subclasses. So it can be anything really. Meaning we can't
    # do anything with it here in this generic code, but if you were to say
    # I dunno... OVERRIDE THIS METHOD IN YOUR GameObject SUBCLASS! then yea, you'd
    # probably know exactly what to do here.
    # Your job is to define self.body as a pymunk.Body() object AND
    # to define self.shapes as a dict of shapes with at least one shape called
    # "body" defined. That shape should be defined by the `body_shape` method.
    self.body = pymunk.Body(**self.body_kwargs())
    self.body.position = (self.x, self.y)
    self.shapes = {"body": self.body_shape()}
    for attr, value in gameobj_ctor_kwargs.items():
      setattr(self.shapes["body"], attr, value)

    self.shapes["body"].collision_type = self.collision_type
    self.add_other_shapes()

  def body_shape(self):
    """Override this or create_body, because the default create_body calls this."""
    raise NotImplemented()

  def add_other_shapes(self):
    """Override this and add entries to self.shapes if you have any shapes
    other than 'body'."""

  def circle_body(self, mass, radius, elasticity=0.8, friction=1.0):
    # Helper for when you really don't care what shape the thing is.
    angular_mass = pymunk.moment_for_circle(mass, 0, radius)
    self.body = pymunk.Body(mass, angular_mass)
    self.body.position = (self.x, self.y)
    self.shapes = {
        'body': pymunk.Circle(self.body, radius),
    }
    self.shapes['body'].elasticity = elasticity
    self.shapes['body'].friction = friction
    self.shapes['body'].collision_type = self.collision_type

  def update(self, now, dt):
    pass

  def delete(self):
    logging.debug(f'GameObject.delete() self={self}')
    self.game.remove_object(self)

  def cleanup(self):
      """Do any last-minute custom cleanup behaviors for deleted objects."""
      pass
