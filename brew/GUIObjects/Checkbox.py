import pygame


# ------------------------------------------- BAR ----------------------------------------------------------------------
class Checkbox(object):
    def __init__(self, screen, caption, pos, size=20):
        self.screen = screen
        self.pos = pos
        self.boxSize = 40
        self.rect = (self.pos[0], self.pos[1], self.boxSize, self.boxSize)
        self.focus = False
        self.caption = caption
        self.color = (255, 255, 255)
        self.size = size
        self.valFont = pygame.font.SysFont('ocraextended', self.size, bold=True)

        self.checked = False

    def draw(self):
        if self.caption != "":
            surfaceCaption = self.valFont.render(self.caption, True,
                                                 self.color)
            captionOffset_w = surfaceCaption.get_width() + 10
            captionOffset_h = ((surfaceCaption.get_height() - self.rect[2]) / 2)
            self.screen.blit(surfaceCaption, (self.pos[0] - captionOffset_w, self.pos[1]-captionOffset_h))

        pygame.draw.rect(self.screen, (0, 0, 255),
                         (self.rect[0], self.rect[1], self.rect[2], self.rect[3]), 1)
        pygame.draw.circle(self.screen, (255, 0, 0) if self.checked else (0, 50, 180),
                           (self.rect[0] + int(self.boxSize/2), self.rect[1] + int(self.boxSize/2)), int(self.boxSize/3))

    def mouseClick(self):
        self.checked = not self.checked
