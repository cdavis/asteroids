#!/usr/bin/env python3

import logging
import pymunk


ALL_MASKS = pymunk.ShapeFilter.ALL_MASKS


class PhysicsEngineBase:
  """Base Class for physics engine implementations."""

  def __init__(self, game, object_classes):
    self.game = game
    self.objects = []
    self.object_classes = object_classes
    self.init()

  def init(self):
    """Subclass-specific initialization"""

  def add_object(self, obj):
    if obj in self.objects:
      raise Exception(f'Object {obj} already added')

    self.objects.append(obj)

  def remove_object(self, obj):
    if obj not in self.objects:
      raise Exception(f'Object {obj} does not exist in the physics!')

    self.objects.remove(obj)

  def step(self, dt):
    """Compute physics changes elapsed during 'dt' seconds."""
    raise NotImplementedError()


class CheesyPhysics(PhysicsEngineBase):

  def step(self, now, dt):
    # Collision detect
    for i in range(len(self.objects)):
      for j in range(i + 1, len(self.objects)):
        obj1 = self.objects[i]
        obj2 = self.objects[j]

        if obj1.collides_with(obj2):
          obj1.handle_collision_with(obj2)
          obj2.handle_collision_with(obj1)

    # Objects to add, delete
    for obj in self.objects:
      obj.update(now, dt)


class PymunkPhysics(PhysicsEngineBase):

  def init(self):
    self.space = pymunk.Space()
    self.space.gravity = (0, -self.game.config.gravity)

    for src_class in self.object_classes.values():
      for dst_class_name in src_class.collides_with:
        dst_class = self.object_classes[dst_class_name]

        # Attach handler function if we have one
        handler = self.space.add_collision_handler(
            src_class.collision_type,
            dst_class.collision_type)

        handler.data['game'] = self.game

        for phase in ['begin', 'pre_solve', 'post_solve', 'separate']:
          method_name = f'collision_{dst_class.__name__}_{phase}'
          method = getattr(src_class, method_name, None)
          if method:
            logging.info(f'Collision handler method for {src_class.__name__} to {dst_class.__name__} {phase}')
            logging.info(f'Handler({src_class.__name__}={src_class.collision_type},{dst_class.__name__}={dst_class.collision_type})')
            method = self._decorate_collision_handler(method)
            setattr(handler, phase, method)

  def _decorate_collision_handler(self, func):

    def wrapper(*args, **kwargs):
      logging.info(f'Collision Handler {func.__name__}')
      return func(*args, **kwargs)

    return wrapper


  def add_object(self, obj):
    super().add_object(obj)
    self.space.add(obj.body, *obj.shapes.values())
    
    collision_mask = 0
    for other_gameobj_class_name in obj.collides_with:
      other_gameobj_class = self.object_classes[other_gameobj_class_name]
      collision_mask |= other_gameobj_class.collision_type

    filter = pymunk.ShapeFilter(categories=obj.collision_type, mask=collision_mask)
    logging.debug(f'Configuring {obj} with filter={filter}')

    # Optimization, comment it out if collides_with ain't right.
    for shape in obj.shapes.values():
      shape.filter = filter

  def remove_object(self, obj):
    super().remove_object(obj)
    self.space.remove(obj.body, *obj.shapes.values())


  def step(self, dt):
    self.space.step(dt)


# Dict of all our physics engines
IMPLEMENTATIONS = {
    'cheesy': CheesyPhysics,
    'pymunk': PymunkPhysics,
}
