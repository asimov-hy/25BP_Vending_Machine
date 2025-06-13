import pygame
import sys
import random

# ---------------------------- Initialization ----------------------------
pygame.init()

# Debug options
DEBUG = 0
click_pos = False

# Display setup
info = pygame.display.Info()
initial_width, initial_height = info.current_w, info.current_h
screen = pygame.display.set_mode((initial_width, initial_height-60), pygame.RESIZABLE)
pygame.display.set_caption("Brendan the Vending Machine")

# ---------------------------- Clock & State ----------------------------
clock = pygame.time.Clock()
running = True
order_number = ""
valid_order = 0
payment_money = 0
inserted_money = 0

numpad_visible = False
cardReader_visible = False
cash_machine_visible = False

return_change = False
cloned_items = []
spawn_timer = 0
SPAWN_DURATION = 30

# ---------------------------- Fonts & Messages ----------------------------
font = pygame.font.SysFont(None, 24)
input_font = pygame.font.SysFont(None, 48)

# message for item
MESSAGE_DURATION = 180
message_timer = 0
banner_message = ""

# message for card reader - item price
card_message = ""

# message for debug
debug_message = ""

# ---------------------------- Selection State ----------------------------
selected_item = None
cloned_items = []   # (original item name, positionx, positiony)

# ---------------------------- Scaling Factors ----------------------------
VM_SCALE = 0.54
ITEM_SCALE = 0.70
NUMPAD_SCALE = 0.27
CARDREADER_SCALE = 0.6
CARD_SCALE = 0.7
CASH_MACHINE_SCALE = 0.65
CASH_SCALE = 0.3
CLONECASH_SCALE = 0.2
CLONEITEM_SCALE = 2

# ---------------------------- Layout Offsets ----------------------------
NUMPAD_OFFSET = (500, -150)
GRID_OFFSET = (-90, -75)
CARDREADER_OFFSET = (375, 50)
CARD_OFFSET = (375, 250)
CASH_MACHINE_OFFSET = (375, 150)
cash_offsets = [(250, -200), (250, -100), (250, 0), (250, 100), (250, 200)]

# ---------------------------- Button & Grid Config ----------------------------

numpad_buttons = [
    "1", "2", "3",
    "4", "5", "6",
    "7", "8", "9",
    "C", "0", "E"
]
GRID_BUTTON_WIDTH =60  # wider button
GRID_BUTTON_HEIGHT = 53
GRID_PADDING_X = 5
GRID_PADDING_Y = 8
# CLEAR_BUTTON_SIZE = (60, 30)
# ENTER_BUTTON_SIZE = (60, 30)
# CLEAR_BUTTON_OFFSET = (0, GRID_BUTTON_SIZE * 3 + GRID_PADDING_Y + 17)
# ENTER_BUTTON_OFFSET = (CLEAR_BUTTON_SIZE[0] + GRID_PADDING_X + 10, GRID_BUTTON_SIZE * 3 + GRID_PADDING_Y + 17)

# ---------------------------- UI Buttons ----------------------------
ui_buttons = {
    "numpad": ((161, -120), (1.5, 2.0)),
    "cardreader_button": ((161, -21), (1.5, 1.0)),
    "cash": ((161, 65), (1.5, 1.6)),
    "dispenser": ((-33, 200), (5, 1.5))
}
ui_colors = {
    "numpad": (255, 200, 200),
    "cardreader_button": (200, 255, 200),
    "cash": (200, 200, 255),
    "dispenser": (255, 255, 200)
}

# ---------------------------- Asset Loading ----------------------------
original_sprite = pygame.image.load("vm_sprite.png").convert_alpha()
scaled_width = int(original_sprite.get_width() * VM_SCALE)
scaled_height = int(original_sprite.get_height() * VM_SCALE)
sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
bg_color = sprite.get_at((0, 0))

