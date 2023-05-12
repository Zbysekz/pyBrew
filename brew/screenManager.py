from mainScreen import cMainScreen
import pygame
from Logger import Log
from GUIObjects import InputField, Checkbox, Button

class cScreenManager:

    def __init__(self, pyScreen):

        self.screens = [cMainScreen(self, pyScreen)]

        self.fontBig = pygame.font.SysFont('mono', 30, bold=True)
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.fontSmall = pygame.font.SysFont('mono', 15, bold=False)

        self.activeScreenPtr = 0
        self.activeScreen = self.screens[self.activeScreenPtr] # default screen


        self.dataContainer = {} # container for data that we want to pass between main script and screens

        self.dataContainer["outputs"] = 0
        self.dataContainer["sp_reached"] = False  # aux variable - determining if we reached SP in current step

    def draw(self):
        #self.activeScreen.drawBackground()
        self.activeScreen.draw()

    def animate(self):
        self.activeScreen.animate()

    def updateValues(self): # slow value update event
        self.activeScreen.updateValues()

    def handleEvents(self, events):
        for name, obj in self.activeScreen.objects.items():
            if type(obj) == InputField:
                if not obj.focus:
                    for e in events:
                        if e.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(obj.rect).collidepoint(e.pos):
                            # deactivate all other focuses
                            for _, obj2 in self.activeScreen.objects.items():
                                if hasattr(obj2, 'focus'):
                                    obj2.focus = False
                            #print(str(name) + "got focus!")
                            obj.gotFocus()
                            break
                if obj.focus:
                    obj.handleEvents(events)
            if type(obj) in [Checkbox, Button]:
                for e in events:
                    if e.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(obj.rect).collidepoint(e.pos):
                        obj.mouseClick()

    def SetScreen(self, screenNo):
        if 0 <= screenNo < len(self.screens):
            self.activeScreenPtr = screenNo
            self.activeScreen = self.screens[self.activeScreenPtr]

    def NextScreen(self):
        self.activeScreenPtr += 1
        if self.activeScreenPtr >= len(self.screens):
            self.activeScreenPtr = 0
        self.activeScreen = self.screens[self.activeScreenPtr]
    def ResetStateMachine(self):
        self.dataContainer["stateMachine_status"] = 0

        for i in range(5):
            self.dataContainer['aut_remTime'+str(i)] = None