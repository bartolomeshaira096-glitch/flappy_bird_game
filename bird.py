import pygame
from game_object import GameObject


class Bird(GameObject):
    def __init__(self, frames):
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        super().__init__(self.image, 100, 512)

        self.gravity = 0.35
        self.movement = 0

    def flap(self):
        self.movement = 0
        self.movement -= 8

    def update(self):
        self.movement += self.gravity
        self.rect.centery += self.movement

    def animate(self):
        self.index = 0 if self.index == 2 else self.index + 1
        self.image = self.frames[self.index]

    def rotate(self):
        return pygame.transform.rotozoom(self.image, -self.movement * 3, 1)