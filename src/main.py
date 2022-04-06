# import launcher
import time
import badger2040
import badger_os


# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 104

COMPANY_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

COMPANY_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

BADGE_IMAGE = bytearray(int(IMAGE_WIDTH * HEIGHT / 8))

try:
    open("lemon.raw", "rb").readinto(BADGE_IMAGE)
except OSError:
    try:
        import badge_image
        BADGE_IMAGE = bytearray(badge_image.data())
        del badge_image
    except ImportError:
        pass


# ------------------------------
#      Utility functions
# ------------------------------

# Reduce the size of a string until it fits within a given width
def truncatestring(text, text_size, width):
    while True:
        length = screen.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            text += ""
            return text


class Screen:
    def __init__(self):
        self.badger = badger2040.Badger2040()
        self.badger.led(128)
        self.badger.update_speed(badger2040.UPDATE_NORMAL)

    def clear(self, *args, **kwargs):
        self.badger.clear(*args, **kwargs)

    def pen(self, *args, **kwargs):
        self.badger.pen(*args, **kwargs)
    def font(self, *args, **kwargs):
        self.badger.font(*args, **kwargs)
    def thickness(self, *args, **kwargs):
        self.badger.thickness(*args, **kwargs)

    def image(self, *args, **kwargs):
        self.badger.image(*args, **kwargs)

    def line(self, *args, **kwargs):
        self.badger.line(*args, **kwargs)
    def rectangle(self, *args, **kwargs):
        self.badger.rectangle(*args, **kwargs)
        
    def text(self, text, x, y, size, spacing=0):
        for ch in text:
            self.badger.text(ch, x, y, size)
            x += self.badger.measure_text(ch, size) + spacing

    def measure_text(self, text, size, spacing=0):
        return sum(self.badger.measure_text(ch, size) for ch in text) + max(len(text) - 1, 0) * spacing
    
    
# ------------------------------
#      Drawing functions
# ------------------------------

# Draw the badge, including user text
def draw_badge():
    screen.pen(0)
    screen.clear()

    # Draw badge image
    screen.image(BADGE_IMAGE, IMAGE_WIDTH, HEIGHT, WIDTH - IMAGE_WIDTH, 0)

    # Draw a border around the image
    screen.pen(0)
    screen.thickness(1)
    screen.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
    screen.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
    screen.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
    screen.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

    # Uncomment this if a white background is wanted behind the company
    # screen.pen(15)
    # screen.rectangle(1, 1, TEXT_WIDTH, COMPANY_HEIGHT - 1)

    # Draw the company
    screen.pen(15)  # Change this to 0 if a white background is used
    screen.font("sans")
    screen.thickness(3)
    screen.text(company, LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1, COMPANY_TEXT_SIZE, 2)

    # Draw a white background behind the name
    screen.pen(15)
    screen.thickness(1)
    screen.rectangle(1, COMPANY_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT)

    # Draw the name, scaling it based on the available width
    screen.pen(0)
    screen.font("sans")
    screen.thickness(4)
    name_size = 2.0  # A sensible starting scale
    name_spacing = 2
    while True:
        name_length = screen.measure_text(name, name_size, spacing=name_spacing)
        if name_length >= (TEXT_WIDTH - NAME_PADDING) and name_size >= 0.1:
            name_size -= 0.01
        else:
            screen.text(name, (TEXT_WIDTH - name_length) // 2, (NAME_HEIGHT // 2) + COMPANY_HEIGHT + 1, name_size, spacing=name_spacing)
            break

    # Draw a white backgrounds behind the details
    screen.pen(15)
    screen.thickness(1)
    screen.rectangle(1, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH, DETAILS_HEIGHT - 1)
    screen.rectangle(1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1)

    # Draw the first detail's title and text
    screen.pen(0)
    screen.font("sans")
    screen.thickness(3)
    
    title_length = 0
    for i, (title, _) in enumerate(details):
        title_length = max(title_length, screen.measure_text(title, DETAILS_TEXT_SIZE))

    for i, (title, text) in enumerate(details):
        height_offset_factor = 2 * (len(details) - i) - 1
        screen.thickness(3)
        screen.text(title, LEFT_PADDING, HEIGHT - ((DETAILS_HEIGHT * height_offset_factor) // 2), DETAILS_TEXT_SIZE)
        screen.thickness(2)
        screen.text(text, 5 + title_length + DETAIL_SPACING, HEIGHT - ((DETAILS_HEIGHT * height_offset_factor) // 2), DETAILS_TEXT_SIZE)


# ------------------------------
#        Program setup
# ------------------------------

# Create a new Badger and set it to update NORMAL
screen = Screen()

# Open the badge file
badge = open("badge.txt", "r")

# Read in the next 6 lines
company = badge.readline()
name = badge.readline()
details = []
for i in range(2):
    title, detail = badge.readline().split("|", 1)
    details.append((title.strip(), detail.strip()))

# Truncate all of the text (except for the name as that is scaled)
# company = truncatestring(company, COMPANY_TEXT_SIZE, TEXT_WIDTH)
# 
# for i, (title, text) in details:
#     title = truncatestring(title, DETAILS_TEXT_SIZE, TEXT_WIDTH)
#     text = truncatestring(text, DETAILS_TEXT_SIZE,
#                               TEXT_WIDTH - DETAIL_SPACING - screen.measure_text(title, DETAILS_TEXT_SIZE))
#     details[i] = title, text

# ------------------------------
#       Main program
# ------------------------------

draw_badge()

while True:
    screen.badger.update()
    time.sleep(1)

    # If on battery, halt the Badger to save power, it will wake up if any of the front buttons are pressed
    screen.badger.halt()
