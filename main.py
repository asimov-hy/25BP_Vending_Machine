import pygame
import sys
from assets import load_assets, get_fonts
from game_state import *
from handlers import payment_success
from config import *

pygame.init()

screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption("Vending Machine")
clock = pygame.time.Clock()

assets = load_assets()
fonts = get_fonts()

running = True

while running:
    window_width, window_height = screen.get_size()
    sprite = assets['sprite']
    sprite_rect = sprite.get_rect(center=(window_width // 2, window_height // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            DEBUG = not DEBUG

    screen.fill((0, 0, 0))
    screen.blit(sprite, sprite_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()