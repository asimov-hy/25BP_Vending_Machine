import pygame
from config import *

def load_assets():
    assets = {}
    assets['sprite'] = pygame.transform.scale(pygame.image.load("vm_sprite.png").convert_alpha(),
                                  (int(800 * VM_SCALE), int(600 * VM_SCALE)))
    assets['numpad'] = pygame.image.load("picture/cash/numpad.png").convert_alpha()
    assets['card'] = pygame.image.load("picture/cash/card.png").convert_alpha()
    return assets

def get_fonts():
    return {
        "default": pygame.font.SysFont(None, 24),
        "input": pygame.font.SysFont(None, 48)
    }