import pygame
from game_object import GameObject


class Pipe(GameObject):
    def __init__(self, image, x, y, flipped=False):
        if flipped:
            image = pygame.transform.flip(image, False, True)

        self.image = image
        self.rect = self.image.get_rect(midleft=(x, y))

        self.speed = 5

    def update(self):
        self.rect.centerx -= self.speed

    def off_screen(self):
        return self.rect.right < -50