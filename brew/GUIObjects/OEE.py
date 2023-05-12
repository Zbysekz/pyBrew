import math
import random
from GUIObjects.CircleGraph import CircleGraph

class OEEGraph:
    def __init__(self, screen, position, color=None, size=1.0):

        self.screen = screen
        self.position = position
        self.color = color
        self.size = size

        radius = 200
        innerCirclePos = radius/2.2

        xOffset = math.cos(math.radians(30)) * innerCirclePos
        yOffset = math.sin(math.radians(30)) * innerCirclePos

        self.performanceCircle = CircleGraph(self.screen,self.position,color, radius, "Rychlost",segmented = True, cntSegments=50, segmentSpace=0.7,bottomText=True, textSize=27)
        self.availabilityCircle = CircleGraph(self.screen,(self.position[0],self.position[1]-yOffset*2),color,radius/3, "Dostupnost",segmented = True, cntSegments=40, segmentSpace=0.7)
        self.oeeCircle = CircleGraph(self.screen,(self.position[0]+xOffset,self.position[1]+yOffset),color,radius/3, "OEE",segmented = True, cntSegments=40, segmentSpace=0.7)
        self.qualityCircle = CircleGraph(self.screen,(self.position[0]-xOffset,self.position[1]+yOffset),color,radius/3 , "Kvalita",segmented = True, cntSegments=40, segmentSpace=0.7)


        self.performanceCircle.value = 0#random.randint(0, 100)
        self.availabilityCircle.value = 0#random.randint(0, 100)
        self.oeeCircle.value = 0#random.randint(0, 100)
        self.qualityCircle.value = 0#random.randint(0, 100)

    def draw(self):
        self.performanceCircle.draw()
        self.availabilityCircle.draw()
        self.oeeCircle.draw()
        self.qualityCircle.draw()
