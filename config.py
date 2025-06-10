initial_width = 800
initial_height = 600

VM_SCALE = 0.54
ITEM_SCALE = 0.70
NUMPAD_OFFSET = (500, -150)
NUMPAD_SCALE = 1
GRID_OFFSET = (-65, -60)
GRID_BUTTON_SIZE = 40
GRID_PADDING_X = 5
GRID_PADDING_Y = 8

CLEAR_BUTTON_SIZE = (60, 30)
CLEAR_BUTTON_OFFSET = (0, GRID_BUTTON_SIZE * 3 + GRID_PADDING_Y + 17)
ENTER_BUTTON_SIZE = (60, 30)
ENTER_BUTTON_OFFSET = (CLEAR_BUTTON_SIZE[0] + GRID_PADDING_X + 10,
                       GRID_BUTTON_SIZE * 3 + GRID_PADDING_Y + 17)

CARDREADER_OFFSET = (375, 50)
CARDREADER_SCALE = 0.6
CARD_OFFSET = (375, 250)
CARD_SCALE = 0.7
CASH_MACHINE_OFFSET = (375, 150)
CASH_MACHINE_SCALE = 0.7
cash_offsets = [(250, -200), (250, -100), (250, 0), (250, 100), (250, 200)]
CASH_SCALE = 0.3

MESSAGE_DURATION = 180

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
