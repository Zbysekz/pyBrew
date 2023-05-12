import pygame
import math
from pygame import gfxdraw

class CircleGraph:
    def __init__(self, screen, position, color=None, radius=200, title="", segmented = False, cntSegments=10,segmentSpace=0.9, bottomText = False, textSize = 14, valueLimit = 60):

        self.screen = screen
        self.position = position
        self.color = color
        self.color2=(255,255,255) # color of percent value
        self.radius = radius
        self.title = title
        self.bottomText = bottomText
        self.valueLimit = valueLimit
        self.segmented = segmented
        self.cntSegments = cntSegments
        self.segmentSpace = segmentSpace

        self.font = pygame.font.SysFont('ocraextended', textSize, bold=True)
        self.value = 0

    def draw(self):
        width = 100
        height = 100
        #pygame.draw.arc(self.screen, (255, 0, 0), (self.position[0]-width,self.position[1]-height,width,height), 0,math.pi/2, 10)

        if self.value is None:
            value = 0
        else:
            value = self.value

        val = -math.pi/2 + value/100*math.pi*2

        activeColor = (0,245,0) if self.valueLimit < value else (245,0,0)
        if not self.segmented:
            self.drawArc(self.screen, self.position[0], self.position[1], self.radius, 20,-math.pi/2, val,activeColor)
            self.drawArc(self.screen, self.position[0], self.position[1], self.radius, 10, val, math.pi*3/2, (152, 169, 166))
        else:
            self.drawArc(self.screen, self.position[0], self.position[1], self.radius, 20, -math.pi / 2,
                         math.pi * 3 / 2, (0, 84, 154))

            start = -math.pi/2
            stop = val
            stepW = self.segmentSpace * math.pi*2/self.cntSegments
            step = int(value * self.cntSegments / 100)
            for i in range(step):
                self.drawArc(self.screen, self.position[0], self.position[1], self.radius, 20, start, start+stepW,
                             activeColor)
                start = start + math.pi*2/self.cntSegments


        surface1 = self.font.render(self.title, True, self.color if self.valueLimit < value else (245,0,0))

        if self.value is None:
            surface2 = self.font.render("--- %", True, self.color2)
        else:
            surface2 = self.font.render(str(round(value))+ "%", True, self.color2)

        offsetY = self.radius*0.7 if self.bottomText else 0

        self.screen.blit(surface1, (self.position[0]-surface1.get_width()/2,self.position[1]-surface1.get_height()+offsetY))
        self.screen.blit(surface2,
                         (self.position[0] - surface2.get_width() / 2, self.position[1]+offsetY ))

    def drawArc(self,surface, x, y, r, th, start, stop, color):
        points_outer = []
        points_inner = []
        n = round(r * abs(stop - start) / 10)
        if n < 2:
            n = 2
        for i in range(n):
            delta = i / (n - 1)
            phi0 = start + (stop - start) * delta
            x0 = round(x + r * math.cos(phi0))
            y0 = round(y + r * math.sin(phi0))
            points_outer.append([x0, y0])
            phi1 = stop + (start - stop) * delta
            x1 = round(x + (r - th) * math.cos(phi1))
            y1 = round(y + (r - th) * math.sin(phi1))
            points_inner.append([x1, y1])
        points = points_outer + points_inner
        pygame.gfxdraw.aapolygon(surface, points, color)
        pygame.gfxdraw.filled_polygon(surface, points, color)