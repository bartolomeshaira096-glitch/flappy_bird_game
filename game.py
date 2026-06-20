import pygame
import random
import sys
import os
from bird import Bird
from pipe import Pipe


class Game:
    def __init__(self):
        pygame.init()

        self.game_state = "intro"
        self.font = pygame.font.Font("04B_19.ttf", 40)

        self.screen = pygame.display.set_mode((576, 1024))
        self.clock = pygame.time.Clock()

        self.game_active = True
        self.score = 0
        self.high_score = 0
        self.can_score = True

        self.bg = pygame.transform.scale2x(
            pygame.image.load("assets/background-day.png").convert()
        )

        self.floor = pygame.transform.scale2x(
            pygame.image.load("assets/base.png").convert()
        )

        self.pipe_img = pygame.transform.scale2x(
            pygame.image.load("assets/pipe-green.png")
        )

        bird_down = pygame.transform.scale2x(pygame.image.load("assets/bluebird-downflap.png").convert_alpha())
        bird_mid = pygame.transform.scale2x(pygame.image.load("assets/bluebird-midflap.png").convert_alpha())
        bird_up = pygame.transform.scale2x(pygame.image.load("assets/bluebird-upflap.png").convert_alpha())

        self.bird = Bird([bird_down, bird_mid, bird_up])

        self.pipes = []
        self.floor_x = 0

        self.SPAWNPIPE = pygame.USEREVENT
        pygame.time.set_timer(self.SPAWNPIPE, 1200)

        self.BIRDFLAP = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BIRDFLAP, 200)

        base_path = os.path.dirname(__file__)
        self.flap_sound = pygame.mixer.Sound(os.path.join(base_path, "sound", "sound_sfx_wing.wav"))
        self.hit_sound = pygame.mixer.Sound(os.path.join(base_path, "sound", "sound_sfx_hit.wav"))
        self.score_sound = pygame.mixer.Sound(os.path.join(base_path, "sound", "sound_sfx_point.wav"))

    def create_pipe(self):
        gap = 300
        center_y = random.randint(300, 700)

        top_pipe = Pipe(
            self.pipe_img,
            700,
            center_y - gap // 2,
            flipped=True
        )

        bottom_pipe = Pipe(
            self.pipe_img,
            700,
            center_y + gap // 2,
        )

        return bottom_pipe, top_pipe

    def check_collision(self):
        self.hit_sound.play()
        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.rect):
                return False

        if self.bird.rect.top <= -100 or self.bird.rect.bottom >= 900:
            return False

        return True

    def update_score(self):
        for pipe in self.pipes:
            if 95 < pipe.rect.centerx < 105 and self.can_score:
                self.score += 1
                self.score_sound.play()
                self.can_score = False

            if pipe.rect.centerx < 0:
                self.can_score = True

    def reset_game(self):
        self.pipes.clear()
        self.bird.rect.center = (100, 512)
        self.bird.movement = 0
        self.bird.index = 0
        self.bird.image = self.bird.frames[0]
        self.score = 0
        self.can_score = True
        self.game_active = True

    def draw_floor(self):
        self.screen.blit(self.floor, (self.floor_x, 900))
        self.screen.blit(self.floor, (self.floor_x + 576, 900))

    def draw_score(self):
        font = pygame.font.Font("04B_19.ttf", 40)

        if self.game_active:
            score_surface = font.render(str(int(self.score)), True, (255, 255, 255))
            self.screen.blit(score_surface, (288, 100))
        else:
            score_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_surface, (250, 100))

            high = font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(high, (200, 850))

    def run(self):
        if self.game_state == "intro":
            self.screen.blit(self.bg, (0, 0))

        title = self.font.render("FLAPPY BIRD", True, (255, 255, 255))
        sub = self.font.render("CLICK TO START", True, (255, 255, 255))

        self.screen.blit(title, (150, 300))
        self.screen.blit(sub, (140, 400))

        if pygame.mouse.get_pressed()[0]:
            self.game_state = "playing"

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.game_active:
                        self.bird.flap()
                        self.flap_sound.play()

                if event.type == self.SPAWNPIPE:
                    self.pipes.extend(self.create_pipe())

                if event.type == self.BIRDFLAP:
                    self.bird.animate()

            self.screen.blit(self.bg, (0, 0))

            if self.game_active:
                self.bird.update()
                self.screen.blit(self.bird.rotate(), self.bird.rect)
                if not self.check_collision():
                    self.hit_sound.play()
                    self.game_active = False

                self.pipes = [p for p in self.pipes if not p.off_screen()]
                for pipe in self.pipes:
                    pipe.update()
                    pipe.draw(self.screen)

                self.game_active = self.check_collision()
                self.update_score()

            else:
                self.high_score = max(self.high_score, self.score)

            self.floor_x -= 1
            if self.floor_x <= -576:
                self.floor_x = 0

            self.draw_floor()
            self.draw_score()

            pygame.display.update()
            self.clock.tick(60)