import pygame
from typing import overload
import copy
from pygame.math import Vector2
from pygame.color import Color
import math

pygame.init()

VER = "1.2.5"
NULL_SURFACE = pygame.Surface((100, 100))
NULL_SURFACE.fill("#FF00FF")
pygame.draw.rect(NULL_SURFACE, "#000000", (0, 0, 50, 50))
pygame.draw.rect(NULL_SURFACE, "#000000", (50, 50, 50, 50))

# ==============================================================================
# BASIC/HELPFUL FUNCTIONS
# ==============================================================================
# region

# region load_image different cases
@overload
def load_image(path: str):
    ...

@overload
def load_image(path: str, scale: float = None):
    ...

@overload
def load_image(path: str, size: tuple = None):
    ...
# endregion
def load_image(path: str, size: tuple = None):
    if isinstance(size, tuple):
        return pygame.transform.scale(pygame.image.load(path), size)
    elif isinstance(size, float) or isinstance(size, int):
        return pygame.transform.scale_by(pygame.image.load(path), size)
    elif size == None:
        return pygame.image.load(path)
    else:
        raise TypeError("image size/scale must be a tuple/float/int")

def scale_nostretch(surface: pygame.Surface, target_size: tuple[int, int]):
    """
    scale a surface to target size maintaining aspect ratio, adding black bars to vertical or horizontal edges
    """
    target_width, target_height = target_size
    original_width, original_height = surface.get_size()

    original_aspect = original_width / original_height
    target_aspect = target_width / target_height

    if original_aspect > target_aspect:
        new_width = target_width
        new_height = int(target_width / original_aspect)
    else:
        new_height = target_height
        new_width = int(target_height * original_aspect)
    
    scaled_surface = pygame.transform.smoothscale(surface, (new_width, new_height))

    result_surface = pygame.Surface((target_width, target_height))
    result_surface.fill((0, 0, 0))
    result_surface.blit(scaled_surface, ((target_width - new_width) // 2, (target_height - new_height) // 2))

    return result_surface

def draw_text(surface: pygame.Surface, text: str, pos: tuple[int, int], color: Color = "#FFFFFF", font: pygame.font.Font = pygame.font.Font(None, 25), background_color: Color = None, antialias: bool = True):
    x, y = pos
    lines = str(text).split("\n")
    for i in range(len(lines)):
        surface.blit(font.render(lines[i], antialias, color, background_color), (x, y + (i*(font.get_linesize()))))

# endregion

# ==============================================================================
# COLLISION FUNCTIONS
# ==============================================================================
# region

def point_line_collision(point: tuple[int, int], line_start: tuple[int, int], line_end: tuple[int, int], tolerance: int = 5):
    p = Vector2(point)
    a = Vector2(line_start)
    b = Vector2(line_end)

    ab = b - a
    ap = p - a

    t = max(0, min(1, ap.dot(ab) / ab.length_squared()))
    closest = a + t * ab
    return p.distance_to(closest) <= tolerance

def circle_line_collision(circle_center: tuple[int, int], radius: int, line_start: tuple[int, int], line_end: tuple[int, int]):
    p = Vector2(circle_center)
    a = Vector2(line_start)
    b = Vector2(line_end)

    ab = b - a
    ap = p - a

    # Project point onto the line (clamped between 0 and 1 to stay within segment)
    t = max(0, min(1, ap.dot(ab) / ab.length_squared()))
    closest = a + ab * t

    # Distance from circle center to closest point
    return p.distance_to(closest) <= radius

def circle_circle_collision(center1: tuple[int, int], radius1: int, center2: tuple[int, int], radius2: int):
    # Calculate distance between centers
    dx = center2[0] - center1[0]
    dy = center2[1] - center1[1]
    distance = math.hypot(dx, dy)

    # Check if distance is less than or equal to sum of radii
    return distance <= (radius1 + radius2)

def line_line_collision(line_start1: tuple[int, int], line_end1: tuple[int, int], line_start2: tuple[int, int], line_end2: tuple[int, int]):
    # Checks if line segments (a1–a2) and (b1–b2) intersect
    def ccw(p1, p2, p3):
        return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])
    return ccw(line_start1, line_start2, line_end2) != ccw(line_end1, line_start2, line_end2) and ccw(line_start1, line_end1, line_start2) != ccw(line_start1, line_end1, line_end2)

# endregion

# ==============================================================================
# CLASSES
# ==============================================================================
# region

