import pygame
from toppy2D import *

pygame.init()

screen = pygame.display.set_mode((700, 500), pygame.RESIZABLE)

world = World(background_color="#555555", size=(3000, 200))
player = Player(0, 0, controls=["w", "s", "a", "d"], name="guy", collision_rect=(0, 70, 100, 30), texture_surface=placeholder("#00FFFF"))

world.objects.extend([
    Object(100, 100, "regular"),
    Group(objects=[Object(200, 200, "in group 1"), Object(305, 200, "in group 2")]),
    Union(-100, 100, objects=[Object(0, 0, "in union 1"), Object(10, 10, "in union 2")]),
    player,
    Player(100, 0, controls=["y", "h", "g", "j"], name="ziom")
])
world.focus_on(player)
guy = world.get_by_attrs({"name": "guy", "type": "Player"})

world.GUI.dialog.typewrite_step = 0.2
world.add_event_handle(pygame.KEYDOWN, {"key": pygame.K_1}, lambda _: world.GUI.dialog.show_text("Markiplier", "hello everybody my name is Markiplier!\nAnd in todays video we will be testing out the length of this dialog box and see if it is big or not at all!"))
world.add_event_handle(pygame.MOUSEWHEEL, {}, lambda event: world.change_zoom(0.05*event.y))

world.GUI.add_child(
    Frame((0.5, 0, 0.5, 0), (0.5, 0, 0.5, 0), (0.5, 0.5), "Menu", [
        TextButton(
            (1, -30, 0, 0), (0, 30, 0, 30), (0, 0), "Exit", [], "X", background_color="#FF0000"
        )
    ])
)
world.GUI.get_by_name("Menu").get_by_name("Exit").onclick = lambda: world.GUI.get_by_name("Menu").toggle(False)

world.GUI.add_child(
    TextButton((0, 0, 0.5, 0), (0, 100, 0, 30), (0, 0.5),
               "OpenMenu", None, "Menu", background_color="#11CCEE", onclick=world.GUI.get_by_name("Menu").toggle
    )
)

world.GUI.get_by_name("Menu").hidden = True

while True:
    world.tick()
    world.debug_value("test", world.camera_zoom_limits)
    world.draw(screen)