numpad_image = pygame.image.load("picture/cash/numpad.png").convert_alpha()
card_image_src = pygame.image.load("picture/cash/card.png").convert_alpha()

# ---------------------------- Stock Items ----------------------------
stock_list = [
    "picture/chips.png",
    "picture/coffee.png",
    "picture/cola_can.png",
    "picture/lemonade.png",
    "picture/orange_juice.png",
    "picture/cola_bottle.png",
    "picture/sword.png",
    "picture/mystery_potion.png",
    "picture/nuke.png",
    "picture/pokeball.png",
    "picture/mystery_box.png",
    "picture/small_doll.png",
    "picture/sold_out.png"
]

item_names = [
    "Crisps - $3500",
    "Coffee - $1500",
    "Cola Can - $1200",
    "Lemonade - $1300",
    "Orange Juice - $1500",
    "Cola Bottle - $2200",
    "Sword - $13000",
    "Mystery Potion - $30000",
    "Nuke - $100000",
    "Pokeball - $5000",
    "Mystery Box - $1000",
    "Small Doll - $50000",
    "Sold Out"
]

cash_images = [
    "picture/cash/cash_10000.png",
    "picture/cash/cash_5000.png",
    "picture/cash/cash_1000.png",
    "picture/cash/cash_500.png",
    "picture/cash/cash_100.png"
]

row_offsets = [-205, -124, -45]
col_offsets = [-151, -76, -4, 66]
item_offsets = [(x, y) for y in row_offsets for x in col_offsets]
BOX_SIZE = int(68 * ITEM_SCALE)

item_surfaces = []
for path in stock_list:
    img = pygame.image.load(path).convert_alpha()
    item_surfaces.append(img)

# ---------------------------- Game Loop ----------------------------

def payment_success():
    global banner_message, cloned_items, selected_item, valid_order, message_timer, card_message
    banner_message = "Payment complete"
    if selected_item is not None:
        dispenser_x = sprite_rect.centerx + ui_buttons["dispenser"][0][0]
        dispenser_y = sprite_rect.centery + ui_buttons["dispenser"][0][1]
        rand_x = dispenser_x + random.randint(-200, 200)
        rand_y = dispenser_y + random.randint(-50, 50)

        cloned_items.append({
            "type": "item",
            "index": selected_item,
            "pos": (rand_x, rand_y)
        })
    selected_item = None
    valid_order = 0

    message_timer = MESSAGE_DURATION
    card_message = "..."

