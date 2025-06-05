import sys
import os
import pygame
import random

pygame.init()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH = 2000

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("pygame")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GREEN = (100, 100, 100)
GOLD = (255, 215, 0)

player_img = pygame.image.load(resource_path("img/player.png"))
player_img = pygame.transform.scale(player_img, (40, 40))

enemy_img = pygame.image.load(resource_path("img/enemy.png"))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_y = 0
        self.on_ground = False
        self.jump_count = 0

    def update(self, blocks):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5

        if keys[pygame.K_SPACE]:
            if self.jump_count < 2:
                self.vel_y = -18
                self.jump_count += 1

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy = self.vel_y

        self.on_ground = False
        for block in blocks:
            if block.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            if block.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y > 0:
                    self.rect.bottom = block.top
                    self.on_ground = True
                    self.jump_count = 0
                    dy = 0
                elif self.vel_y < 0:
                    self.rect.top = block.bottom
                    dy = 0

        self.rect.x += dx
        self.rect.y += dy

    def draw(self, screen, offset_x):
        screen.blit(player_img, (self.rect.x - offset_x, self.rect.y))


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.direction = 1
        self.speed = random.randint(2, 6)
        self.change_direction_time = random.randint(100, 300)

    def update(self):
        self.rect.x += self.direction * self.speed
        self.change_direction_time -= 1

        if self.change_direction_time <= 0:
            self.direction *= -1
            self.speed = random.randint(2, 6)
            self.change_direction_time = random.randint(100, 300)

        if self.rect.left < 0 or self.rect.right > MAP_WIDTH:
            self.direction *= -1
            self.speed = random.randint(2, 6)

    def draw(self, screen, offset_x):
        screen.blit(enemy_img, (self.rect.x - offset_x, self.rect.y))


class Spike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, screen, offset_x):
        pygame.draw.polygon(screen, BLACK, [
            (self.rect.left - offset_x, self.rect.bottom),
            (self.rect.centerx - offset_x, self.rect.top),
            (self.rect.right - offset_x, self.rect.bottom)
        ])


class PopUpSpike:
    def __init__(self, x, y):
        self.base_y = y
        self.rect = pygame.Rect(x, y + 20, 40, 20)
        self.active = False
        self.timer = 0

    def update(self, player):
        distance = abs(player.rect.centerx - self.rect.centerx)
        if distance < 70:
            self.active = True
            self.timer += 1
        else:
            self.active = False
            self.timer = 0

        if self.active:
            if self.timer < 30:
                self.rect.y = self.base_y + 10 - int(500 * (self.timer / 30))
            else:
                self.rect.y = self.base_y - 20
        else:
            self.rect.y = self.base_y + 20

    def draw(self, screen, offset_x):
        pygame.draw.polygon(screen, BLACK, [
            (self.rect.left - offset_x, self.rect.bottom),
            (self.rect.centerx - offset_x, self.rect.top),
            (self.rect.right - offset_x, self.rect.bottom)
        ])


class MovingSpike(Spike):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * 3
        if self.rect.left < 0 or self.rect.right > MAP_WIDTH:
            self.direction *= -1


class FallingBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 20)
        self.falling = False
        self.fall_speed = random.randint(5, 10)

    def update(self, player):
        if self.rect.colliderect(player.rect) and not self.falling:
            self.falling = True
        if self.falling:
            self.rect.y += self.fall_speed

    def draw(self, screen, offset_x):
        pygame.draw.rect(screen, GREEN, (self.rect.x - offset_x, self.rect.y, self.rect.width, self.rect.height))


def create_level():
    blocks = []
    for i in range(0, MAP_WIDTH, 50):
        blocks.append(pygame.Rect(i, 550, 50, 50))
    blocks.append(pygame.Rect(300, 450, 100, 20))
    blocks.append(pygame.Rect(600, 400, 100, 20))
    blocks.append(pygame.Rect(1300, 350, 100, 20))
    return blocks


player = Player(100, 300)
blocks = create_level()

enemies = [Enemy(x, 510) for x in (1200, 1400, 1600)]
spikes = [Spike(x, 510) for x in (700, 800, 1000)]
moving_spikes = [MovingSpike(1600, 510)]

falling_blocks = [
    FallingBlock(900, 300),
    FallingBlock(1100, 250),
    FallingBlock(1300, 200),
    FallingBlock(1500, 150)
]

popup_spikes = [PopUpSpike(1000, 510), PopUpSpike(1700, 510)]

camera_x = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    player.update(blocks)

    for pspike in popup_spikes:
        pspike.update(player)

    for enemy in enemies:
        enemy.update()
    for fb in falling_blocks:
        fb.update(player)
    for mspike in moving_spikes:
        mspike.update()

    for pspike in popup_spikes:
        if player.rect.colliderect(pspike.rect):
            print("飛び出すスパイクで死亡！")
            pygame.quit()
            sys.exit()

    camera_x = int(player.rect.centerx - SCREEN_WIDTH * 0.35)
    camera_x = max(0, min(camera_x, MAP_WIDTH - SCREEN_WIDTH))

    for spike in spikes + moving_spikes:
        if player.rect.colliderect(spike.rect):
            print("スパイクで死亡！")
            pygame.quit()
            sys.exit()
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            print("敵にやられた！")
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)
    for block in blocks:
        pygame.draw.rect(screen, GRAY, (block.x - camera_x, block.y, block.width, block.height))
    for spike in spikes:
        spike.draw(screen, camera_x)
    for mspike in moving_spikes:
        mspike.draw(screen, camera_x)
    for fb in falling_blocks:
        fb.draw(screen, camera_x)
    for enemy in enemies:
        enemy.draw(screen, camera_x)
    player.draw(screen, camera_x)
    for pspike in popup_spikes:
        pspike.draw(screen, camera_x)

    goal = pygame.Rect(1900, 500, 50, 50)
    pygame.draw.rect(screen, GOLD, (goal.x - camera_x, goal.y, goal.width, goal.height))
    if player.rect.colliderect(goal):
        font = pygame.font.SysFont("meiryo", 60)
        message = font.render("ゲームクリア！おめでとう！", True, (0, 0, 0))
        screen.fill(WHITE)
        screen.blit(message, ((SCREEN_WIDTH - message.get_width()) // 2, SCREEN_HEIGHT // 2 - 50))
        pygame.display.update()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    time_elapsed = pygame.time.get_ticks() // 10
    for enemy in enemies:
        enemy.speed = min(11, 3 + time_elapsed // 5)
    for fb in falling_blocks:
        fb.fall_speed = min(20, 5 + time_elapsed // 20)

    pygame.display.update()
    clock.tick(60)
