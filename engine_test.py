import pygame
from toppy2D import *

pygame.init()

window = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
screen = pygame.Surface((500, 500))

world = World("#555555")
world.objects.extend([
    Object(100, 100),
    Group(objects=[Object(200, 200), Object(305, 200)]),
    Union(-100, 100, objects=[Object(0, 0), Object(10, 10)]),
    Player(0, 0, controls=["w", "s", "a", "d"], name="guy"),
    Player(100, 0, controls=["y", "h", "g", "j"], name="ziom")
])
world.lock_camera("guy")
world.add_event_handle("KEYDOWN", {"key": pygame.K_BACKQUOTE}, world.toggle_debug)

while True:
    world.tick()    

    world.draw(screen, (True, True, True))
    window.blit(scale_nostretch(screen, window.get_size()), (0, 0))