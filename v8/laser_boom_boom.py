#!/usr/bin/env python3

import pyglet
from pyglet.gl import *


KEY = pyglet.window.key
KEYS = pyglet.window.key.KeyStateHandler()

win = pyglet.window.Window(fullscreen=True)
win.push_handlers(KEYS)
pressed = set()


class TextBuffer:
  def __init__(self):
    self.buf = []

  def input(self, text):
    self.buf.extend(text)

  def get(self):
    return ''.join(self.buf)


@win.event
def on_draw():
  win.clear()
  text_opts = {
    'font_name': 'Courier New',
    'font_size': 48,
    'color': (0, 255, 0, 255),
    'x': 10,
    'y': 100,
  }
  label = pyglet.text.Label(text_buf.get(), **text_opts)
  label.draw()


@win.event
def on_key_press(symbol, modifiers):
  if symbol in pressed:
    print(f'already pressed {symbol}')
  elif symbol not in KEYS:
    print(f'no longer pressing {symbol}')
    pressed.discard(symbol)
  else:
    pressed.add(symbol)


def update(dt):
  print(dt)

  if KEYS[KEY.A]:
    text_buf.input('a')


text_buf = TextBuffer()
text_buf.input('root@pentagon01 # ')
 
fps = 30.0
pyglet.clock.schedule_interval(update, 1 / fps)
pyglet.app.run()
