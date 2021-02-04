#!/usr/bin/env python3

import logging
import pymunk


class PhysicsEngineBase:
  """Base Class for physics engine implementations."""

  def __init__(self, config, object_classes):
    self.config = config
    self.objects = []
    self.set_allowed_collisions(object_classes)

  def set_allowed_collisions(self, object_classes):
    raise NotImplementedError()

  def add_object(self, obj):
    if obj in self.objects:
      raise Exception(f'Object {obj} already added')

    self.objects.append(obj)

  def step(self, dt):
    """Compute physics changes elapsed during 'dt' seconds."""
    raise NotImplementedError()


class CheesyPhysics(PhysicsEngineBase):

  def step(self, dt):
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
      obj.update(dt)


class PymunkPhysics(PhysicsEngineBase):

  def set_allowed_collisions(self, obj_classes):
    self.space = pymunk.Space()
    self.space.gravity = (0, -self.config.gravity)

    for src_class in obj_classes.values():
      for dst_class_name in src_class.collides_with:
        dst_class = obj_classes[dst_class_name]

        handler = self.space.add_collision_handler(
            src_class.collision_type,
            dst_class.collision_type)

        for phase in ['begin', 'pre_solve', 'post_solve', 'separate']:
          method_name = f'collision_{dst_class.__name__}_{phase}'
          method = getattr(src_class, method_name, None)
          if method:
            logging.info(f'Collision handler method for {src_class.__name__} to {dst_class.__name__} {phase}')
            setattr(handler, phase, method)

  def add_object(self, obj):
    super().add_object(obj)
    self.space.add(obj.body, *obj.shapes.values())

  def step(self, dt):
    self.space.step(dt)


# Dict of all our physics engines
IMPLEMENTATIONS = {
    'cheesy': CheesyPhysics,
    'pymunk': PymunkPhysics,
}
