from game_state import *
from config import MESSAGE_DURATION

def payment_success():
    global active_message, cloned_items, selected_item, valid_order, message_timer, payment_message
    active_message = "Payment complete"
    if selected_item is not None:
        cloned_items.append(selected_item)
    selected_item = None
    valid_order = 0
    message_timer = MESSAGE_DURATION
    payment_message = "..."