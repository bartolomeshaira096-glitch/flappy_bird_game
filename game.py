import pygame
import random
import sys
import os
from bird import Bird
from pipe import Pipe


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

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
            pygame.image.load("assets/pipe-green.png").convert_alpha()
        )

        self.message_img = pygame.transform.scale2x(
            pygame.image.load("assets/message.png").convert_alpha()
        )

        bird_down = pygame.transform.scale2x(
            pygame.image.load("assets/bluebird-downflap.png").convert_alpha()
        )

        bird_mid = pygame.transform.scale2x(
            pygame.image.load("assets/bluebird-midflap.png").convert_alpha()
        )

        bird_up = pygame.transform.scale2x(
            pygame.image.load("assets/bluebird-upflap.png").convert_alpha()
        )

        self.bird = Bird([bird_down, bird_mid, bird_up])

        self.pipes = []

        self.floor_x = 0

        self.SPAWNPIPE = pygame.USEREVENT
        pygame.time.set_timer(self.SPAWNPIPE, 1200)

        self.BIRDFLAP = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BIRDFLAP, 200)

        base_path = os.path.dirname(__file__)

        self.flap_sound = pygame.mixer.Sound(
            os.path.join(base_path, "sound", "sound_sfx_wing.wav")
        )

        self.hit_sound = pygame.mixer.Sound(
            os.path.join(base_path, "sound", "sound_sfx_hit.wav")
        )

        self.score_sound = pygame.mixer.Sound(
            os.path.join(base_path, "sound", "sound_sfx_point.wav")
        )

        self.flap_sound.set_volume(0.5)
        self.hit_sound.set_volume(0.6)
        self.score_sound.set_volume(0.6)

    def create_pipe(self):
        gap = 250
        center_y = random.randint(300, 700)

        bottom_pipe = Pipe(
            self.pipe_img,
            700,
            center_y + gap // 2
        )

        top_pipe = Pipe(
            self.pipe_img,
            700,
            center_y - gap // 2,
            flipped=True
        )

        bottom_pipe.rect.midtop = (700, center_y + gap // 2)
        top_pipe.rect.midbottom = (700, center_y - gap // 2)

        return bottom_pipe, top_pipe

    def check_collision(self):
        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.rect):
                return False

        if self.bird.rect.top <= -100:
            return False

        if self.bird.rect.bottom >= 900:
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
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)

            high = font.render(f"High: {self.high_score}", True, (255, 255, 255))
            high_rect = high.get_rect(center=(288, 850))
            self.screen.blit(high, high_rect)

    def run(self):
        while self.game_state == "intro":

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.game_state = "playing"

            self.screen.blit(self.bg, (0, 0))
            msg_rect = self.message_img.get_rect(center=(288, 420))
            self.screen.blit(self.message_img, msg_rect)
            self.draw_floor()

            pygame.display.update()
            self.clock.tick(60)

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.game_active:
                        self.bird.flap()
                        self.flap_sound.play()

                    else:
                        self.reset_game()

                if event.type == self.SPAWNPIPE:
                    self.pipes.extend(self.create_pipe())

                if event.type == self.BIRDFLAP:
                    self.bird.animate()

            self.screen.blit(self.bg, (0, 0))

            if self.game_active:

                self.bird.update()
                self.screen.blit(self.bird.rotate(), self.bird.rect)

                collision = self.check_collision()

                if not collision:
                    self.hit_sound.play()

                self.game_active = collision

                self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]

                for pipe in self.pipes:
                    pipe.update()
                    pipe.draw(self.screen)

                self.update_score()

            else:

                self.high_score = max(self.high_score, self.score)

                game_over = self.font.render(
                    "CLICK TO RESTART",
                    True,
                    (255, 255, 255)
                )

                self.screen.blit(game_over, (145, 450))

            self.floor_x -= 1

            if self.floor_x <= -576:
                self.floor_x = 0

            self.draw_floor()
            self.draw_score()

            pygame.display.update()
            self.clock.tick(60)