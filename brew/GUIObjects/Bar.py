import pygame


# ------------------------------------------- BAR ----------------------------------------------------------------------
class Bar(object):
    def __init__(self, screen, color, rect, direction=Direction.UP):
        self.color = color
        self.screen = screen
        self.rect = rect
        self.direction = direction
        self.value = None

    def draw(self):
        if self.value is None:  # if not initialized, draw empty rectange crossed
            # cross
            pygame.draw.line(self.screen, (255, 0, 0), (self.rect[0]+2, self.rect[1]+1),
                             (self.rect[0] + self.rect[2]-1, self.rect[1] + self.rect[3]-1), 1)
            pygame.draw.line(self.screen, (255, 0, 0), (self.rect[0]+2, self.rect[1] + self.rect[3]-1),
                             (self.rect[0] + self.rect[2]-1, self.rect[1]+1), 1)
            # rect
            pygame.draw.rect(self.screen, self.color, self.rect, 2)
        else:
            #pygame.draw.rect(self.screen, self.color, self.rect, 2)

            barWidth = self.value * self.rect[2] / 100.0
            barHeight = self.value * self.rect[3] / 100.0

            if self.direction == Direction.UP:
                bar = (self.rect[0], self.rect[1] + (self.rect[3] - barHeight), self.rect[2], barHeight)
            elif self.direction == Direction.DOWN:
                bar = (self.rect[0], self.rect[1], self.rect[2], barHeight)
            elif self.direction == Direction.LEFT:
                bar = (self.rect[0] + (self.rect[2] - barWidth), self.rect[1], barWidth, self.rect[3])
            elif self.direction == Direction.RIGHT:
                bar = (self.rect[0], self.rect[1], barWidth, self.rect[3])
            else:
                raise ValueError()
            pygame.draw.rect(self.screen, self.color, bar, 0)