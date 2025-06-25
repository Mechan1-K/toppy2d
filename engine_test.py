import pygame
from toppy2D import *

pygame.init()

FPS = 30

screen = pygame.display.set_mode((500, 500))

objects = [Object(100, 100), Group(objects=[Object(200, 200), Object(305, 200)]), Union(-100, 100, objects=[Object(0, 0), Object(10, 10)])]
world = World()
world.objects.extend(objects)
world.players = [Player(0, 0, controls=["w", "s", "a", "d"], name="guy"), Player(100, 0, controls=["y", "h", "g", "j"], name="ziom")]
world.lock_camera("guy")

clock = pygame.time.Clock()

def events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            world.objects[2].x += 10

def draw():
    screen.fill("#555555")
    world.draw(screen, (True, True, True))
    pygame.display.update()

running = True
while running:
    clock.tick(FPS)
    events()
    world.players_tick()

    draw()