import pygame
import toppy2D

pygame.init()

FPS = 30

screen = pygame.display.set_mode((500, 500))

objects = [toppy2D.Object(0, 0, toppy2D.load_image("cat.png", (100, 100)), (0, 50, 100, 50))]
engine = toppy2D.Engine()
engine.add_objects(objects)
clock = pygame.time.Clock()

def events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

def draw():
    screen.fill("#555555")
    engine.draw(screen, (True, True, True))
    pygame.display.update()

running = True
while running:
    clock.tick(FPS)
    events()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        engine.camera_x += 5
    if keys[pygame.K_RIGHT]:
        engine.camera_x -= 5
    draw()