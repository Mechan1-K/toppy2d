import pygame
from toppy2D import *

pygame.init()

screen = pygame.display.set_mode((700, 600), pygame.RESIZABLE)

world = World(background_color="#555555", size=(3000, 200))
# player = Player(0, 0, controls=["w", "s", "a", "d"], name="guy", collision_rect=(0, 70, 100, 30), texture_surface=placeholder("#00FFFF"))

# world.objects.extend([
#     Object(100, 100, "regular"),
#     Group(objects=[Object(200, 200, "in group 1"), Object(305, 200, "in group 2")]),
#     Union(-100, 100, objects=[Object(0, 0, "in union 1"), Object(10, 10, "in union 2")]),
#     player,
#     Player(100, 0, controls=["y", "h", "g", "j"], name="ziom")
# ])
# world.focus_on(player)

world.GUI.dialog.typewrite_step = 0.2
world.add_event_handle(pygame.KEYDOWN, {"key": pygame.K_1}, lambda _: world.GUI.dialog.show_text("Markiplier", "hello everybody my name is Markiplier!\nAnd in todays video we will be testing out the length of this dialog box and see if it is big or not at all!"))
world.add_event_handle(pygame.MOUSEWHEEL, {}, lambda event: world.change_zoom(0.05*event.y))

world.GUI.add_children([
    Frame("Menu", (0.5, 0, 0.5, 0), (0.5, 0, 0.5, 0), (0.5, 0.5), children=[
        TextButton(
            "Exit", (0.9, 0, 0, 0), (0.1, 0, 0.1, 0), (0, 0), "XX").setup("X", "#FFFFFF", "#EE0000", on_click=lambda: world.GUI.get_by_name("Menu").toggle(False))
    ]),
    TextButton("OpenMenu", (0, 0, 0.5, 0), (0, 100, 0, 30), (0, 0.5)).setup("Menu", background_color="#11CCEE", on_click=lambda: world.GUI.get_by_name("Menu").toggle()
    )
])

while True:
    world.tick()
    world.draw(screen)