import pygame
import requests
from io import BytesIO
from PIL import Image
import sys

# Emote-URL
EMOTE_URL = "https://static-cdn.jtvnw.net/emoticons/v2/25/default/dark/3.0"  # Kappa

# Emote herunterladen und konvertieren
def load_emote(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode)

# Pygame initialisieren
pygame.init()
screen = pygame.display.set_mode((800, 200), pygame.NOFRAME)  # ohne Rand
pygame.display.set_caption("Twitch Emote")
clock = pygame.time.Clock()

# Transparenter Hintergrund (optional für OBS-Chroma-Keying)
bg_color = (0, 255, 0)  # Grün für Chroma-Key
screen.fill(bg_color)

emote_img = load_emote(EMOTE_URL)
x = -emote_img.get_width()
y = 100

running = True
while running:
    clock.tick(60)  # 60 FPS
    screen.fill(bg_color)

    # Event-Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Emote bewegen
    x += 5
    screen.blit(emote_img, (x, y))

    pygame.display.update()

    # Emote ist durchgelaufen
    if x > 800:
        running = False

pygame.quit()
sys.exit()
