
import functools
import logging
import math
from random import random, randint
import time

import pyglet
import pymunk

from objects import GameObject
import resources

KEY = pyglet.window.key
KEYS = KEY.KeyStateHandler()
MOUSE = pyglet.window.mouse
Vec2d = pymunk.Vec2d
PI = math.pi

def ALL_MASKS():  # So it works from either old or new pymunk
  try:
    return pymunk.ShapeFilter.ALL_MASKS()
  except:
    return pymunk.ShapeFilter.ALL_MASKS


class Drop(GameObject):
  image = resources.bullet_image
  collides_with = ['Drop', 'Floor']

  def create_body(self, mass, scale, radius=4.5, **unused):
    self.circle_body(mass, int(radius * scale))
    self.drop_scale = scale
    pyglet.sprite.Sprite.update(self, scale=scale)

  @staticmethod
  def collision_Floor_begin(arbiter, space, data):
    drop_shape, floor_shape = arbiter.shapes
    game = data['game']

    # This can fail because pymunk is silly.
    try:
      drop_obj = game.get_object_from_body(drop_shape.body)
      floor_obj = game.get_object_from_body(floor_shape.body)
    except KeyError:
      return False

    if floor_obj.is_goal:
      drop_obj.delete()
      if drop_obj in game.drops:
        game.drops.remove(drop_obj)

    else:
      #force = Vec2d(1000, 0)
      force = arbiter.normal * 1000
      drop_shape.body.apply_impulse_at_local_point(force, (0, 0))

    return True


class Floor(GameObject):
  image = resources.bullet_image
  collides_with = ['Drop']
  shape_to_obj = {}  # Map pymunk 'body' shape Segments to their owning Floor object

  def create_body(
      self,
      width=250,
      height=40,
      rotate=0,
      batch=None,
      color=(55, 55, 255),
      is_goal=False,
      body_type=pymunk.Body.STATIC,
      **unused):
    assert batch
    self.body = pymunk.Body(body_type=body_type)
    self.body.position = (self.x, self.y)
    a = (-width / 2, 0)
    b = (width / 2, 0)
    radius = height / 2
    self.shapes = {
        'body': pymunk.Segment(self.body, a, b, radius),
    }
    self.shapes['body'].elasticity = 0.8
    self.shapes['body'].friction = 0.8
    self.shapes['body'].collision_type = self.collision_type  # Very important!
    self.shape_to_obj[self.shapes['body']] = self

    self.body.angle += rotate

    # Draw our own visual instead of self.image
    self.rect = pyglet.shapes.Rectangle(
        x=self.x,
        y=self.y,
        width=width,
        height=height,
        color=color if not is_goal else (255, 255, 55),
        batch=batch,
    )
    self.rect.anchor_position = (width / 2, height / 2)
    self.is_goal = is_goal

  def update(self, now, dt):
    self.rect.rotation = math.degrees(-self.body.angle) + 180

  def cleanup(self):
    # Called when we get deleted, remove our entry from our shape_to_obj tracking map
    for shape, obj in list(self.shape_to_obj.items()):
      if obj is self:
        del self.shape_to_obj[shape]


def configure(config):
  config.physics = 'pymunk'
  config.fps = 120
  config.fullscreen = True
  config.window_width = None
  config.window_height = None
  #config.vsync = True


def update(game):
  # Settings and stuff
  min_x, min_y = 0, 0
  max_x, max_y = game.window.get_size()

  max_drops = 2000
  drops_per_second = 100
  seconds_per_drop = 1 / drops_per_second
  drop_spawn = (1000, 500)
  spawn_jitter = (100, 100)
  max_scale = 10.0  # TODO: we got the sprite to scale, but not the collision body. fix that so things look way better.

  # Drop spawner
  if time.time() - game.last_drop > seconds_per_drop:
    game.last_drop = time.time()

    if len(game.drops) < max_drops:
      x_jitter = randint(-spawn_jitter[0]/2, spawn_jitter[0]/2)
      y_jitter = randint(-spawn_jitter[1]/2, spawn_jitter[1]/2)

      #scale = 1 + random() * max_scale  # big ones take up most of the space.
      scale = 1.0
      while random() < 0.8 and scale < max_scale:
        scale += random()

      drop = Drop(
        x=drop_spawn[0] + x_jitter,
        y=drop_spawn[1] + y_jitter,
        mass=randint(0, 10),
        scale=min(scale, max_scale),
      )
      game.add_object(drop)
      game.drops.append(drop)

  # Delete fallen drops
  for drop in list(game.drops):
    x, y = drop.body.position
    if y < 0 or y > max_y or x < 0 or x > max_x:
      drop.delete()
      game.drops.remove(drop)

  game.obj_count_update()


