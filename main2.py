import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1250, 500
window = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
GREEN = (0, 255, 0)

START_SCREEN = 0
PLAYING = 1
GAME_CLEAR = 2
state = START_SCREEN

camera_x = 0
CAMERA_MARGIN = 300

# === 画像の読み込み ===
background = pygame.image.load("pygame/img/sky.jpg")
background = pygame.transform.scale(background, (WIDTH * 2, HEIGHT))

start_bg = pygame.image.load("pygame/img/qingi-kongto-haini-baii-yun.jpg")
start_bg = pygame.transform.scale(start_bg, (WIDTH, HEIGHT))

clear_bg = pygame.image.load("pygame/img/IMG_6556.jpg")
clear_bg = pygame.transform.scale(clear_bg, (WIDTH, HEIGHT))

mario_img = pygame.image.load("pygame/img/IMG_3174.jpg")
mario_img = pygame.transform.scale(mario_img, (60, 40))

goomba_img = pygame.image.load("pygame/img/IMG_6268.JPG")
goomba_img = pygame.transform.scale(goomba_img, (40, 40))

def init_game():
    global mario, goombas, goomba_speeds, game_clear, on_ground, mario_velocity_y
    mario = pygame.Rect(50, HEIGHT - 40, 40, 40)

    goombas = [
        pygame.Rect(600, HEIGHT - 40, 40, 40),
        pygame.Rect(800, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
        pygame.Rect(1300, HEIGHT - 40, 40, 40),
    ]
    goomba_speeds = [50, -15, 10,10,50,20,2,10,10,1,10]

    game_clear = False
    on_ground = True
    mario_velocity_y = 0

obstacles = [

    pygame.Rect(900, HEIGHT - 150, 50, 50),
]

goal = pygame.Rect(2000, HEIGHT - 150, 20, 150)

init_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == START_SCREEN and event.key == pygame.K_RETURN:
                state = PLAYING
                init_game()
            elif state == GAME_CLEAR and event.key == pygame.K_RETURN:
                running = False

    if state == START_SCREEN:
        window.blit(start_bg, (0, 0))
        font = pygame.font.SysFont(None, 60)
        text = font.render("Press ENTER to Start", True, BLACK)
        window.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))

    elif state == PLAYING:
        max_scroll = background.get_width() - WIDTH
        scroll_x = min(max(camera_x, 0), max_scroll)
        window.blit(background, (-scroll_x, 0))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and mario.left > 0:
            mario.x -= 5
        if keys[pygame.K_RIGHT]:
            mario.x += 5

        if keys[pygame.K_SPACE] and on_ground:
            mario_velocity_y = -15
            on_ground = False

        mario_velocity_y += 0.5
        mario.y += mario_velocity_y

        if mario.y >= HEIGHT - mario.height:
            mario.y = HEIGHT - mario.height
            on_ground = True
            mario_velocity_y = 0

        if mario.x > CAMERA_MARGIN + camera_x:
            camera_x = mario.x - CAMERA_MARGIN
        elif mario.x < camera_x + CAMERA_MARGIN:
            camera_x = mario.x - CAMERA_MARGIN

        for obstacle in obstacles:
            pygame.draw.rect(window, BLACK, (obstacle.x - scroll_x, obstacle.y, obstacle.width, obstacle.height))
            if mario.colliderect(obstacle):
                if mario_velocity_y > 0 and mario.bottom >= obstacle.top and mario.top < obstacle.top:
                    mario.y = obstacle.top - mario.height
                    on_ground = True
                    mario_velocity_y = 0

        for i, goomba in enumerate(goombas):
            goomba.x += goomba_speeds[i]
            if goomba.left < 0 or goomba.right > 2200:
                goomba_speeds[i] *= -1
            window.blit(goomba_img, (goomba.x - scroll_x, goomba.y))
            if mario.colliderect(goomba):
                init_game()

        if mario.colliderect(goal):
            state = GAME_CLEAR

        window.blit(mario_img, (mario.x - scroll_x, mario.y))
        pygame.draw.rect(window, GRAY, (goal.x - scroll_x, goal.y, goal.width, goal.height))

    elif state == GAME_CLEAR:
        window.blit(clear_bg, (0, 0))
        font = pygame.font.SysFont(None, 60)
        text = font.render("Game Clear!", True, GREEN)
        window.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
