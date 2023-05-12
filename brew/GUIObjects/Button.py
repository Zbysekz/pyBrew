import pygame

# ------------------------------------------- BAR ----------------------------------------------------------------------
class Button(object):
    def __init__(self, manager, screen, caption, pos, callback, size = 80):
        self.screen = screen
        self.manager = manager
        self.pos = pos
        self.rect = (self.pos[0], self.pos[1], size, size/3)
        self.focus = False
        self.caption = caption
        self.color = (255, 255, 255)
        self.size = size
        self.valFont = pygame.font.SysFont('ocraextended', int(self.size/5), bold=False)

        self.checked = False
        self.mouseClick = callback

    def draw(self):
        surfaceVal = self.valFont.render(self.caption, True,
                                         self.color)
        self.screen.blit(surfaceVal, (self.rect[0]+self.rect[2]/2 - surfaceVal.get_width()/2, self.rect[1]+self.rect[3]/2- surfaceVal.get_height()/2))

        pygame.draw.rect(self.screen, (0, 0, 255),  self.rect, 1)