def on_mouse_press(game, x, y, button, modifiers):
  #print(f'on_mouse_press(x={x}, y={y}, button={button}, modifiers={modifiers})')
  if button in (MOUSE.LEFT, MOUSE.MIDDLE):
    floor = Floor(x=x, y=y, rotate=(30 * random()) - 15, batch=game.main_batch, is_goal=button == MOUSE.MIDDLE)
    game.add_object(floor)
  elif button == MOUSE.RIGHT:
    point = (x, y)
    info = game.physics.space.point_query_nearest(
      point,
      max_distance=250,
      shape_filter=pymunk.ShapeFilter(categories=ALL_MASKS() ^ Floor.collision_type),
    )
    if info and info.shape and info.shape in Floor.shape_to_obj:
      Floor.shape_to_obj[info.shape].delete()


def on_mouse_motion(game, x, y, dx, dy):
  if game.cursor_obj:
    game.cursor_obj.body.position = (x, y)
    game.cursor_obj.rect.position = (x, y)


def on_key_press(game, symbol, modifiers):  # Basic, one direction at a time
  current_magnitude = 900  #XXX

  if symbol == KEY.LEFT:
    game.physics.space.gravity = (-current_magnitude, 0)
  elif symbol == KEY.RIGHT:
    game.physics.space.gravity = (current_magnitude, 0)
  elif symbol == KEY.UP:
    game.physics.space.gravity = (0, current_magnitude)
  elif symbol == KEY.DOWN:
    game.physics.space.gravity = (0, -current_magnitude)


def on_key_press2(game, symbol, modifiers):  # Toggle gravity in each direction
  current = list(game.physics.space.gravity)

  if symbol == KEY.LEFT:
    current[0] = 0 if current[0] else 900
  elif symbol == KEY.RIGHT:
    current[0] = 0 if current[0] else -900
  elif symbol == KEY.UP:
    current[1] = 0 if current[1] else 900
  elif symbol == KEY.DOWN:
    current[1] = 0 if current[1] else -900
  else:
    return

  game.physics.space.gravity = current


def init(game):
  # Set background RGBA
  pyglet.gl.glClearColor(255, 255, 255, 255)

  # Game state for our update() method
  game.last_drop = time.time()
  game.drops = []
  screen_width, screen_height = game.window.get_size()
  center_x = screen_width / 2
  center_y = screen_height / 2
  game.cursor_obj = None

  if game.config.cursor:
    game.cursor_obj = Floor(x=0, y=0, rotate=0, height=200, batch=game.main_batch, body_type=pymunk.Body.KINEMATIC)
    game.add_object(game.cursor_obj)

  # Setup event handling
  game.window.on_mouse_press = functools.partial(on_mouse_press, game)
  game.window.on_mouse_motion = functools.partial(on_mouse_motion, game)
  game.window.on_key_press = functools.partial(on_key_press, game)

  # Object counter
  text_opts = {
      'font_name': 'Courier New',
      'font_size': 16,
      'color': (80, 80, 120, 255),
      'x': screen_width - 200,
      'y': screen_height - 40,
      'batch': game.main_batch,
  }
  obj_count_label = pyglet.text.Label("Objects: 0", **text_opts)

  def obj_count_update():
    obj_count_label.text = f"objects: {len(game.drops)}"

  game.obj_count_update = obj_count_update

  # Throw in a floor or two
  floor1 = Floor(x=1000, y=500, rotate=10, batch=game.main_batch)
  floor2 = Floor(x=1000, y=500, rotate=-10, batch=game.main_batch)
  game.add_object(floor1)
  game.add_object(floor2)

  # Big green floor dealies
  mega_floor = Floor(x=center_x, y=1, width=screen_width, batch=game.main_batch, color=(0, 255, 0))
  game.add_object(mega_floor)
  mega_floor2 = Floor(x=center_x, y=screen_height, width=screen_width, batch=game.main_batch, color=(0, 255, 0))
  game.add_object(mega_floor2)
  mega_floor3 = Floor(x=screen_width, y=center_y, width=screen_width, batch=game.main_batch, color=(0, 255, 0), rotate=PI/4)
  game.add_object(mega_floor3)
  mega_floor4 = Floor(x=1, y=center_y, width=screen_width, batch=game.main_batch, color=(0, 255, 0), rotate=-PI/4)
  game.add_object(mega_floor4)

  # GOOOOOOOAAAAAL
  goal = Floor(x=1300, y=250, batch=game.main_batch, is_goal=True)
  game.add_object(goal)

  # Damping makes interactions settle down nicely but also causes our asteroids to just "stop" at some point.
  #game.physics.space.damping = 0.8
  game.post_physics_step = lambda: update(game)
  game.window.set_mouse_visible(True)
  game.play_song('stuff', loop=True)
