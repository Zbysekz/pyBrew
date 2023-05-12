import pygame
from enum import Enum
import math

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

# ------------------------------------------ ARROWS --------------------------------------------------------------------
class Arrows(object):

    def __init__(self, screen, direction, count, position, colorA, colorB):
        self.colBuffer = [colorA] * count
        self.count = count
        self.colorA = colorA
        self.colorB = colorB
        self.surface = screen
        self.direction = direction
        self.position = position
        self.animTmp = 0.0
        self.active = False

        self.NOT_ACTIVE_COL = (80,80,80)
        self.speed = 0.3

    def draw(self):
        if self.direction == Direction.UP:
            x = 0
            y = -1
        elif self.direction == Direction.DOWN:
            x = 0
            y = 1
        elif self.direction == Direction.LEFT:
            x = -1
            y = 0
        elif self.direction == Direction.RIGHT:
            x = 1
            y = 0

        for i in range(self.count):
            offset = i * 5
            self._drawArrow((x * offset + self.position[0], y * offset + self.position[1]), self.colBuffer[i])

    def _drawArrow(self, pos, color):  # draws one arrow
        if self.direction == Direction.UP:
            pygame.draw.line(self.surface, color, (pos[0] + 0, pos[1] + 10), (pos[0] + 10, pos[1] + 0))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 0), (pos[0] + 20, pos[1] + 10))
        elif self.direction == Direction.DOWN:
            pygame.draw.line(self.surface, color, (pos[0] + 0, pos[1] + 0), (pos[0] + 10, pos[1] + 10))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 10), (pos[0] + 20, pos[1] + 0))
        elif self.direction == Direction.LEFT:
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 0), (pos[0] + 0, pos[1] + 10))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 20), (pos[0] + 0, pos[1] + 10))
        elif self.direction == Direction.RIGHT:
            pygame.draw.line(self.surface, color, (pos[0] + 0, pos[1] + 0), (pos[0] + 10, pos[1] + 10))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 10), (pos[0] + 0, pos[1] + 20))

    def animate(self):
        # reverse(self.colBuffer)

        prev = (0, 0, 0)
        for i in range(len(self.colBuffer)):
            (self.colBuffer[i], prev) = (prev, self.colBuffer[i])  # swap them

        if not self.active:
            self.colBuffer[0] = self.NOT_ACTIVE_COL
            return
        diff = self.colorB[0] - self.colorA[0]
        blend1 = diff * abs(math.sin(self.animTmp)) + self.colorA[0]
        diff = self.colorB[1] - self.colorA[1]
        blend2 = diff * abs(math.sin(self.animTmp)) + self.colorA[1]
        diff = self.colorB[2] - self.colorA[2]
        blend3 = diff * abs(math.sin(self.animTmp)) + self.colorA[2]

        self.colBuffer[0] = (blend1, blend2, blend3)

        self.animTmp += self.speed
        if self.animTmp > math.pi:
            self.animTmp -= math.pi
