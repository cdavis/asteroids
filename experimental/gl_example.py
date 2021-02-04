#!/usr/bin/env python3

import pyglet
from pyglet.gl import *


KEY = pyglet.window.key


win = pyglet.window.Window(fullscreen=True)
FRAME = 0

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



def update(dt):
  print(dt)

  if 


text_buf = TextBuffer()
text_buf.input('root@pentagon01 # ')
 
fps = 30.0
pyglet.clock.schedule_interval(update, 1 / fps)
pyglet.app.run()







# Trasho
'''
@win.event
def on_draw():
    win.clear()

    global FRAME
    FRAME += 1
    print(f'FRAME={FRAME}')

    t = FRAME % 10
    tf = t / 10

    glClear(GL_COLOR_BUFFER_BIT)
    low = (FRAME % 10) / 10
    glColor3d(low, low, 1.0)

    # create a line context
    glBegin(GL_LINES)

    # create a line, x,y
    glVertex2f(100.0, 100.0)
    glVertex2f(200.0, 300.0)

    glEnd()
'''


