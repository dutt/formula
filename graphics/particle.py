# from https://bitbucket.org/BigYellowCactus/particlegame

import itertools
import math

import numpy
import pygame
import pygame.surfarray as surfarray
from pygame.locals import *

colors = pygame.color.THECOLORS


def memoize(function):
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv

    return wrapper


@memoize
def makecircle(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2), 0, 8)
    surf.set_palette(((0, 0, 0), color))

    axis = abs(numpy.arange(radius * 2) - (radius - 0.5)).astype(int) ** 2
    mask = numpy.sqrt(axis[numpy.newaxis, :] + axis[:, numpy.newaxis])
    mask = numpy.less(mask, radius).astype(int) ** 2

    surfarray.blit_array(surf, mask)
    surf.set_colorkey(0, RLEACCEL)

    return surf.convert()


def ascending(speed):
    def _ascending(particle):
        particle.y -= speed

    return _ascending


def kill_at(max_x, max_y):
    def _kill_at(particle):
        if particle.x < -max_x or particle.x > max_x or particle.y < -max_y or particle.y > max_y:
            particle.alive = 0

    return _kill_at


def age(amount):
    def _age(particle):
        particle.alive += amount

    return _age


def translate_x(threshold):
    def _translate_x(particle):
        if particle.x >= threshold:
            particle.x = 0

    return _translate_x


def fan_out(modifier):
    def _fan_out(particle):
        d = particle.alive / modifier
        d += 1
        particle.x += numpy.random.randint(-d, d + 1)

    return _fan_out


def wind(direction, strength):
    def _wind(particle):
        if strength > 99 or numpy.random.randint(0, 101) < strength:
            particle.x += direction

    return _wind


def grow(amount):
    def _grow(particle):
        if numpy.random.randint(0, 101) < particle.alive / 20:
            particle.size += amount

    return _grow


def sinus(amount, speed):
    def _sinus(particle):
        particle.y = math.cos(particle.alive / speed) * amount

    return _sinus


class Particle:
    def __init__(self, col, size, *strategies):
        self.x, self.y = 0, 0
        self.col = col
        self.alive = 1
        self.strategies = strategies
        self.size = size

    def move(self):
        for s in self.strategies:
            s(self)
        if self.alive > 0:
            return self


def rain_machine(total_level_width, total_level_height):
    cm = ((50, 100, 120), (100, 100, 100))

    behaviour = (
        ascending(-6),
        wind(4, 80),
        translate_x(total_level_width),
        kill_at(total_level_width, total_level_height),
    )

    def create():
        if numpy.random.randint(100) < 50:
            c = cm[numpy.random.choice(range(len(cm)))]
            p = Particle(c, 1, *behaviour)
            p.x = numpy.random.randint(0, total_level_width)
            yield p

    while True:
        yield create()


def wind_machine(total_level_width, total_level_height):
    cm = [colors["white"]]

    def create():
        if numpy.random.randint(1000) < 15:
            y = numpy.random.randint(0, total_level_height)
            behaviour = (
                age(1),
                sinus(4, 12.0),
                wind(5, 100),
                kill_at(total_level_width, total_level_height),
                ascending(-y),
            )
            for x in range(65):
                c = cm[numpy.random.choice(range(len(cm)))]
                p = Particle(c, 2, *behaviour)
                p.y = y
                p.alive = 50 - x * 3
                p.x = -x * 3
                yield p

    while True:
        yield create()


def smoke_machine(total_level_width, total_level_height):
    cm = [colors["grey"], colors["darkgrey"], colors["gray52"]]

    behaviour = (
        age(1),
        ascending(1),
        fan_out(400),
        wind(1, 15),
        grow(0.5),
        kill_at(total_level_width, total_level_height / 2),
    )

    def create():
        for _ in range(numpy.random.choice([0, 0, 0, 0, 0, 0, 0, 1, 2, 3])):
            c = cm[numpy.random.choice(range(len(cm)))]
            p = Particle(c, numpy.random.randint(10, 16), *behaviour)
            yield p

    while True:
        yield create()


class Emitter(object):
    def __init__(self, pos=(0, 0), *facs):
        self.particles = []
        self.pos = pos
        self.factories = []
        for f in facs:
            self.add_factory(f)

    def add_factory(self, factory, pre_fill=300):
        self.factories.append(factory)
        tmp = []
        for _ in range(pre_fill):
            n = next(factory)
            tmp.extend(n)
            for p in tmp:
                p.move()
        self.particles.extend(tmp)

    def update(self):
        tmp = itertools.chain(self.particles, *map(next, self.factories))
        tmp = itertools.ifilter(Particle.move, tmp)  # side effect!
        self.particles = list(tmp)

    def draw(self, screen, position_translater_func):
        x, y = position_translater_func(self.pos)
        for p in self.particles:
            target_pos = p.x + x, p.y + y
            circle = makecircle(int(p.size), p.col)
            screen.blit(circle, target_pos)
