import pygame
import sys

# ---------------------------- Initialization ----------------------------
pygame.init()

# debug options
DEBUG = 1  # only controls outlines, not functionality
click_pos = False  # for console logging

# set up display
initial_width, initial_height = 800, 600
screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption("Vending Machine Items Only")

# ---------------------------- image variables ----------------------------

VM_SCALE = 0.54
ITEM_SCALE = 0.70

# Numpad grid configuration
NUMPAD_OFFSET = (500, -150)
NUMPAD_SCALE = 1

# Numpad grid layout
GRID_OFFSET = (-65, -60)
GRID_BUTTON_SIZE = 40
GRID_PADDING_X = 5
GRID_PADDING_Y = 8

# Clear/Enter button configuration
CLEAR_BUTTON_SIZE = (60, 30)
CLEAR_BUTTON_OFFSET = (0, GRID_BUTTON_SIZE * 3 + GRID_PADDING_Y + 17)
ENTER_BUTTON_SIZE = (60, 30)
ENTER_BUTTON_OFFSET = (CLEAR_BUTTON_SIZE[0] + GRID_PADDING_X + 10,
                       GRID_BUTTON_SIZE * 3 + GRID_PADDING_Y + 17)

# card reader config
CARDREADER_OFFSET = (375, 50)
CARDREADER_SCALE = 0.6

# card config
CARD_OFFSET = (375, 250)
CARD_SCALE = 0.7

# ---------------------------- font Variables ----------------------------

# Font for displaying messages
font = pygame.font.SysFont(None, 24)
input_font = pygame.font.SysFont(None, 48)

message_timer = 0  # frames remaining for timed messages (>0)
MESSAGE_DURATION = 180  # 3 seconds at 60 FPS

# active message; top of vending machine
active_message = ""  # message to display
# order message; on top of numpad
order_number = ""  # stores numpad input
payment_mesg = ""

# Selected item index for purchase
selected_item = None  # index of last item chosen
# Cloned (dispensed) items indices
cloned_items = []  # indices of items that were paid for and dispensed


# Payment success handler
def payment_success():
    global active_message, cloned_items, selected_item, valid_order, message_timer, payment_mesg
    active_message = "Payment complete"
    if selected_item is not None:
        cloned_items.append(selected_item)
    selected_item = None
    valid_order = 0  # reset validity after payment
    message_timer = MESSAGE_DURATION  # show payment complete for set duration
    payment_mesg = "..."


# ---------------------------- Load Sprites and Assets ----------------------------
original_sprite = pygame.image.load("vm_sprite.png").convert_alpha()
scaled_width = int(original_sprite.get_width() * VM_SCALE)
scaled_height = int(original_sprite.get_height() * VM_SCALE)
sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
bg_color = sprite.get_at((0, 0))

numpad_image = pygame.image.load("picture/cash/numpad.png").convert_alpha()
card_image_src = pygame.image.load("picture/cash/card.png").convert_alpha()  # card image to insert

numpad_visible = False
cardReader_visible = False  # toggle for card reader display

# ---------------------------- Stock Items ----------------------------
stock_list = [
    "picture/chips.png", "picture/coffee.png", "picture/cola_can.png", "picture/lemonade.png",
    "picture/orange_juice.png", "picture/cola_bottle.png", "picture/sword.png", "picture/mystery_potion.png",
    "picture/nuke.png", "picture/pokeball.png", "picture/mystery_box.png", "picture/small_doll.png",
    "picture/sold_out.png"
]
item_names = [
    "Crisps - $3500", "Coffee - $1500", "Cola Can - $1200", "Lemonade - $1300", "Orange Juice - $1500",
    "Cola Bottle - $2200", "Sword - $13000", "Mystery Potion - $30000", "Nuke - $100000", "Pokeball - $5000",
    "Mystery Box - $1000", "Small Doll - $50000", "Sold Out"
]
item_surfaces = [pygame.image.load(path).convert_alpha() for path in stock_list]

row_offsets = [-205, -124, -45]
col_offsets = [-151, -76, -4, 66]
item_offsets = [(x, y) for y in row_offsets for x in col_offsets]
BOX_SIZE = int(68 * ITEM_SCALE)

# ---------------------------- UI Buttons ----------------------------
ui_buttons = {
    "numpad": ((161, -120), (1.5, 2.0)),
    "cardreader_icon": ((161, -21), (1.5, 1.0)),
    "cash": ((161, 65), (1.5, 1.6)),
    "dispenser": ((-33, 200), (5, 1.5))
}
ui_colors = {
    "numpad": (255, 200, 200),
    "cardreader_icon": (200, 255, 200),
    "cash": (200, 200, 255),
    "dispenser": (255, 255, 200)
}

