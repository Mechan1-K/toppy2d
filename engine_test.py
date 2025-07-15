import pygame
from toppy2D import *

pygame.init()

screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

world = World(background_color="#555555")
player = Player(0, 0, controls=["w", "s", "a", "d"], name="guy", collision_rect=(0, 70, 100, 30), texture_surface=placeholder("#00FFFF"))

world.objects.extend([
    Object(100, 100, "regular"),
    Group(objects=[Object(200, 200, "in group 1"), Object(305, 200, "in group 2")]),
    Union(-100, 100, objects=[Object(0, 0, "in union 1"), Object(10, 10, "in union 2")]),
    player,
    Player(100, 0, controls=["y", "h", "g", "j"], name="ziom")
])
world.lock_camera("guy")
guy = world.get_objects_by_attrs({"name": "guy", "type": "Player"})[0]

while True:
    world.tick()

    world.draw(screen)