while running:
    # create vending machine sprite rect
    window_width, window_height = screen.get_size()
    sprite_rect = sprite.get_rect(center=(window_width // 2, window_height // 2))

    # Handle events
    for event in pygame.event.get():

        # quit event
        if event.type == pygame.QUIT:
            running = False

        # window is resized
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # trigger debug mode when pressed D
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            DEBUG = not DEBUG

        # ------------------------------------ Mouse Events ------------------------------------
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # ---------------- UI Button Toggle Logic ----------------
            for name, ((x_off, y_off), (scale_w, scale_h)) in ui_buttons.items():
                base = 70 * ITEM_SCALE
                w = int(base * scale_w)
                h = int(base * scale_h)
                center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
                rect = pygame.Rect(0, 0, w, h)
                rect.center = center

                # Toggle visibility of numpad, card reader, or cash machine
                if rect.collidepoint(mouse_x, mouse_y):
                    if name == "numpad":
                        numpad_visible = not numpad_visible
                        cardReader_visible = False
                        cash_machine_visible = False

                        if numpad_visible:
                            debug_message = "Numpad Visible"
                        else:
                            debug_message = "Numpad Hidden"


                    elif name == "cardreader_button":
                        cardReader_visible = not cardReader_visible
                        cash_machine_visible = False
                        numpad_visible = False

                        if cardReader_visible:
                            debug_message = "Card Reader Visible"
                        else:
                            debug_message = "Card Reader Hidden"

                    elif name == "cash":
                        cash_machine_visible = not cash_machine_visible
                        numpad_visible = False
                        cardReader_visible = False

                        if cash_machine_visible:
                            debug_message = "Cash Machine Visible"
                        else:
                            debug_message = "Cash Machine Hidden"

            # ---------------- Item Selection ----------------
            for idx, (x_off, y_off) in enumerate(item_offsets[:12]):
                center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
                rect = pygame.Rect(0, 0, BOX_SIZE, BOX_SIZE)
                rect.center = center
                if rect.collidepoint(mouse_x, mouse_y):
                    selected_item = idx
                    valid_order = 0  # Reset until confirmed by numpad
                    banner_message = f"{idx + 1}: {item_names[idx]}"
                    message_timer = MESSAGE_DURATION

                    debug_message = "Item Selected: " + item_names[idx]

            # ---------------- Numpad Input Handling ----------------
            if numpad_visible:
                base_x = sprite_rect.centerx + NUMPAD_OFFSET[0] + GRID_OFFSET[0]
                base_y = sprite_rect.centery + NUMPAD_OFFSET[1] + GRID_OFFSET[1]

                for i, label in enumerate(numpad_buttons):
                    r = i // 3
                    c = i % 3
                    btn_rect = pygame.Rect(
                        base_x + c * GRID_BUTTON_WIDTH,
                        base_y + r * GRID_BUTTON_HEIGHT,
                        GRID_BUTTON_WIDTH, GRID_BUTTON_HEIGHT
                    )
                    if btn_rect.collidepoint(mouse_x, mouse_y):
                        if label == "C":
                            order_number = ""
                            banner_message = ""
                            message_timer = 0
                            valid_order = 0
                        elif label == "E":
                            if order_number.isdigit() and 1 <= int(order_number) <= 12:
                                valid_order = int(order_number)
                                selected_item = valid_order - 1
                                payment_money = int(item_names[valid_order - 1].split('$')[-1].replace(',', ''))
                                banner_message = f"Insert: ${payment_money - inserted_money}"
                                debug_message = f"Order: {order_number}, Pay: ${payment_money}"
                                message_timer = -1
                            else:
                                banner_message = "No such item"
                                message_timer = MESSAGE_DURATION
                                valid_order = 0
                            order_number = ""
                        else:
                            order_number += label
                            if len(order_number) > 2:
                                order_number = order_number[1:]

            # ---------------- Card Payment Handling ----------------
            if cardReader_visible:
                # Define clickable rect for the card image
                cw = int(card_image_src.get_width() * CARD_SCALE)
                ch = int(card_image_src.get_height() * CARD_SCALE)
                card_click_rect = pygame.Rect(0, 0, cw, ch)
                card_click_rect.center = (
                    sprite_rect.centerx + CARD_OFFSET[0],
                    sprite_rect.centery + CARD_OFFSET[1]
                )

                # Display item price if a valid order exists
                if valid_order != 0:
                    card_message = f"${payment_money}"
                else:
                    card_message = "..."

                # Detect if card image is clicked
                if card_click_rect.collidepoint(mouse_x, mouse_y):
                    print("card clicked")
                    if valid_order != 0:
                        payment_success()
                    else:
                        banner_message = "No valid order"
                        message_timer = MESSAGE_DURATION
                        valid_order = 0

            # ---------------- Cash Machine Handling ----------------
            if cash_machine_visible:
                for idx, (x_off, y_off) in enumerate(cash_offsets):
                    cash_img_src = pygame.image.load(cash_images[idx]).convert_alpha()
                    cash_w = int(cash_img_src.get_width() * CASH_SCALE)
                    cash_h = int(cash_img_src.get_height() * CASH_SCALE)
                    cash_rect = pygame.Rect(0, 0, cash_w, cash_h)
                    cash_rect.center = (
                        sprite_rect.centerx + CASH_MACHINE_OFFSET[0] + x_off,
                        sprite_rect.centery + CASH_MACHINE_OFFSET[1] + y_off
                    )

                    if cash_rect.collidepoint(mouse_x, mouse_y):
                        cash_filename = cash_images[idx].split('/')[-1]
                        debug_message = f"Pressed cash: {cash_filename}"

                        # Determine inserted value based on index
                        if idx == 0:
                            inserted_money += 10000
                        elif idx == 1:
                            inserted_money += 5000
                        elif idx == 2:
                            inserted_money += 1000
                        elif idx == 3:
                            inserted_money += 500
                        elif idx == 4:
                            inserted_money += 100

                        if valid_order != 0:
                            price_str = item_names[valid_order - 1].split('$')[-1].replace(',', '')
                            payment_money = int(price_str)
                            banner_message = f"Inserted: ${inserted_money}/${payment_money}"
                            message_timer = MESSAGE_DURATION

                            if inserted_money >= payment_money:
                                inserted_money -= payment_money
                                return_change = True
                                payment_success()

                        else:
                            banner_message = "No valid order"
                            message_timer = MESSAGE_DURATION
                            valid_order = 0

            # -------------------- Cloned Item Handling --------------------
            # if clone item is clicked it is destroyed
            for idx, cloned in enumerate(cloned_items):
                img_rect = pygame.Rect(0, 0, BOX_SIZE, BOX_SIZE)
                img_rect.center = cloned["pos"]
                if img_rect.collidepoint(mouse_x, mouse_y):
                    debug_message = f"Cloned Item {idx} clicked"
                    cloned_items.pop(idx)

    # --------------------------------------------Draw --------------------------------------------
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
        inp_rect = inp.get_rect(topright=(np_rect.right - 30, np_rect.top + 28))
        screen.blit(inp, inp_rect)
        if DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), np_rect, 2)
            pygame.draw.rect(screen, (0, 255, 0), inp_rect, 2)

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
    # Draw cash machine:
    if cash_machine_visible:
        cash_machine_img_src = pygame.image.load("picture/cash/cash_machine.png").convert_alpha()
        cm_w = int(cash_machine_img_src.get_width() * CASH_MACHINE_SCALE)
        cm_h = int(cash_machine_img_src.get_height() * CASH_MACHINE_SCALE)
        cash_machine_img = pygame.transform.smoothscale(cash_machine_img_src, (cm_w, cm_h))
        cash_machine_rect = cash_machine_img.get_rect(
            center=(sprite_rect.centerx + CASH_MACHINE_OFFSET[0], sprite_rect.centery + CASH_MACHINE_OFFSET[1])
        )
        screen.blit(cash_machine_img, cash_machine_rect)

        if DEBUG:
            pygame.draw.rect(screen, (0, 0, 255), cash_machine_rect, 2)


        for i, cash_path in enumerate(cash_images):
            cash_img_src = pygame.image.load(cash_path).convert_alpha()
            cash_w = int(cash_img_src.get_width() * CASH_SCALE)
            cash_h = int(cash_img_src.get_height() * CASH_SCALE)
            cash_img = pygame.transform.smoothscale(cash_img_src, (cash_w, cash_h))
            cash_rect = cash_img.get_rect(
                center=(sprite_rect.centerx + CASH_MACHINE_OFFSET[0] + cash_offsets[i][0],
                        sprite_rect.centery + CASH_MACHINE_OFFSET[1] + cash_offsets[i][1])
            )
            screen.blit(cash_img, cash_rect)
            if DEBUG:
                pygame.draw.rect(screen, (255, 255, 0), cash_rect, 2)

    # draw cloned items
    for cloned in cloned_items:
        if cloned["type"] == "cash":
            img = pygame.image.load(cash_images[cloned["index"]]).convert_alpha()
            cw = int(img.get_width() * CLONECASH_SCALE)
            ch = int(img.get_height() * CLONECASH_SCALE)
            img = pygame.transform.smoothscale(img, (cw, ch))
            img_rect = img.get_rect(center=cloned["pos"])
            screen.blit(img, img_rect)
            if DEBUG:
                pygame.draw.rect(screen, (200, 200, 0), img_rect, 2)

        elif cloned["type"] == "item":
            img = item_surfaces[cloned["index"]]
            iw, ih = img.get_size()
            sf = min(BOX_SIZE / iw, BOX_SIZE / ih) * CLONEITEM_SCALE
            img_s = pygame.transform.smoothscale(img, (int(iw * sf), int(ih * sf)))
            b_r = img_s.get_rect(center=cloned["pos"])
            screen.blit(img_s, b_r)
            if DEBUG:
                pygame.draw.rect(screen, (200, 0, 200), b_r.inflate(0, 0), 2)

    # change logic
    if return_change:
        if inserted_money == 0:
            return_change = False
        elif spawn_timer <= 0:
            denominations = [10000, 5000, 1000, 500, 100]
            for i, value in enumerate(denominations):
                if inserted_money >= value:
                    inserted_money -= value
                    spawn_timer = SPAWN_DURATION

                    # Calculate position for cash clone spawn near cash dispenser
                    x_variation = random.randint(-50, 50)
                    y_variation = random.randint(-50, 50)
                    clone_pos = (
                        sprite_rect.centerx + ui_buttons["cash"][0][0] + x_variation,
                        sprite_rect.centery + ui_buttons["cash"][0][1] + y_variation
                    )
                    cloned_items.append({"type": "cash", "index": i, "pos": clone_pos})
                    break
        else:
            spawn_timer -= 1


    # --------------------------------------   message --------------------------------------
    # Draw active message
    if banner_message:
        msg_surf = font.render(banner_message, True, (255, 255, 255))
        msg_pos = (sprite_rect.centerx - 80, sprite_rect.centery - 303)
        screen.blit(msg_surf, msg_pos)
        if message_timer > 0:
            message_timer -= 1
        elif message_timer == 0 and "Insert" not in banner_message:
            banner_message = ""

    if card_message and cardReader_visible:
        msg_surf = input_font.render(card_message, True, (255, 255, 255))
        msg_rect = msg_surf.get_rect(
            center=(sprite_rect.centerx + CARD_OFFSET[0]+5,
                    sprite_rect.centery + CARD_OFFSET[1] -235))
        screen.blit(msg_surf, msg_rect)

    if DEBUG and debug_message:
        debug_surf = input_font.render(debug_message, True, (255, 255, 255))
        debug_pos = (100, 100)
        screen.blit(debug_surf, debug_pos)

    # --------------------------------------- Debugging ---------------------------------------
    if DEBUG:
        # Draw debug rectangles for all UI buttons
        for name, ((x_off, y_off), (sw, sh)) in ui_buttons.items():
            bs = 70 * ITEM_SCALE
            rw, rh = int(bs * sw), int(bs * sh)
            r = pygame.Rect(0, 0, rw, rh)
            r.center = (sprite_rect.centerx + x_off, sprite_rect.centery + y_off)
            pygame.draw.rect(screen, ui_colors[name], r, 2)

        if numpad_visible:

            base_x = sprite_rect.centerx + NUMPAD_OFFSET[0] + GRID_OFFSET[0]
            base_y = sprite_rect.centery + NUMPAD_OFFSET[1] + GRID_OFFSET[1]

            for i, label in enumerate(numpad_buttons):
                r = i // 3
                c = i % 3
                btn_rect = pygame.Rect(
                    base_x + c * GRID_BUTTON_WIDTH,
                    base_y + r * GRID_BUTTON_HEIGHT,
                    GRID_BUTTON_WIDTH, GRID_BUTTON_HEIGHT
                )
                pygame.draw.rect(screen, (0, 255, 0), btn_rect, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