class Base:
    def __init__(self, name):
        self.type = self.__class__.__name__
        self.name = (self.__class__.__name__ if name == None else name)

class Object(Base):
    def __init__(self, x: int, y: int, name: str = None, texture_surface: pygame.Surface = NULL_SURFACE, collision_rect:tuple = None):
        super().__init__(name)

        self.x = x
        self.y = y
        
        self.surface = texture_surface
        self.collider = collision_rect
    
    def get_rect(self):
        rect = self.surface.get_rect()
        rect.x, rect.y = self.x, self.y
        return rect
    
    def get_colliders(self) -> tuple[int, int, int, int]:
        """
        returns a list of rect tuples of the object's colliders, relative to the world:

        (x, y, w, h)
        """
        if self.collider == None:
            collider = self.surface.get_rect()
        else:
            collider = self.collider
        return [(self.x + collider[0], self.y + collider[1], collider[2], collider[3])]
    
    def info_str(self):
        """
        returns info about object
        """
        return f"({self.type}) {self.name} - {self.x};{self.y}"
    
    def draw(self, surface: pygame.Surface, camera_pos: tuple[int, int], debug_options: tuple[bool, bool, bool] = (True, False, False)) -> None:
        if debug_options[0]:
            surface.blit(self.surface, (self.x - camera_pos[0], self.y - camera_pos[1]))
        if debug_options[1]:
            pygame.draw.rect(surface, "#FF00FF", (self.x - camera_pos[0], self.y - camera_pos[1], self.surface.get_width(), self.surface.get_height()), 3)
        if debug_options[2]:
            colliders = self.get_colliders()
            for c in colliders:
                pygame.draw.rect(surface, "#FF0000", (c[0] - camera_pos[0], c[1] - camera_pos[1], c[2], c[3]), 4)        

class Player(Object):
    def __init__(self, x, y, name = None, texture_surface = NULL_SURFACE, collision_rect = None, speed = 5, controls: list[str, str, str, str] = []):
        """
        controls is a list with keyboard keys, examples:

        "w", "LEFT", "RETURN", "1", etc...

        if controls is not defined, you are expected to use the move() method manually
        """
        super().__init__(x, y, name, texture_surface, collision_rect)
        self.speed = speed
        self.controls = controls
    
    def change_controls(self, new_controls = [None, None, None, None]):
        for i in range(len(new_controls)):
            if new_controls[i] != None:
                self.controls[i] = new_controls[i]
    
    def control(self):
        bools = []
        keys = pygame.key.get_pressed()
        for key in self.controls:
            bools.append(keys[getattr(pygame, "K_"+key)])
        self.move(*bools)

    def move(self, up: bool, down: bool, left: bool, right: bool):
        self.x += (right - left) * self.speed
        self.y += (down - up) * self.speed

class Group(Base):
    def __init__(self, objects: list[Object] = [], name: str = None):
        """
        A Group holds multiple Objects in one place in the code for easy identifying.

        Objects in the group are not relative to any position, they are all free to move around separately.

        Group.get_pos() always returns (0, 0)
        """
        super().__init__(name)

        self.objects: list[Object] = objects
    
    def get_rect(self):
        if not self.objects:
            return pygame.Rect(0, 0, 0, 0)

        # Start with the rect of the first object
        first_rect = self.objects[0].get_rect()
        
        bounding_rect = first_rect.copy()

        for obj in self.objects[1:]:
            obj_rect = obj.get_rect()
            bounding_rect.union_ip(obj_rect)  # expands the bounding rect to include obj_rect

        return bounding_rect

    def get_colliders(self) -> tuple[int, int, int, int]:
        """
        returns a list of rect tuples of the object's colliders, relative to the world:

        (x, y, w, h)
        """
        colliders = []
        for object in self.objects:
            colliders.extend(object.get_colliders())
        return colliders

    def get_objects_by_attr(self, attr, value):
        """
        a multiple in one!

        you can get by name, type, x, etc.

        example usage:

        get_objects_by_attr("type", "Player")

        gets all objects in the group of type player.
        """
        out = []
        for object in self.objects:
            if getattr(object, attr) == value:
                out.append(object)
        
        return out
    
    def extract_objects(self):
        def extract(group: Group):
            out = []
            for object in group.objects:
                if object.type == "Group":
                    out.extend(extract(object))
                else:
                    out.append(object)
            return out
        
        working_list = []
        for object in self.objects:
            if object.type == "Group":
                working_list.extend(extract(object))
            else:
                working_list.append(object)
        return working_list
    
    def info_str(self):
        out = f"({self.type}) {self.name}{f' - {self.x};{self.y}' if hasattr(self, 'x') else ''}"
        for i in range(len(self.objects)):
            for line in self.objects[i].info_str().split("\n"):
                if i == len(self.objects)-1 and line[0] != ' ':
                    out += "\n └" + line
                elif i == len(self.objects)-1:
                    out += "\n  " + line
                elif line[0] == ' ':
                    out += "\n │" + line
                else:
                    out += "\n ├" + line
        
        return out

    def draw(self, surface: pygame.Surface, camera_pos, debug_options: tuple[bool, bool, bool] = (True, False, False)):
        working_list = self.extract_objects()
        length = len(working_list)
        
        for _ in range(length):
            smallest = working_list[0]
            smallest_index = 0

            for i in range(len(working_list)):
                if working_list[i].y+working_list[i].get_rect().h < smallest.y+smallest.get_rect().h:
                    smallest = working_list[i]
                    smallest_index = i

            smallest.draw(surface, camera_pos, debug_options)
            del working_list[smallest_index]

