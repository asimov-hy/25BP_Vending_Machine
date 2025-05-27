import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vending Machine")

# Fonts
font = pygame.font.Font(None, 36)

# Items in the vending machine
items = [
    {"name": "Soda", "price": 1.50, "rect": pygame.Rect(50, 100, 200, 100)},
    {"name": "Chips", "price": 1.00, "rect": pygame.Rect(300, 100, 200, 100)},
    {"name": "Candy", "price": 0.75, "rect": pygame.Rect(550, 100, 200, 100)},
]

# Payment methods
payment_methods = [
    {"name": "Cash", "rect": pygame.Rect(200, 400, 150, 50)},
    {"name": "Card", "rect": pygame.Rect(450, 400, 150, 50)},
]

# Selected item and payment method
selected_item = None
selected_payment = None


def draw_items():
    for item in items:
        pygame.draw.rect(screen, GRAY, item["rect"])
        text = font.render(f"{item['name']} - ${item['price']:.2f}", True, BLACK)
        screen.blit(text, (item["rect"].x + 10, item["rect"].y + 30))


def draw_payment_methods():
    for method in payment_methods:
        pygame.draw.rect(screen, GRAY, method["rect"])
        text = font.render(method["name"], True, BLACK)
        screen.blit(text, (method["rect"].x + 20, method["rect"].y + 10))


def main():
    global selected_item, selected_payment

    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)

        # Draw items and payment methods
        draw_items()
        draw_payment_methods()

        # Display selected item and payment method
        if selected_item:
            item_text = font.render(f"Selected: {selected_item['name']}", True, BLACK)
            screen.blit(item_text, (50, 300))
        if selected_payment:
            payment_text = font.render(f"Payment: {selected_payment['name']}", True, BLACK)
            screen.blit(payment_text, (50, 350))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Check if an item is selected
                for item in items:
                    if item["rect"].collidepoint(pos):
                        selected_item = item
                        selected_payment = None  # Reset payment method

                # Check if a payment method is selected
                for method in payment_methods:
                    if method["rect"].collidepoint(pos) and selected_item:
                        selected_payment = method
                        print(f"Purchased {selected_item['name']} with {selected_payment['name']}!")

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()