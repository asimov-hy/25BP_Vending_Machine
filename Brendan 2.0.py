import pygame
import sys
import random
import datetime

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
receipt_visible = False

return_change = False
cloned_items = []
spawn_timer = 0
SPAWN_DURATION = 20

# ---------------------------- Fonts & Messages ----------------------------
font = pygame.font.SysFont(None, 24)
input_font = pygame.font.SysFont(None, 48)

mono_font = pygame.font.SysFont("Courier New", 20)

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
last_purchased_item = None
purchase_time = ""

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
NUMPAD_OFFSET = (375, -175)
GRID_OFFSET = (-90, -75)
CARDREADER_OFFSET = (375, 50)
CARD_OFFSET = (400, 250)
CASH_MACHINE_OFFSET = (380, 150)
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


receipt_width = 400
receipt_height = 400

receipt_payment = 0
receipt_paid = 0
receipt_change = 0

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
stock_address = [
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

stock_data = [
    {"name": "Crisps", "price": 3500, "stock": 5},
    {"name": "Coffee", "price": 1500, "stock": 5},
    {"name": "Cola Can", "price": 1200, "stock": 5},
    {"name": "Lemonade", "price": 1300, "stock": 5},
    {"name": "Orange Juice", "price": 1500, "stock": 5},
    {"name": "Cola Bottle", "price": 2200, "stock": 5},
    {"name": "Sword", "price": 13000, "stock": 2},
    {"name": "Mystery Potion", "price": 30000, "stock": 1},
    {"name": "Nuke", "price": 100000, "stock": 1},
    {"name": "Pokeball", "price": 5000, "stock": 3},
    {"name": "Mystery Box", "price": 1000, "stock": 4},
    {"name": "Small Doll", "price": 50000, "stock": 2},
    {"name": "Sold Out", "price": 0, "stock": 0}
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
for path in stock_address:
    img = pygame.image.load(path).convert_alpha()
    item_surfaces.append(img)

# ---------------------------- Animation Variables ----------------------------

numpad_anim_progress = 0.0  # 0 = hidden, 1 = fully shown
NUMPAD_ANIM_DURATION = 1000  # in milliseconds

cardreader_anim_progress = 0.0  # 0 = hidden, 1 = shown
card_anim_progress = 0.0        # 0 = below screen, 1 = at slot
CARDREADER_ANIM_DURATION = 1000
CARD_ANIM_DURATION = 1000

cashmachine_anim_progress = 0.0  # 0 = hidden, 1 = visible
cashimages_anim_progress = 0.0   # for bills appearing
CASHMACHINE_ANIM_DURATION = 1000
CASHIMAGES_ANIM_DURATION = 1000

receipt_anim_progress = 0.0
RECEIPT_ANIM_DURATION = 1000

receipt_dismissing = False

receipt_pending = False
pending_receipt_data = None
pending_payment_type = None
change_due = 0



# ---------------------------- Game Loop ----------------------------

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def draw_stock_counts(screen, sprite_rect, font):
    for idx, (x_off, y_off) in enumerate(item_offsets[:12]):
        stock = stock_data[idx]["stock"]
        if stock > 0:
            color = (255, 255, 0)
            stock_txt = font.render(f"{stock}", True, color)
            pos = (sprite_rect.centerx + x_off - 24, sprite_rect.centery + y_off + BOX_SIZE//2 - 18)
            screen.blit(stock_txt, pos)
        else:
            sold_out_img = item_surfaces[-1]
            iw, ih = sold_out_img.get_size()
            scaled_img = pygame.transform.smoothscale(sold_out_img, (int(iw * 0.15), int(ih * 0.15)))
            img_rect = scaled_img.get_rect(center=(sprite_rect.centerx + x_off, sprite_rect.centery + y_off))
            screen.blit(scaled_img, img_rect)


def payment_success(payment):
    global banner_message, cloned_items, selected_item, valid_order, message_timer
    global card_message, receipt_visible, last_purchased_item, purchase_time
    global receipt_paid, receipt_change, cardReader_visible, cash_machine_visible
    global receipt_dismissing, receipt_pending, receipt_payment, inserted_money
    global receipt_anim_progress, receipt_visible, pending_payment_type, change_due, return_change

    # If a receipt is still visible or animating, dismiss it first
    if receipt_visible or receipt_anim_progress > 0:
        receipt_dismissing = True
        receipt_pending = True
        pending_payment_type = payment
        return  # wait until old one is gone before creating new
    # else, continue with new receipt logic

    if payment == "card":
        receipt_payment = payment_money
        receipt_paid = payment_money
        receipt_change = 0
    elif payment == "cash":
        receipt_payment = payment_money
        receipt_paid = inserted_money
        receipt_change = inserted_money - payment_money
        change_due = receipt_change
        inserted_money = 0
        return_change = True


    else:   # error payment or fraud
            receipt_payment = 0
            receipt_paid = 0
            receipt_change = 0


    banner_message = "Payment complete"
    receipt_visible = True
    if selected_item is not None:
        stock_data[selected_item]["stock"] -= 1
        dispenser_x = sprite_rect.centerx + ui_buttons["dispenser"][0][0]
        dispenser_y = sprite_rect.centery + ui_buttons["dispenser"][0][1]
        rand_x = dispenser_x + random.randint(-150, 150)
        rand_y = dispenser_y + random.randint(-50, 50)

        cloned_items.append({
            "type": "item",
            "index": selected_item,
            "pos": (rand_x, rand_y)
        })
    last_purchased_item = selected_item
    purchase_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    selected_item = None
    valid_order = 0

    message_timer = MESSAGE_DURATION
    card_message = "..."
    cardReader_visible = False
    cash_machine_visible = False


while running:
    dt = clock.tick(60)
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
                    banner_message = f"{idx + 1}: {stock_data[idx]['name']} - ${stock_data[idx]['price']}"
                    message_timer = MESSAGE_DURATION

                    debug_message = f"Item Selected: {stock_data[idx]['name']}"

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
                            if order_number.isdigit() and 1 <= int(order_number) <= 12 and stock_data[int(order_number) - 1]['stock'] > 0:
                                valid_order = int(order_number)
                                selected_item = valid_order - 1
                                payment_money = stock_data[valid_order - 1]['price']
                                banner_message = f"Insert: ${payment_money - inserted_money}"
                                debug_message = f"Order: {order_number}, Pay: ${payment_money}"
                                message_timer = -1
                            else:
                                banner_message = "No item stocked"
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

                        payment_success("card")
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
                            payment_money = stock_data[valid_order - 1]['price']
                            banner_message = f"Inserted: ${inserted_money}/${payment_money}"
                            message_timer = MESSAGE_DURATION

                            if inserted_money >= payment_money:

                                payment_success("cash")
                                return_change = True


                        else:
                            banner_message = "No valid order"
                            message_timer = MESSAGE_DURATION
                            valid_order = 0

            # -------------------- Cloned Item Handling --------------------
            # if clone item is clicked it is destroyed
            for idx, cloned in enumerate(cloned_items):
                img_rect = pygame.Rect(0, 0, BOX_SIZE, BOX_SIZE)
                img_rect.center = cloned["pos"]
                if img_rect.collidepoint(mouse_x, mouse_y) and "anim" not in cloned:
                    debug_message = f"Cloned Item {idx} clicked"
                    cloned["anim"] = {
                        "vy": -8,  # initial upward velocity
                        "gravity": 0.6,  # acceleration downward
                        "life": 0  # counts frames
                    }

            # -------------------- receipt handling --------------------
            # destroy receipt if clicked
            if receipt_visible:
                receipt_rect = pygame.Rect(0, 0, receipt_width, receipt_height)
                receipt_rect.center = (sprite_rect.centerx - 450, sprite_rect.centery)

                if receipt_rect.collidepoint(mouse_x, mouse_y):
                    debug_message = "Receipt clicked"

                    receipt_dismissing = True


    # --------------------------------------------Draw --------------------------------------------
    screen.fill(bg_color)

    # Draw numpad
    if numpad_anim_progress > 0:


        nw, nh = int(numpad_image.get_width() * NUMPAD_SCALE), int(numpad_image.get_height() * NUMPAD_SCALE)
        np_img = pygame.transform.smoothscale(numpad_image, (nw, nh))
        np_rect = np_img.get_rect(
            center=(sprite_rect.centerx + NUMPAD_OFFSET[0] + numpad_anim_x, sprite_rect.centery + NUMPAD_OFFSET[1])
        )
        screen.blit(np_img, np_rect)
        inp = input_font.render(order_number, True, (255, 255, 255))
        inp_rect = inp.get_rect(topright=(np_rect.right - 30, np_rect.top + 28))
        screen.blit(inp, inp_rect)
        if DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), np_rect, 2)
            pygame.draw.rect(screen, (0, 255, 0), inp_rect, 2)

    # Draw card reader image
    if cardreader_anim_progress > 0:

        # show card reader image
        cardReader_img_src = pygame.image.load("picture/cash/card_reader.png").convert_alpha()
        cw = int(cardReader_img_src.get_width() * CARDREADER_SCALE)
        ch = int(cardReader_img_src.get_height() * CARDREADER_SCALE)
        card_img = pygame.transform.smoothscale(cardReader_img_src, (cw, ch))
        card_rect = card_img.get_rect(
            center=(sprite_rect.centerx + CARDREADER_OFFSET[0] + cardreader_anim_x,
                    sprite_rect.centery + CARDREADER_OFFSET[1])
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
                center=(sprite_rect.centerx + CARD_OFFSET[0], card_anim_y)
            )

            screen.blit(card_img, card_rect)
            if DEBUG:
                pygame.draw.rect(screen, (0, 255, 0), card_rect, 2)

    # Draw cash machine:
    if cashmachine_anim_progress > 0:

        cash_machine_img_src = pygame.image.load("picture/cash/cash_machine.png").convert_alpha()
        cm_w = int(cash_machine_img_src.get_width() * CASH_MACHINE_SCALE)
        cm_h = int(cash_machine_img_src.get_height() * CASH_MACHINE_SCALE)
        cash_machine_img = pygame.transform.smoothscale(cash_machine_img_src, (cm_w, cm_h))
        cash_machine_rect = cash_machine_img.get_rect(
            center=(sprite_rect.centerx + CASH_MACHINE_OFFSET[0] + cashmachine_anim_x,
                    sprite_rect.centery + CASH_MACHINE_OFFSET[1])
        )
        screen.blit(cash_machine_img, cash_machine_rect)

        if DEBUG:
            pygame.draw.rect(screen, (0, 0, 255), cash_machine_rect, 2)


        for i, cash_path in enumerate(cash_images):
            cash_img_src = pygame.image.load(cash_path).convert_alpha()
            cash_w = int(cash_img_src.get_width() * CASH_SCALE)
            cash_h = int(cash_img_src.get_height() * CASH_SCALE)
            cash_img = pygame.transform.smoothscale(cash_img_src, (cash_w, cash_h))
            final_cash_x = sprite_rect.centerx + CASH_MACHINE_OFFSET[0] + cash_offsets[i][0]

            # Animate from right to that final position
            start_x = window_width + 200  # offscreen right
            animated_x = start_x + (final_cash_x - start_x) * cashimages_eased
            cash_rect = cash_img.get_rect(
                center=(animated_x,
                        sprite_rect.centery + CASH_MACHINE_OFFSET[1] + cash_offsets[i][1])
            )
            screen.blit(cash_img, cash_rect)
            if DEBUG:
                pygame.draw.rect(screen, (255, 255, 0), cash_rect, 2)


    screen.blit(sprite, sprite_rect)

    # --------------------------------------   Animation --------------------------------------

    # Easing animation for numpad
    if numpad_visible and numpad_anim_progress < 1.0:
        numpad_anim_progress += dt / NUMPAD_ANIM_DURATION
        if numpad_anim_progress > 1.0:
            numpad_anim_progress = 1.0
    elif not numpad_visible and numpad_anim_progress > 0.0:
        numpad_anim_progress -= dt / NUMPAD_ANIM_DURATION
        if numpad_anim_progress < 0.0:
            numpad_anim_progress = 0.0

    numpad_eased = ease_in_out_cubic(numpad_anim_progress)
    numpad_anim_x = -400 + 400 * numpad_eased

    # Easing animation for card reader
    if cardReader_visible and cardreader_anim_progress < 1.0:
        cardreader_anim_progress += dt / CARDREADER_ANIM_DURATION
        if cardreader_anim_progress > 1.0:
            cardreader_anim_progress = 1.0
    elif not cardReader_visible and cardreader_anim_progress > 0.0:
        cardreader_anim_progress -= dt / CARDREADER_ANIM_DURATION
        if cardreader_anim_progress < 0.0:
            cardreader_anim_progress = 0.0

    # Easing animation for card
    if cardReader_visible and card_anim_progress < 1.0:
        card_anim_progress += dt / CARD_ANIM_DURATION
        if card_anim_progress > 1.0:
            card_anim_progress = 1.0
    elif not cardReader_visible and card_anim_progress > 0.0:
        card_anim_progress -= dt / CARD_ANIM_DURATION
        if card_anim_progress < 0.0:
            card_anim_progress = 0.0

    # Compute eased positions
    cardreader_eased = ease_in_out_cubic(cardreader_anim_progress)
    card_eased = ease_in_out_cubic(card_anim_progress)
    cardreader_anim_x = -400 + 400 * cardreader_eased  # Slide from left
    card_anim_y = window_height + 100 - (
                window_height + 100 - (sprite_rect.centery + CARD_OFFSET[1])) * card_eased  # Slide up from bottom

    # Easing animation for cash machine
    if cash_machine_visible and cashmachine_anim_progress < 1.0:
        cashmachine_anim_progress += dt / CASHMACHINE_ANIM_DURATION
        if cashmachine_anim_progress > 1.0:
            cashmachine_anim_progress = 1.0
    elif not cash_machine_visible and cashmachine_anim_progress > 0.0:
        cashmachine_anim_progress -= dt / CASHMACHINE_ANIM_DURATION
        if cashmachine_anim_progress < 0.0:
            cashmachine_anim_progress = 0.0

    # Easing animation for cash images
    if cash_machine_visible and cashimages_anim_progress < 1.0:
        cashimages_anim_progress += dt / CASHIMAGES_ANIM_DURATION
        if cashimages_anim_progress > 1.0:
            cashimages_anim_progress = 1.0
    elif not cash_machine_visible and cashimages_anim_progress > 0.0:
        cashimages_anim_progress -= dt / CASHIMAGES_ANIM_DURATION
        if cashimages_anim_progress < 0.0:
            cashimages_anim_progress = 0.0

    # Compute eased positions
    cashmachine_eased = ease_in_out_cubic(cashmachine_anim_progress)
    cashimages_eased = ease_in_out_cubic(cashimages_anim_progress)
    cashmachine_anim_x = -400 + 400 * cashmachine_eased  # from left
    cashimages_anim_x = window_width + 200 - (window_width + 200 - 0) * cashimages_eased  # from right

    # Easing animation for receipt
    # Receipt animation logic
    if receipt_visible and not receipt_dismissing:
        if receipt_anim_progress < 1.0:
            receipt_anim_progress += dt / RECEIPT_ANIM_DURATION
            if receipt_anim_progress > 1.0:
                receipt_anim_progress = 1.0

    elif receipt_dismissing:
        if receipt_anim_progress > 0.0:
            receipt_anim_progress -= dt / RECEIPT_ANIM_DURATION
            if receipt_anim_progress < 0.0:
                receipt_anim_progress = 0.0
        if receipt_anim_progress == 0.0:
            receipt_dismissing = False
            receipt_visible = False

            if receipt_pending:
                receipt_pending = False
                payment_success(pending_payment_type)
                pending_payment_type = None

    receipt_eased = ease_in_out_cubic(receipt_anim_progress)

    # From above window (-receipt_height) to center (normal position), then slide down if dismissed
    receipt_anim_y = -receipt_height + (sprite_rect.centery - (-receipt_height)) * receipt_eased

    # Draw items
    for idx, (x_off, y_off) in enumerate(item_offsets[:12]):
        img = item_surfaces[idx]
        iw, ih = img.get_size()
        sf = min(BOX_SIZE / iw, BOX_SIZE / ih)
        img_s = pygame.transform.smoothscale(img, (int(iw * sf), int(ih * sf)))
        b_r = img_s.get_rect(center=(sprite_rect.centerx + x_off, sprite_rect.centery + y_off))
        screen.blit(img_s, b_r)
        draw_stock_counts(screen, sprite_rect, font)
        if DEBUG: pygame.draw.rect(screen, (255, 100, 100), b_r.inflate(0, 0), 2)


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

    for cloned in cloned_items[:]:  # loop over a copy to allow safe removal
        if "anim" in cloned:
            cloned["anim"]["vy"] += cloned["anim"]["gravity"]
            x, y = cloned["pos"]
            y += cloned["anim"]["vy"]
            cloned["pos"] = (x, y)
            cloned["anim"]["life"] += 1

            # Remove if out of screen
            if y > window_height + 100:
                cloned_items.remove(cloned)

    # draw receipt
    if receipt_anim_progress > 0:

        receipt_rect = pygame.Rect(0, 0, receipt_width, receipt_height)
        receipt_rect.center = (sprite_rect.centerx - 450, receipt_anim_y)

        # Draw receipt background image
        receipt_bg_img = pygame.image.load("picture/cash/receipt_bg.png").convert_alpha()
        receipt_bg_img = pygame.transform.scale(receipt_bg_img, (receipt_width, receipt_height))
        screen.blit(receipt_bg_img, receipt_rect)

        # Display text lines (mock receipt)
        lines = [
            "  BRENDAN THE VENDING MACHINE",
            "",
            "",
            "   Seoul, South Korea",
            f"  {purchase_time}",
            "  --------------------------",
            "  ITEM           PRICE",
            f"  {stock_data[last_purchased_item]['name']:<14} $ {receipt_payment:,}"
            "",
            "  --------------------------",
            f"  TOTAL          $ {receipt_payment:,}",
            f"  PAID           $ {receipt_paid:,}",
            f"  CHANGE         $ {receipt_change:,}",
            "",
            "  --------------------------",
            "",
            "  THANK YOU FOR YOUR PURCHASE",
            ""
        ]

        for i, line in enumerate(lines):

            text = mono_font.render(line, True, (0, 0, 0))
            screen.blit(text, (receipt_rect.x + 20, receipt_rect.y + 30 + i * 18))

    # change logic
    if return_change:
        if change_due == 0:
            return_change = False
        elif spawn_timer <= 0:
            denominations = [10000, 5000, 1000, 500, 100]
            for i, value in enumerate(denominations):
                if change_due  >= value:
                    change_due  -= value
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

    if card_message and cardreader_anim_progress == 1.0:
        msg_surf = input_font.render(card_message, True, (255, 255, 255))
        msg_rect = msg_surf.get_rect(
            center=(sprite_rect.centerx + CARDREADER_OFFSET[0]+5,
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

        if receipt_visible:
            receipt_rect = pygame.Rect(0, 0, receipt_width-20, receipt_height-20)
            receipt_rect.center = (sprite_rect.centerx - 450, sprite_rect.centery)
            pygame.draw.rect(screen, (255, 0, 0), receipt_rect, 2)


    pygame.display.flip()


pygame.quit()
sys.exit()
