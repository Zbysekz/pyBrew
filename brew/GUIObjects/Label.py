import pygame

class Label(object):
    default_color = (255, 255, 255)

    def __init__(self, screen, position, color=None, size=24, text = "---"):
        self.text = text

        if color is None:
            self.color = Label.default_color
        else:
            self.color = color
        self.position = position

        self.font = pygame.font.SysFont('ocraextended', size, bold=True)

        self.screen = screen

    def draw(self):
        # fw, fh = self.font.size(text)  # fw: font width,  fh: font height
        surface = self.font.render(self.text, True, self.color)

        self.screen.blit(surface, self.position)