class Union(Group):
    def __init__(self, x: int, y: int, objects = [], name = None):
        super().__init__(objects, name)
        self.x = x
        self.y = y
    
    def transform_objects(self):
        transformed = []
        for object in self.objects:
            temp = copy.copy(object)
            temp.x += self.x
            temp.y += self.y
            transformed.append(temp)
        return transformed
    
    def get_colliders(self):
        temp = self.objects.copy()
        self.objects = self.transform_objects()
        super().get_colliders()
        self.objects = temp.copy()
    
    def draw(self, surface, camera_pos, debug_options = (True, False, False)):
        temp = self.objects.copy()
        self.objects = self.transform_objects()
        super().draw(surface, camera_pos, debug_options)
        self.objects = temp.copy()

class World(Group):
    def __init__(self, background_color="#000000", FPS=30):
        super().__init__([], "World")
        self.camera_x = 0
        self.camera_y = 0
        self.camera_lock = None
        
        self.FPS = FPS
        self.clock = pygame.time.Clock()

        self.handled_events = [
            ("QUIT", {}, exit),
            ("KEYDOWN", {"key": pygame.K_BACKQUOTE}, self.toggle_debug)
        ]

        self.debug = False
        self.background_color = background_color
    
    def add_event_handle(self, event:str, attr_conditions:dict, func):
        """
        Appends a tuple (event, attr_conditions, function) to handled_events if it doesnt exist in the list

        Here is what each element does lead by an example `("KEYDOWN", {"key":pygame.K_SPACE}, print)`

        the above tuple:

        - on World.tick() checks for event pygame.KEYDOWN

        - check if the Event attributes (keys in dict) match the values of the dict

        - if the above succeeds, runs print()
        """

        if (event, attr_conditions, func) not in self.handled_events:
            self.handled_events.append((event, attr_conditions, func))
    
    def toggle_debug(self):
        self.debug = not self.debug

    def lock_camera(self, player_name: str):
        self.camera_lock = player_name
    
    def unlock_camera(self):
        self.camera_lock = None
    
    def tick(self):
        """
        Handles the following:

        - maintaining FPS

        - players

        - events (pygame.QUIT exits the program by default)
        """
        
        self.clock.tick(self.FPS)
        for object in self.objects:
            if object.type == "Player":
                if len(object.controls) >= 4:
                    object.control()
                
                if object.name == self.camera_lock:
                    self.camera_x, self.camera_y = object.x + (object.surface.get_rect().w//2), object.y + (object.surface.get_rect().h//2)
        
        for event in pygame.event.get():
            for handled in self.handled_events:
                if event.type == getattr(pygame, handled[0]):
                    proceed = True
                    for attribute in handled[1]:
                        if getattr(event, attribute) != handled[1][attribute]:
                            proceed = False
                    if proceed:
                        handled[2]()

    def draw(self, surface: pygame.Surface, debug_options: tuple[bool, bool, bool] = (True, False, False)):
        # center camera pos
        camera_pos = (self.camera_x - (surface.get_width()//2), self.camera_y - (surface.get_height()//2))

        surface.fill(self.background_color)
        super().draw(surface, camera_pos, debug_options)

        if self.debug:
            debug_output = f"""FPS: {round(self.clock.get_fps())}
{self.info_str()}"""

            draw_text(surface, debug_output, (0, 0), background_color="#000000", font=pygame.font.SysFont("Consolas", 15))
        pygame.display.update()

#endregion