clock = pygame.time.Clock()
running = True
valid_order = 0

# ---------------------------- Game Loop ----------------------------

while running:
    # create vending machine sprite rect
    window_width, window_height = screen.get_size()
    sprite_rect = sprite.get_rect(center=(window_width // 2, window_height // 2))

    # Handle events
    for event in pygame.event.get():
        # quit event
        if event.type == pygame.QUIT:
            running = False

        # VIDEORESIZE is triggered when the window is resized
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # trigger debug mode when pressed D
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            DEBUG = not DEBUG

        # mouse click events
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            # UI toggles
            for name, ((x_off, y_off), (scale_w, scale_h)) in ui_buttons.items():
                base = 70 * ITEM_SCALE
                w = int(base * scale_w)
                h = int(base * scale_h)
                center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
                rect = pygame.Rect(0, 0, w, h)
                rect.center = center

                # if click position is within the button rect of the buttons
                if rect.collidepoint(mouse_x, mouse_y):
                    if name == "numpad":
                        numpad_visible = not numpad_visible
                        cardReader_visible = False
                    elif name == "cardreader_icon":
                        cardReader_visible = not cardReader_visible
                        numpad_visible = False

            # Item slot clicks
            for idx, (x_off, y_off) in enumerate(item_offsets[:12]):  # set up collision rects for first 12 items
                center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
                rect = pygame.Rect(0, 0, BOX_SIZE, BOX_SIZE)
                rect.center = center
                # check if the mouse click is within the item rect
                if rect.collidepoint(mouse_x, mouse_y):
                    selected_item = idx
                    valid_order = 0  # reset until confirmed by Enter
                    active_message = f"{idx + 1}: {item_names[idx]}"
                    message_timer = MESSAGE_DURATION

            # card payment chcker
            if cardReader_visible:
                # compute scaled card image rect
                cw = int(card_image_src.get_width() * CARD_SCALE)
                ch = int(card_image_src.get_height() * CARD_SCALE)
                card_click_rect = pygame.Rect(0, 0, cw, ch)
                card_click_rect.center = (
                    sprite_rect.centerx + CARD_OFFSET[0],
                    sprite_rect.centery + CARD_OFFSET[1]
                )

                # show item price on card reader
                if valid_order != 0:
                    # render message relative to card reader box
                    price = item_names[int(valid_order) - 1].split(" - ")[1]
                    payment_mesg = f"{price}"
                else:
                    payment_mesg = "..."

                    # if card image is pressed
                if card_click_rect.collidepoint(mouse_x, mouse_y):
                    print("card clicked")
                    # trigger payment only if a valid order exists
                    if valid_order != 0:
                        payment_success()
                    else:
                        active_message = "No valid order"
                        message_timer = MESSAGE_DURATION
                        valid_order = 0

            # Numpad input
            if numpad_visible:
                base_x = sprite_rect.centerx + NUMPAD_OFFSET[0] + GRID_OFFSET[0]
                base_y = sprite_rect.centery + NUMPAD_OFFSET[1] + GRID_OFFSET[1]
                # digit buttons
                for r in range(3):
                    for c in range(3):
                        rct = pygame.Rect(
                            base_x + c * (GRID_BUTTON_SIZE + GRID_PADDING_X),
                            base_y + r * (GRID_BUTTON_SIZE + GRID_PADDING_Y),
                            GRID_BUTTON_SIZE, GRID_BUTTON_SIZE
                        )
                        if rct.collidepoint(mouse_x, mouse_y):
                            order_number += str(r * 3 + c + 1)
                            if len(order_number) > 2: order_number = order_number[1:]
                # clear/enter
                c_r = pygame.Rect(base_x + CLEAR_BUTTON_OFFSET[0], base_y + CLEAR_BUTTON_OFFSET[1], *CLEAR_BUTTON_SIZE)
                e_r = pygame.Rect(base_x + ENTER_BUTTON_OFFSET[0], base_y + ENTER_BUTTON_OFFSET[1], *ENTER_BUTTON_SIZE)
                if c_r.collidepoint(mouse_x, mouse_y):
                    order_number = ""
                    active_message = ""
                    message_timer = 0
                    valid_order = 0  # invalidate order on clear
                # enter button
                if e_r.collidepoint(mouse_x, mouse_y):
                    # insert price message, persistent
                    if order_number.isdigit() and 1 <= int(order_number) <= 12:
                        valid_order = int(order_number)
                        selected_item = valid_order - 1
                        # ooutput: itemname chosen!
                        active_message = f"{item_names[selected_item].split(' - ')[0]} chosen!"
                        message_timer = -1  # special flag to make message persistent

                    else:
                        active_message = "No such item"
                        message_timer = 120
                        valid_order = 0
                    order_number = ""

    # Drawing
    screen.fill(bg_color)
    screen.blit(sprite, sprite_rect)

    # Draw items
    for idx, (x_off, y_off) in enumerate(item_offsets[:12]):
        img = item_surfaces[idx]
        iw, ih = img.get_size()
        sf = min(BOX_SIZE / iw, BOX_SIZE / ih)
        img_s = pygame.transform.smoothscale(img, (int(iw * sf), int(ih * sf)))
        b_r = img_s.get_rect(center=(sprite_rect.centerx + x_off, sprite_rect.centery + y_off))
        screen.blit(img_s, b_r)
        if DEBUG: pygame.draw.rect(screen, (255, 100, 100), b_r.inflate(0, 0), 2)

    # Draw numpad
    if numpad_visible:
        nw, nh = int(numpad_image.get_width() * NUMPAD_SCALE), int(numpad_image.get_height() * NUMPAD_SCALE)
        np_img = pygame.transform.smoothscale(numpad_image, (nw, nh))
        np_rect = np_img.get_rect(
            center=(sprite_rect.centerx + NUMPAD_OFFSET[0], sprite_rect.centery + NUMPAD_OFFSET[1]))
        screen.blit(np_img, np_rect)
        inp = input_font.render(order_number, True, (255, 255, 255))
        inp_rect = inp.get_rect(topright=(np_rect.right - 30, np_rect.top + 30))
        screen.blit(inp, inp_rect)
        if DEBUG:
            pass

    # Draw card reader image
    if cardReader_visible:
        # show card reader image
        cardReader_img_src = pygame.image.load("picture/cash/card_reader.png").convert_alpha()
        cw = int(cardReader_img_src.get_width() * CARDREADER_SCALE)
        ch = int(cardReader_img_src.get_height() * CARDREADER_SCALE)
        card_img = pygame.transform.smoothscale(cardReader_img_src, (cw, ch))
        card_rect = card_img.get_rect(
            center=(sprite_rect.centerx + CARDREADER_OFFSET[0], sprite_rect.centery + CARDREADER_OFFSET[1])
        )
        screen.blit(card_img, card_rect)

        if DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), card_rect, 2)
        # show card image twice for effect
        card_img_src = pygame.image.load("picture/cash/card.png").convert_alpha()
        for _ in range(2):
            cw = int(card_img_src.get_width() * CARD_SCALE)
            ch = int(card_img_src.get_height() * CARD_SCALE)
            card_img = pygame.transform.smoothscale(card_img_src, (cw, ch))
            card_img = pygame.transform.rotate(card_img, -90)
            card_rect = card_img.get_rect(
                center=(sprite_rect.centerx + CARD_OFFSET[0], sprite_rect.centery + CARD_OFFSET[1])
            )
            screen.blit(card_img, card_rect)
            if DEBUG:
                pygame.draw.rect(screen, (0, 255, 0), card_rect, 2)

    # Draw active message
    if active_message:
        msg_surf = font.render(active_message, True, (255, 255, 255))
        msg_pos = (sprite_rect.centerx - 80, sprite_rect.centery - 303)
        screen.blit(msg_surf, msg_pos)
        if message_timer > 0:
            message_timer -= 1
        elif message_timer == 0 and "Insert" not in active_message:
            active_message = ""

    if payment_mesg and cardReader_visible:
        msg_surf = input_font.render(payment_mesg, True, (255, 255, 255))
        msg_rect = msg_surf.get_rect(
            center=(sprite_rect.centerx + CARD_OFFSET[0]+5,
                    sprite_rect.centery + CARD_OFFSET[1] -235))
        screen.blit(msg_surf, msg_rect)

    # Draw UI outlines
    if DEBUG:
        for name, ((x_off, y_off), (sw, sh)) in ui_buttons.items():
            bs = 70 * ITEM_SCALE
            rw, rh = int(bs * sw), int(bs * sh)
            r = pygame.Rect(0, 0, rw, rh)
            r.center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
            pygame.draw.rect(screen, ui_colors[name], r, 2)
        card_off, card_scale = ui_buttons['cardreader_icon']
        bs = 70 * ITEM_SCALE
        cw, ch = int(bs * card_scale[0]), int(bs * card_scale[1])
        card_btn_rect = pygame.Rect(0, 0, cw, ch)
        card_btn_rect.center = (sprite_rect.centerx + card_off[0], sprite_rect.centery + card_off[1])
        pygame.draw.rect(screen, (255, 0, 255), card_btn_rect, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
