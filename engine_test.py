import pygame
from toppy2D import *

pygame.init()

FPS = 30

screen = pygame.display.set_mode((500, 500))

objects = [Object(100, 100), Group(objects=[Object(200, 200), Object(305, 200)])]
test = objects[1].get_id()
world = World()
world.add_objects(objects)
clock = pygame.time.Clock()

def events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            world.delete_object(test)

def draw():
    screen.fill("#555555")
    world.draw(screen, (True, True, True))
    pygame.display.update()

running = True
while running:
    clock.tick(FPS)
    events()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        world.camera_x += 5
    if keys[pygame.K_RIGHT]:
        world.camera_x -= 5
    draw()