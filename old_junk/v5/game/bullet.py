import pyglet
from . import physicalobject, resources


class Bullet(physicalobject.PhysicalObject):
    """Bullets fired by the player"""

    def __init__(self, *args, **kwargs):
        super(Bullet, self).__init__(resources.bullet_image, *args, **kwargs)
        self.scale = 1

        # Bullets shouldn't stick around forever
        pyglet.clock.schedule_once(self.die, 1000)

        # Flag as a bullet
        self.is_bullet = True

    def die(self, dt):
        self.dead = True

    def handle_collision_with(self, other_object):
        pass
