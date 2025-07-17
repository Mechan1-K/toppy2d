import pygame
from toppy2D import *

pygame.init()

screen = pygame.display.set_mode((700, 500), pygame.RESIZABLE)

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
guy = world.get_by_attrs({"name": "guy", "type": "Player"})

world.GUI.dialog.typewrite_step = 0.2
world.add_event_handle("KEYDOWN", {"key": pygame.K_1}, lambda: world.GUI.dialog.show_text("Markiplier", "hello everybody my name is Markiplier!\nAnd in todays video we will be testing out the length of this dialog box and see if it is big or not at all!"))

world.GUI.add_child(Frame(
    (0.5, 0, 0.5, 0), (0.5, 0, 0.5, 0), (0.5, 0.5), "TestFrame",
    [SurfaceButton(
        (0.5, 0, 0.5, 0), (0.5, 0, 0.5, 0), (0.5, 0.5), "TestFrameInFrame", [], onclick=lambda: print("clicked")
    )]
))

while True:
    world.tick()

    world.draw(screen)