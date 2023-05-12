import pygame
import math


class Value(object):
    default_color = (255, 255, 255)

    def __init__(self, screen, position, units, decimals=0, valueLimit=999999, colorLimit=(255, 0, 0),
                 color=None, size = 28,title="", units2="", timeFormat= False):
        self.value = None
        self.valueLimit = valueLimit
        if color is None:
            self.color = Value.default_color
        else:
            self.color = color
        self.colorLimit = colorLimit
        self.colorLimit_anim = colorLimit
        self.position = position

        self.valFont = pygame.font.SysFont('ocraextended', size, bold=True)
        self.unitsFont = pygame.font.SysFont('ocraextended', int(size-13), bold=True)

        self.screen = screen
        self.units = units
        self.units2 = units2
        self.animTmp = 0.0
        self.speed = 0.2
        self.decimals = decimals
        self.title = title
        self.timeFormat = timeFormat

    def draw(self):

        value = self.value
        decimals = self.decimals
        units = self.units
        valueLimit = self.valueLimit

        if self.value is not None:

            if self.timeFormat:
                hours = int(self.value//60)
                minutes = int(self.value % 60)
                valueText = str(hours) + ":{:02d}".format(minutes)
            else:
                # if > 1000, switch to higher order if units2 is not empty
                if value > 1000 and self.units2 != '':
                    value /= 1000
                    valueLimit /= 1000
                    decimals = 2
                    units = self.units2

                formatStr = "{:." + str(decimals) + "f}"
                valueText = formatStr.format(value)
        else:
            if self.timeFormat:
                valueText = "-:-"
            elif self.decimals > 1:
                valueText = "-." + '-' * self.decimals
            elif self.decimals > 0:
                valueText = "--." + '-' * self.decimals
            else:
                valueText = "--"

        titleOffset = 0
        if self.title != "":
            surfaceTitle = self.valFont.render(self.title, True, self.color)
            self.screen.blit(surfaceTitle, self.position)
            titleOffset = surfaceTitle.get_width()

        surfaceVal = self.valFont.render(valueText, True,
                                         self.color if value is None or value < valueLimit else self.colorLimit_anim)
        self.screen.blit(surfaceVal, (self.position[0] + titleOffset, self.position[1]))

        unitsVal = self.unitsFont.render(units, True,
                                         self.color if value is None or value < valueLimit else self.colorLimit_anim)
        self.screen.blit(unitsVal, (
        self.position[0] + surfaceVal.get_width() + titleOffset, self.position[1] + surfaceVal.get_height() - unitsVal.get_height()))

    def animate(self):

        self.colorLimit_anim = (
            self.colorLimit[0] * (1 - abs(math.sin(self.animTmp) / 3)), self.colorLimit[1], self.colorLimit[2])

        self.animTmp += self.speed
        if self.animTmp > math.pi:
            self.animTmp -= math.pi
