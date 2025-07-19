import pygame
from typing import overload
import copy
from pygame.math import Vector2
from pygame.color import Color
import math

pygame.init()

VER = "1.8.3"

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

def placeholder(color1 = "#FF00FF", color2 = "#000000", size = (100, 100)) -> pygame.Surface:
    surface = pygame.Surface(size)
    surface.fill(color1)
    pygame.draw.rect(surface, color2, (0, 0, surface.get_width()//2, surface.get_height()//2))
    pygame.draw.rect(surface, color2, (surface.get_width()//2, surface.get_height()//2, surface.get_width(), surface.get_height()))

    return surface

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

    result_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
    result_surface.blit(scaled_surface, ((target_width - new_width) // 2, (target_height - new_height) // 2))

    return result_surface

def apply_alpha(surface: pygame.Surface, alpha: int):
    new = surface.convert_alpha()
    alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    alpha_surface.fill((255, 255, 255, alpha))
    new.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new

def overlay_colour(surface: pygame.Surface, RGB_color, strength: int):
    copy = surface.copy()
    dark_overlay = pygame.Surface(copy.get_size()).convert_alpha()
    dark_overlay.fill((*RGB_color, strength))
    copy.blit(dark_overlay, (0, 0))
    return copy

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
# GUI
# ==============================================================================
# region

class Dialog:
    def __init__(self):
        self.title = ""

        self.visible = False
        self.buffer_text = ""
        self.showing_text = ""

        self.typewriter_stage = 0
        self.typewriter_finished = False
        self.typewrite_step = 1

        self.set_defaults()

    def set_defaults(self):
        """
        set all styling attributes to default values
        """
        # its all here so you can configure it later with eg. instance.text_color = "#FF0000" or instance.BG_color = color.RED
        bold = pygame.font.SysFont("arial", 30)
        bold.set_bold(True)
        self.title_font = bold

        self.desc_font = pygame.font.SysFont("arial", 20)

        italic = pygame.font.SysFont("arial", 14)
        italic.set_italic(True)
        self.skip_font = italic

        self.line_gap = 3
        
        self.BG_color = "#000000"
        self.title_color = "#EEEEEE"
        self.text_color = "#FFFFFF"
        self.skip_color = "#BBBBBB"
        self.border_color = "#FFFFFF"

        self.padding = 15
        self.border_offset = 5
        self.border_radius = 20
        self.border_width = 3
        self.height = 200

        self.skip_key = "SPACE"
    
    def set_config(self, config: dict):
        """
        Here are the default settings, and attributes you can modify:

        **fonts:**
        - title_font = arial, size 30, bold
        - desc_font = arial, size 20
        - skip_font = arial, size 14, italic
        - line_gap = 3
        
        **colors:**
        - BG_color = "#000000"
        - title_color = "#EEEEEE"
        - text_color = "#FFFFFF"
        - skip_color = "#BBBBBB"
        - border_color = "#FFFFFF"

        **dimensions:**
        - padding = 15
        - border_offset = 5
        - border_radius = 20
        - border_width = 3
        - height = 200

        **misc:**
        - skip_key = "SPACE"
        """
        for key in config:
            setattr(self, key, config[key])

    def show_text(self, title:str, text:str):
        """
        Shows dialog box, and automatically starts the typewriting effect.
        """
        self.hide()
        self.title = title
        self.visible = True
        self.buffer_text = text
        self.typewriter_finished = False

    def hide(self):
        """
        Hides dialog box
        """
        self.visible = False
        self.title = ""
        self.buffer_text = ""
        self.showing_text = ""
        self.typewriter_stage = 0
        self.typewriter_finished = True # did it finish typing?

    def skip(self):
        """
        Skips typewriting effect if it's still going, if typewriter already finished executes hideText()
        """
        if self.typewriter_stage < len(self.buffer_text):
            self.showing_text = self.buffer_text
            self.typewriter_stage = len(self.buffer_text)
        else:
            self.hide()

    def draw(self, screen:pygame.Surface):
        if self.visible:
            # progresses dialog typewriter effect
            if self.typewriter_stage < len(self.buffer_text):
                self.typewriter_stage += self.typewrite_step
                self.showing_text = self.buffer_text[:int(self.typewriter_stage)]
            else:
                self.typewriter_finished = True


            # draw dialog box

            rect = (
                self.border_offset, screen.get_height() - self.border_offset*2 - self.height,
                screen.get_width()-self.border_offset*2, self.height
            )
            pygame.draw.rect(screen, self.BG_color, rect, 0, self.border_radius)
            pygame.draw.rect(screen, self.border_color, rect, self.border_width, self.border_radius)

            # draw text
            screen.blit(self.title_font.render(self.title, True, self.title_color), (self.border_offset + self.padding, screen.get_height() - self.border_offset*2 - self.height + self.padding))
            description = self.showing_text.split("\n")
            for i in range(len(description)):
                screen.blit(self.desc_font.render(description[i], True, self.text_color), (
                    self.border_offset + self.padding,
                    (screen.get_height() - self.border_offset*2 - self.height + self.padding + self.title_font.get_height() + self.line_gap) + (self.desc_font.get_height()+self.line_gap)*i
                ))

            # draw skip hint text
            skip_text_width, skip_text_height = self.skip_font.render(f"Press '{self.skip_key}' to close...", True, self.skip_color).get_size()
            placement = (
                screen.get_width() - self.border_offset - self.padding - skip_text_width,
                screen.get_height() - self.border_offset - self.padding - skip_text_height
            )
            if self.typewriter_finished:
                screen.blit(self.skip_font.render(f"Press '{self.skip_key}' to close...", True, self.skip_color), placement)
            else:
                screen.blit(self.skip_font.render(f"Press '{self.skip_key}' to skip...", True, self.skip_color), placement)

class GUIObject:
    def __init__(self, position: tuple[float, int, float, int], size: tuple[float, int, float, int], anchor_point: tuple[float, float] = (0, 0), name: str = None, children: list["GUIObject"] = None):
        self.position = position
        self.size = size
        self.anchor_point = anchor_point

        self.children: list[GUIObject] = children if children != None else []

        self.hidden = False
        self.type = self.__class__.__name__
        self.name = name if name != None else self.__class__.__name__

    def toggle(self, on_off: bool = None):
        if on_off == None:
            self.hidden = not self.hidden
        else:
            self.hidden = not on_off

    def get_all_by_type(self, type) -> list["GUIObject"]:
        out = []
        for object in self.children:
            if object.type == type:
                out.append(object)
        return out
    
    def get_by_type(self, type) -> "GUIObject":
        for object in self.children:
            if object.type == type:
                return object
    
    def get_all_by_name(self, name) -> list["GUIObject"]:
        out = []
        for object in self.children:
            if object.name == name:
                out.append(object)
        return out
    
    def get_by_name(self, name) -> "GUIObject":
        for object in self.children:
            if object.name == name:
                return object

    def add_child(self, child: "GUIObject"):
        self.children.append(child)

    def prepare(self, surface: pygame.Surface, position: tuple[int, int]):
        pass

    def draw(self, surface: pygame.Surface, position_offset: tuple[int, int] = (0, 0)):
        if self.hidden:
            return
        size = (
            surface.get_width()*self.size[0] + self.size[1],
            surface.get_height()*self.size[2] + self.size[3]
        )

        position = (
            surface.get_width()*self.position[0] + self.position[1] - self.anchor_point[0]*size[0],
            surface.get_height()*self.position[2] + self.position[3] - self.anchor_point[1]*size[1]
        )

        element = pygame.Surface(size, pygame.SRCALPHA)

        self.prepare(element, (position[0] + position_offset[0], position[1] + position_offset[1]))

        for child in self.children:
            child.draw(element, (position[0] + position_offset[0], position[1] + position_offset[1]))
        
        surface.blit(element, position)

class Frame(GUIObject):
    def __init__(self, position, size, anchor_point = (0, 0), name = None, children = None, background_color = "#FFFFFF"):
        super().__init__(position, size, anchor_point, name, children)
        self.background_color = background_color     
    
    def prepare(self, surface: pygame.Surface, position: tuple[int, int]):
        surface.fill(self.background_color)

class SurfaceBox(GUIObject):
    def __init__(self, position, size, anchor_point = (0, 0), name = None, children = None, surface: pygame.Surface = None, stretch: bool = True):
        super().__init__(position, size, anchor_point, name, children)
        self.surface = surface if surface != None else placeholder()
        self.stretch = stretch
    
    def prepare(self, surface: pygame.Surface, position):
        surface.blit(pygame.transform.scale(self.surface, surface.get_size()) if self.stretch else scale_nostretch(self.surface, surface.get_size()), (0, 0))

class TextLabel(SurfaceBox):
    def __init__(self, position, size, anchor_point=(0, 0), name=None, children=None, text: str = "TextLabel", color = "#000000", background_color = "#FFFFFF"):
        self.text = text
        self.color = color
        self.background_color = background_color
        self.font = pygame.font.SysFont("arial", 25)
        self.padding = 2
        
        super().__init__(position, size, anchor_point, name, children)
    
    def prepare(self, surface, position):
        self.surface = pygame.Surface(surface.get_size())
        self.surface.fill(self.background_color)
        draw_text(self.surface, self.text, (self.padding, self.padding), self.color, self.font)
        super().prepare(surface, position)

class SurfaceButton(SurfaceBox):
    def __init__(self, position, size, anchor_point=(0, 0), name=None, children=None, surface = None, onclick = lambda: None, stretch = True):
        super().__init__(position, size, anchor_point, name, children, surface, stretch)
        self.pressed = False
        self.hovering = False
        self.lastpressed = False
        self.onclick = onclick

        self.hover_intensity = 30
        self.click_intensity = 60

    def prepare(self, surface, position):
        mouse = pygame.mouse.get_pos()
        self.hovering = surface.get_rect().collidepoint(mouse[0] - position[0], mouse[1] - position[1])
        self.pressed = pygame.mouse.get_pressed()[0] and surface.get_rect().collidepoint(mouse[0] - position[0], mouse[1] - position[1])
        
        if self.hovering:
            temp = self.surface.copy()
            if self.pressed:
                self.surface = overlay_colour(self.surface, (0, 0, 0), self.click_intensity)
                if not self.lastpressed:
                    self.onclick()
            else:
                self.surface = overlay_colour(self.surface, (0, 0, 0), self.hover_intensity)
            super().prepare(surface, position)
            self.surface = temp.copy()
            
        else:
            super().prepare(surface, position)

        self.lastpressed = self.pressed

class TextButton(SurfaceButton):
    def __init__(self, position, size, anchor_point=(0, 0), name=None, children=None, text: str = "TextLabel", color = "#000000", background_color = "#FFFFFF", onclick = lambda: None):
        self.text = text
        self.color = color
        self.background_color = background_color
        self.font = pygame.font.SysFont("arial", 25)
        self.padding = 2

        super().__init__(position, size, anchor_point, name, children, None, onclick)

    def prepare(self, surface, position):
        self.surface = pygame.Surface(surface.get_size())
        self.surface.fill(self.background_color)
        draw_text(self.surface, self.text, (self.padding, self.padding), self.color, self.font)
        super().prepare(surface, position)

class GUI:
    def __init__(self):
        self.dialog = Dialog()

        self.children: list[GUIObject] = []
    
    def add_child(self, child):
        self.children.append(child)
    
    def get_all_by_type(self, type) -> list["GUIObject"]:
        out = []
        for object in self.children:
            if object.type == type:
                out.append(object)
        return out
    
    def get_by_type(self, type) -> "GUIObject":
        for object in self.children:
            if object.type == type:
                return object
    
    def get_all_by_name(self, name) -> list["GUIObject"]:
        out = []
        for object in self.children:
            if object.name == name:
                out.append(object)
        return out
    
    def get_by_name(self, name) -> "GUIObject":
        for object in self.children:
            if object.name == name:
                return object

    def draw(self, surface):
        for object in self.children:
            object.draw(surface)

        self.dialog.draw(surface)

# endregion

# ==============================================================================
# OBJECTS
# ==============================================================================
# region

class Base:
    def __init__(self, name):
        self.type = self.__class__.__name__
        self.name = (self.__class__.__name__ if name == None else name)
    
    def log(self, text: str):
        print(f"[{self.name}] {text}")

# ==============================================================================
# SINGULAR
# ==============================================================================
# region

class Object(Base):
    def __init__(self, x: int, y: int, name: str = None, texture_surface: pygame.Surface = None, collision_rect:tuple = None):
        super().__init__(name)

        self.x = x
        self.y = y

        self.opacity = 255
        self.solid = True
        
        self.surface = texture_surface if texture_surface != None else placeholder()
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
    
    def draw(self, surface: pygame.Surface):
        debug_options = World.world_instance.draw_debug
        offset_x, offset_y = World.world_instance.surface.get_width()//2, World.world_instance.surface.get_height()//2
        if debug_options[0]:
            surface.blit(apply_alpha(self.surface, self.opacity), (self.x + offset_x, self.y + offset_y))
        if debug_options[2]:
            collider = self.get_colliders()[0]
            pygame.draw.rect(surface, "#FF0000", (collider[0] + offset_x, collider[1] + offset_y, *collider[2:]), 4)
        if debug_options[1]:
            pygame.draw.rect(surface, "#FFFF00", (self.x + offset_x, self.y + offset_y, self.surface.get_width(), self.surface.get_height()), 2)
           

class Player(Object):
    def __init__(self, x, y, name = None, texture_surface = None, collision_rect = None, speed: int = 5, controls: list[str, str, str, str] = None):
        """
        controls is a list with keyboard keys, examples:

        "w", "LEFT", "RETURN", "1", etc...

        if controls is not defined, you are expected to use the move() method manually
        """
        super().__init__(x, y, name, texture_surface, collision_rect)
        self.speed = speed
        self.controls = controls if controls != None else []
    
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
        colliders = Group(World.world_instance.get_all_by_not_attr("type", "Player")).get_colliders()
        world_size = World.world_instance.size
        for _ in range(self.speed):
            self.x += (right - left)
            if pygame.Rect(self.get_colliders()[0]).collidelist(colliders) != -1 or not -(world_size[0]//2) < self.get_colliders()[0][0] < world_size[0]//2 - self.get_colliders()[0][2]:
                self.x -= (right - left)
                break

        for _ in range(self.speed):
            self.y += (down - up)
            if pygame.Rect(self.get_colliders()[0]).collidelist(colliders) != -1 or not -(world_size[1]//2) < self.get_colliders()[0][1] < world_size[1]//2 - self.get_colliders()[0][3]:
                self.y -= (down - up)
                break

# endregion

# ==============================================================================
# GROUP
# ==============================================================================
# region

class Group(Base):
    """
    A Group holds multiple Objects in one place in the code for easy identifying.

    Objects in the group are not relative to any position, they are all free to move around separately.

    Group.get_pos() always returns (0, 0)
    """
    def __init__(self, objects: list[Object], name: str = None):
        super().__init__(name)

        self.objects: list[Object] = objects if objects != None else []
    
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

    def get_all_by_attr(self, attribute, value):
        """
        a multiple in one!

        you can get by name, type, x, etc.

        example usage:

        get_objects_by_attr("type", "Player")

        gets all objects in the group of type player.
        """
        out = []
        for object in self.objects:
            if getattr(object, attribute) == value:
                out.append(object)
        
        return out

    def get_by_attr(self, attribute, value):
        for object in self.objects:
            if getattr(object, attribute) == value:
                return object

    def get_all_by_not_attr(self, attribute, value):
        """
        works the same as get_objects_by_attr, except only takes objects that dont match attribute
        """
        out = []
        for object in self.objects:
            if getattr(object, attribute) != value:
                out.append(object)
        
        return out
    
    def get_by_not_attr(self, attribute, value):
        for object in self.objects:
            if getattr(object, attribute) != value:
                return object
    
    def get_all_by_attrs(self, attributes_values: dict):
        """
        works the same as get_objects_by_attr, but with multiple attributes as keys, and their values as values, in a dict
        """
        out = []
        for object in self.objects:
            passes = True
            for attr in attributes_values:
                if getattr(object, attr) != attributes_values[attr]:
                    passes = False
            if passes:
                out.append(object)
        return out

    def get_by_attrs(self, attributes_values: dict):
        for object in self.objects:
            passes = True
            for attr in attributes_values:
                if getattr(object, attr) != attributes_values[attr]:
                    passes = False
            if passes:
                return object
    
    def get_all_by_not_attrs(self, attributes_values: dict):
        """
        works the same as get_objects_by_attrs, but only takes objects that dont match all the attributes
        """
        out = []
        for object in self.objects:
            passes = True
            for attr in attributes_values:
                if getattr(object, attr) == attributes_values[attr]:
                    passes = False
            if passes:
                out.append(object)
        return out

    def get_by_not_attrs(self, attributes_values: dict):
        for object in self.objects:
            passes = True
            for attr in attributes_values:
                if getattr(object, attr) == attributes_values[attr]:
                    passes = False
            if passes:
                return object
            
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

    def draw(self, surface: pygame.Surface):
        working_list = self.extract_objects()
        length = len(working_list)
        
        for _ in range(length):
            smallest = working_list[0]
            smallest_index = 0

            for i in range(len(working_list)):
                if working_list[i].y+working_list[i].get_rect().h < smallest.y+smallest.get_rect().h:
                    smallest = working_list[i]
                    smallest_index = i

            smallest.draw(surface)
            del working_list[smallest_index]

class Union(Group):
    def __init__(self, x: int, y: int, objects = None, name = None):
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
        out = super().get_colliders()
        self.objects = temp.copy()
        return out
    
    def draw(self, surface):
        temp = self.objects.copy()
        self.objects = self.transform_objects()
        super().draw(surface)
        self.objects = temp.copy()

# endregion

# ==============================================================================
# 「THE WORLD」
# ==============================================================================

class World(Group):
    world_instance = None
    def __init__(self, size: tuple[int, int] = (1000, 1000), background_color="#000000", FPS=30):
        super().__init__([], "World")

        self.size = size
        self.surface = pygame.Surface((self.size[0]+1000, self.size[1]+1000))
        
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1
        self.camera_zoom_limits = (0.8, 1.3)
        self.focused_on = None

        self.GUI = GUI()
        
        self.FPS = FPS
        self.clock = pygame.time.Clock()

        self.handled_events = [
            ("QUIT", {}, exit),
            ("KEYDOWN", {"key": pygame.K_BACKQUOTE}, self.toggle_debug),
        ]

        self.debug = False
        self.draw_debug = (True, False, False)
        self.background_color = background_color

        World.world_instance = self
        self.log("World initialized. Have fun using Toppy2D!")
        self.log("Remember the keys assigned by default: BACKQUOTE (handled_events, toggles debug), SPACE (dialog skip, World.GUI.dialog.skip_key)")
    
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
        self.draw_debug = (True, True, True) if self.debug else (True, False, False)

    def focus_on(self, object: Object):
        self.focused_on = object
    
    def unfocus(self):
        self.focused_on = None
    
    def set_zoom(self, amount: float = 1):
        self.camera_zoom = amount
    
    def change_zoom(self, amount):
        self.camera_zoom += amount
    
    def tick(self):
        """
        Handles the following:

        - maintaining FPS

        - players

        - events (pygame.QUIT exits the program by default, pygame.KEYDOWN and key is pygame.K_BACKQUOTE toggles debug)

        - dialog skip (!WATCH OUT! - SPACE by default)
        """
        
        self.clock.tick(self.FPS)
        for object in self.objects:
            if object.type == "Player":
                # player controls
                if len(object.controls) >= 4:
                    object.control()
                
                # camera lock

        self.camera_x, self.camera_y = self.focused_on.x + (self.focused_on.surface.get_rect().w//2), self.focused_on.y + (self.focused_on.surface.get_rect().h//2)
        
        # handling events
        for event in pygame.event.get():
            for handled in self.handled_events:
                if event.type == getattr(pygame, handled[0]):
                    proceed = True
                    for attribute in handled[1]:
                        if getattr(event, attribute) != handled[1][attribute]:
                            proceed = False
                    if proceed:
                        handled[2]()
            
            # handle dialog skip event specifically
            if event.type == pygame.KEYDOWN and event.key == getattr(pygame, f"K_{self.GUI.dialog.skip_key}"):
                self.GUI.dialog.skip()

    def draw(self, surface: pygame.Surface):
        if self.camera_zoom < self.camera_zoom_limits[0]:
            self.camera_zoom = self.camera_zoom_limits[0]
        if self.camera_zoom > self.camera_zoom_limits[1]:
            self.camera_zoom = self.camera_zoom_limits[1]
        
        surface.fill("#000000")
        self.surface.fill("#000000")

        pygame.draw.rect(self.surface, self.background_color, (self.surface.get_width()//2 - self.size[0]//2, self.surface.get_height()//2 - self.size[1]//2, *self.size))

        super().draw(self.surface)
        surface.blit(pygame.transform.scale_by(self.surface, self.camera_zoom**3), (
            (-self.camera_x - self.surface.get_width()//2)*(self.camera_zoom**3) + surface.get_width()//2,
            (-self.camera_y - self.surface.get_height()//2)*(self.camera_zoom**3) + surface.get_height()//2
        ))

        self.GUI.draw(surface)

        if self.debug:
            debug_output = f"""FPS: {round(self.clock.get_fps())}
camera: ({self.camera_x}, {self.camera_y}), x{self.camera_zoom}, focused on "{self.focused_on.name}" ({self.focused_on.type})
{self.info_str()}"""
            draw_text(surface, debug_output, (1, 1), background_color="#000000", font=pygame.font.SysFont("Consolas", 15))


        pygame.display.update()

#endregion