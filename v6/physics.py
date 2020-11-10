#!/usr/bin/env python3

#import logging
#import pyglet
import pymunk


class PhysicsEngineBase:
  """Base Class for physics engine implementations."""

  def __init__(self, config):
    self.config = config
    self.objects = []

  def add_object(self, obj):
    if obj in self.objects:
      raise Exception(f'Object {obj} already added')

    self.objects.append(obj)

  def step(self, dt):
    """Compute physics changes elapsed during 'dt' seconds."""
    raise NotImplemented()


class CheesyPhysics(PhysicsEngineBase):

  def step(self, dt):
    # Collision detect
    for obj in self.objects:
        pass #XXX


class PymunkPhysics(PhysicsEngineBase):
  def __init__(self, config):
    super().__init__(config)
    self.space = pymunk.Space()
    self.space.gravity = (0, -config.gravity)

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
