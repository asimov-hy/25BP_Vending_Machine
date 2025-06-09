import pygame
import sys

pygame.init()

DEBUG = 1
initial_width, initial_height = 800, 600
screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption("Vending Machine Items Only")

VM_SCALE = 0.54
ITEM_SCALE = 0.70

original_sprite = pygame.image.load("vm_sprite.png").convert_alpha()
scaled_width = int(original_sprite.get_width() * VM_SCALE)
scaled_height = int(original_sprite.get_height() * VM_SCALE)
sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
bg_color = sprite.get_at((0, 0))

stock_list = [
    "picture/chips.png", "picture/coffee.png", "picture/cola_can.png", "picture/lemonade.png",
    "picture/orange_juice.png", "picture/cola_bottle.png", "picture/sword.png", "picture/mystery_potion.png",
    "picture/nuke.png", "picture/pokeball.png", "picture/mystery_box.png", "picture/small_doll.png",
    "picture/sold_out.png"
]

item_names = [
    "Crisps", "Coffee", "Cola Can", "Lemonade", "Orange Juice", "Cola Bottle",
    "Sword", "Mystery Potion", "Nuke", "Pokeball", "Mystery Box", "Small Doll", "Sold Out"
]

item_surfaces = [pygame.image.load(path).convert_alpha() for path in stock_list]

row_offsets = [-205, -124, -45]
col_offsets = [-151, -76, -4, 66]

item_offsets = [(x, y) for y in row_offsets for x in col_offsets]

ui_buttons = {
    "numpad": ((161, -120), (1.5, 2.0)),
    "card": ((161, -21), (1.5, 1.0)),
    "cash": ((161, 65), (1.5, 1.6)),
    "dispenser": ((-33, 200), (5, 1.5))
}

ui_colors = {
    "numpad": (255, 200, 200),
    "card": (200, 255, 200),
    "cash": (200, 200, 255),
    "dispenser": (255, 255, 200)
}

clock = pygame.time.Clock()
running = True

while running:
    window_width, window_height = screen.get_size()
    sprite_rect = sprite.get_rect(center=(window_width // 2, window_height // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            DEBUG = not DEBUG
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            rel_x = mouse_x - sprite_rect.centerx
            rel_y = mouse_y - sprite_rect.centery
            print(f"Mouse clicked at relative position: ({rel_x}, {rel_y})")

    screen.fill(bg_color)
    screen.blit(sprite, sprite_rect)

    box_size = int(68 * ITEM_SCALE)
    for idx, (x_off, y_off) in enumerate(item_offsets):
        item_img = item_surfaces[idx] if idx < len(item_surfaces) - 1 else item_surfaces[-1]
        iw, ih = item_img.get_width(), item_img.get_height()
        scale_factor = min(box_size / iw, box_size / ih)
        new_w = int(iw * scale_factor)
        new_h = int(ih * scale_factor)
        item_img_scaled = pygame.transform.smoothscale(item_img, (new_w, new_h))
        box_center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
        box_rect = pygame.Rect(0, 0, box_size, box_size)
        box_rect.center = box_center
        item_rect = item_img_scaled.get_rect(center=box_rect.center)
        screen.blit(item_img_scaled, item_rect)

        if DEBUG:
            pygame.draw.rect(screen, (255, 100, 100), box_rect, 2)
            pygame.draw.rect(screen, (0, 200, 255), item_rect, 1)

    for name, ((x_off, y_off), (scale_w, scale_h)) in ui_buttons.items():
        base_size = 70 * ITEM_SCALE
        btn_width = int(base_size * scale_w)
        btn_height = int(base_size * scale_h)
        btn_center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.center = btn_center

        color = ui_colors.get(name, (255, 255, 255))
        pygame.draw.rect(screen, color, btn_rect, 2)  # Outline only

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
