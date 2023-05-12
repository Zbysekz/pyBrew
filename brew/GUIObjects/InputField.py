import pygame
# ------------------------------------------- BAR ----------------------------------------------------------------------
class InputField(object):
    def __init__(self, screen, pos, size, units = '', decimals = 0):
        self.screen = screen
        self.focus = False
        self.string = "" # for editing
        self.units = units
        self.value = 0.0
        self.color = (255, 255, 255)
        self.size = size
        self.valFont = pygame.font.SysFont('calibri', self.size, bold=True)
        self.valUnits = pygame.font.SysFont('calibri', int(self.size/2), bold=False)
        h = self.valFont.get_height()
        self.rect = (*pos, h*2, h)
        self.decimals = decimals
        self.max = 100
        self.frameColor = (0, 0, 255)

    def draw(self):
        formatStr = "{:." + str(self.decimals) + "f}"
        valueText = formatStr.format(self.value)

        surfaceVal = self.valFont.render(self.string if self.focus else valueText, True,
                                         self.color)
        self.screen.blit(surfaceVal, (self.rect[0], self.rect[1]+2))

        surfaceUnits = self.valUnits.render(self.units, True, self.color)
        self.screen.blit(surfaceUnits, (self.rect[0]+ self.rect[2], self.rect[1] + 2))

        pygame.draw.rect(self.screen, (255, 0, 0) if self.focus else self.frameColor, self.rect, 1)
        #self.screen.blit(self.obj.surface, (self.rect.x,self.rect.y))

    def handleEvents(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_BACKSPACE:
                self.string = self.string[:-1]
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                formatStr = "{:." + str(self.decimals) + "f}"
                self.string = formatStr.format(self.value)
            elif e.type == pygame.KEYDOWN and (e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER):
                try:
                    self.value = float(self.string)
                    if self.value > self.max:
                        self.value = self.max
                except:
                    return
                self.focus = False
            elif e.type == pygame.KEYDOWN:
                self.string += e.unicode
    def gotFocus(self):
        self.focus = True

        formatStr = "{:." + str(self.decimals) + "f}"
        self.string = formatStr.format(self.value)