import pygame

def create_button_rect(center, width, height):
    rect = pygame.Rect(0, 0, width, height)
    rect.center = center
    return rect