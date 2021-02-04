import pyglet


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2


# Tell pyglet where to find the resources
pyglet.resource.path = ['assets']
pyglet.resource.reindex()

bullet_image = pyglet.resource.image("bullet.png")
center_image(bullet_image)


'''

# Load the three main resources and get them to draw centered
player_image = pyglet.resource.image("Ship@0.1x.png")
player_image # XXX rotate 90 degrees
player_image # XXX scale to 50x50
center_image(player_image)

bullet_image = pyglet.resource.image("bullet.png")
center_image(bullet_image)

asteroid_image = pyglet.resource.image("Poppy@0.1x.png")
center_image(asteroid_image)

# The engine flame should not be centered on the ship. Rather, it should be shown 
# behind it. To achieve this effect, we just set the anchor point outside the
# image bounds.
engine_image = pyglet.resource.image("Flame@0.1x.png")
engine_image.anchor_x = engine_image.width * 1.25
engine_image.anchor_y = engine_image.height / 2

# Load the bullet sound _without_ streaming so we can play it more than once at a time
bullet_sound = pyglet.resource.media("bullet.wav", streaming=False)
'''

# Available music
SONGS = {
  "stuff": pyglet.resource.media("theme_song.wav"),
}
