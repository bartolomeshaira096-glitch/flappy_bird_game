import pygame, sys, random

class GameObject:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        pass


class Bird(GameObject):
    def __init__(self, frames):
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        super().__init__(self.image, 100, 512)
        self.gravity = 0.25
        self.movement = 0

    def flap(self):
        self.movement = -12

    def update(self):
        self.movement += self.gravity
        self.rect.centery += self.movement

    def animate(self):
        self.index = (self.index + 1) % len(self.frames)
        self.image = self.frames[self.index]

    def rotate(self):
        return pygame.transform.rotozoom(self.image, -self.movement * 3, 1)


class Pipe(GameObject):
    def __init__(self, image, x, y, flipped=False):
        if flipped:
            image = pygame.transform.flip(image, False, True)
        super().__init__(image, x, y)
        self.speed = 5

    def update(self):
        self.rect.centerx -= self.speed

    def off_screen(self):
        return self.rect.right < -50


class Game:
    def __init__(self):
        pygame.init()
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

        pipe_img = pygame.transform.scale2x(
            pygame.image.load("assets/pipe-green.png")
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
        self.pipe_img = pipe_img
        self.pipes = []
        self.floor_x = 0

    def create_pipe(self):
        height = random.choice([400, 600, 800])
        bottom = Pipe(self.pipe_img, 700, height)
        top = Pipe(self.pipe_img, 700, height - 300, flipped=True)
        return bottom, top

    def check_collision(self):
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
                self.can_score = False
            if pipe.rect.centerx < 0:
                self.can_score = True

    def draw_pipes(self):
        for pipe in self.pipes:
            pipe.draw(self.screen)

    def reset_game(self):
        self.pipes.clear()
        self.bird.rect.center = (100, 512)
        self.bird.movement = 0
        self.score = 0
        self.game_active = True

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_active:
                        self.bird.flap()
                    if event.key == pygame.K_SPACE and not self.game_active:
                        self.reset_game()

                if event.type == pygame.USEREVENT:
                    self.pipes.extend(self.create_pipe())

            self.screen.blit(self.bg, (0, 0))

            if self.game_active:
                self.bird.update()
                self.screen.blit(self.bird.rotate(), self.bird.rect)

                self.pipes = [p for p in self.pipes if not p.off_screen()]
                for pipe in self.pipes:
                    pipe.update()

                self.draw_pipes()

                self.game_active = self.check_collision()
                self.update_score()

            self.floor_x -= 1
            self.screen.blit(self.floor, (self.floor_x, 900))
            self.screen.blit(self.floor, (self.floor_x + 576, 900))

            if self.floor_x <= -576:
                self.floor_x = 0

            pygame.display.update()
            self.clock.tick(120)

