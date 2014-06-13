__author__ = 'Ecialo'
from cocos.particle import ParticleSystem, Color
from cocos.euclid import Point2


class Advanced_Emitter(ParticleSystem):

    surface = None

    def add_to_surface(self, pos):
        self.position = pos
        self.auto_remove_on_finish = True
        self.surface.add(self, z=3)


class Sparkles(Advanced_Emitter):
    # angle
    angle = 90.0
    angle_var = 360.0

    # total particle
    total_particles = 50

    # duration
    duration = 0.05

    # gravity
    gravity = Point2(0,-90)

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # speed of particles
    speed = 100.0
    speed_var = 50.0

    # emitter variable position
    pos_var = Point2(0,0)

    # life of particles
    life = 0.5
    life_var = 0.3

    # emits per frame
    emission_rate = total_particles / duration

    # color of particles
    start_color = Color(1.0, 1.0, 0.85, 1.0)
    start_color_var = Color(0.0, 0.0, 0.0, 0.0)
    end_color = Color(1.0, 1.0, 0.85, 0.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # size, in pixels
    size = 5.0
    size_var = 2.0

    # blend additive
    blend_additive = False

    # color modulate
    color_modulate = True


class Blood(Advanced_Emitter):
    # angle
    angle = -90.0
    angle_var = 15.0

    # total particle
    total_particles = 20

    # duration
    duration = 0.1

    # gravity
    gravity = Point2(0,-90)

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # speed of particles
    speed = 80.0
    speed_var = 70.0

    # emitter variable position
    pos_var = Point2(0,0)

    # life of particles
    life = 0.8
    life_var = 0.5

    # emits per frame
    emission_rate = total_particles / duration

    # color of particles
    start_color = Color(1.0, 0.0, 0.0, 1.0)
    start_color_var = Color(0.0, 0.0, 0.0, 0.0)
    end_color = Color(1.0, 0.0, 0.0, 0.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # size, in pixels
    size = 4.0
    size_var = 1.0

    # blend additive
    blend_additive = False

    # color modulate
    color_modulate = True