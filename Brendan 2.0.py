import pygame
import sys

# Initialize Pygame
pygame.init()

# Debug flag: set to True to draw button outlines for debugging
DEBUG = False

# Initial window size
initial_width, initial_height = 800, 600

# Create a resizable window
screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption("Centered VM Sprite with Button Grid and Item Icons")

# Load and scale the main sprite image
original_sprite = pygame.image.load("vm_sprite.png").convert_alpha()
SPRITE_SCALE = 1.1
scaled_width = int(original_sprite.get_width() * SPRITE_SCALE)
scaled_height = int(original_sprite.get_height() * SPRITE_SCALE)
sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))

# Determine the background color from the top-left pixel of the scaled sprite
bg_color = sprite.get_at((0, 0))

# List of item image file paths and their display names
stock_list = [
    "stock/chips.png",
    "stock/coffee.png",
    "stock/cola_can.png",
    "stock/lemonade.png",
    "stock/orange_juice.png",
    "stock/cola_bottle.png",
    "stock/sword.png",
    "stock/mystery_potion.png",
    "stock/nuke.png",
    "stock/pokeball.png",
    "stock/mystery_box.png",
    "stock/small_doll.png",
    "stock/sold_out.png"  # Last image indicates sold out
]
item_names = [
    "Crisps",
    "Coffee",
    "Cola Can",
    "Lemonade",
    "Orange Juice",
    "Cola Bottle",
    "Sword",
    "Mystery Potion",
    "Nuke",
    "Pokeball",
    "Mystery Box",
    "Small Doll",
    "Sold Out"  # Name for sold out state
]

# Preload item images into surfaces
item_surfaces = [pygame.image.load(path).convert_alpha() for path in stock_list]

# Function to generate button rectangles based on sprite_rect each frame
def generate_buttons(sprite_rect, btn_size=68):
    x_offsets = [-144, -70, 4, 78]
    y_offsets = [-155, -80, -5]
    btns = []
    for y_off in y_offsets:
        for x_off in x_offsets:
            x = sprite_rect.centerx + x_off
            y = sprite_rect.centery + y_off
            btns.append(pygame.Rect(x, y, btn_size, btn_size))
    return btns

clock = pygame.time.Clock()
running = True

while running:
    # Always fetch the current window size and sprite_rect
    window_width, window_height = screen.get_size()
    sprite_rect = sprite.get_rect(center=(window_width // 2, window_height // 2))
    buttons = generate_buttons(sprite_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for idx, btn in enumerate(buttons):
                if btn.collidepoint(mouse_pos):
                    # If idx out of range or item is empty, use last (sold out)
                    name = item_names[idx] if idx < len(item_names) - 1 else item_names[-1]
                    print(f"{name} have been added to cart!")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            DEBUG = not DEBUG

    # Draw background and sprite
    screen.fill(bg_color)
    screen.blit(sprite, sprite_rect)

    # Blit item images centered in each button with margin
    margin_ratio = 0.8
    max_dim = int(68 * margin_ratio)
    for idx, btn in enumerate(buttons):
        # If idx < last index, show that item; otherwise show sold_out image
        if idx < len(item_surfaces) - 1:
            item_img = item_surfaces[idx]
        else:
            item_img = item_surfaces[-1]
        iw, ih = item_img.get_width(), item_img.get_height()
        scale_factor = min(max_dim / iw, max_dim / ih, 1)
        new_w = int(iw * scale_factor)
        new_h = int(ih * scale_factor)
        item_img_scaled = pygame.transform.smoothscale(item_img, (new_w, new_h)) if scale_factor < 1 else item_img
        item_rect = item_img_scaled.get_rect(center=btn.center)
        screen.blit(item_img_scaled, item_rect)

    # If debug mode is on, draw outlines around the button rectangles
    if DEBUG:
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]
        for idx, btn in enumerate(buttons):
            color = colors[idx % len(colors)]
            pygame.draw.rect(screen, color, btn, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
