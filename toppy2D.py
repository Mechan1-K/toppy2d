import pygame
import random
from typing import overload
import copy

VER = "0.4.1"
NULL_SURFACE = pygame.Surface((100, 100))
NULL_SURFACE.fill("#FF00FF")
pygame.draw.rect(NULL_SURFACE, "#000000", (0, 0, 50, 50))
pygame.draw.rect(NULL_SURFACE, "#000000", (50, 50, 50, 50))

# ==============================================================================
# BASIC/HELPFUL FUNCTIONS
# ==============================================================================
# region

generated_ids = []
def generate_id(length=8):
    out = ""
    while out in generated_ids:
        out = ""
        for _ in range(length):
            out += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    
    generated_ids.append(out)
    return out

@overload
def load_image(path: str):
    ...

@overload
def load_image(path: str, scale: float = None):
    ...

@overload
def load_image(path: str, size: tuple = None):
    ...

def load_image(path: str, size: tuple = None):
    if isinstance(size, tuple):
        return pygame.transform.scale(pygame.image.load(path), size)
    elif isinstance(size, float):
        return pygame.transform.scale_by(pygame.image.load(path), size)
    elif size == None:
        return pygame.image.load(path)
    else:
        raise TypeError("image size/scale must be a tuple/float/int")

# endregion

# ==============================================================================
# CLASSES
# ==============================================================================
# region

class Object:
    def __init__(self, x: int, y: int, name: str = None, texture_surface: pygame.Surface = NULL_SURFACE, collision_rect:tuple = None):
        self.name = ("Object" if name == None else name)

        self.x = x
        self.y = y
        
        self.surface = texture_surface
        self.collider = collision_rect
    
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
    
    def draw(self, surface: pygame.Surface, camera_pos: tuple[int, int], debug_options: tuple[bool, bool, bool] = (True, False, False)) -> None:
        if debug_options[0]:
            surface.blit(self.surface, (self.x + camera_pos[0], self.y + camera_pos[1]))
        if debug_options[1]:
            pygame.draw.rect(surface, "#FF00FF", (self.x + camera_pos[0], self.y + camera_pos[1], self.surface.get_width(), self.surface.get_height()), 3)
        if debug_options[2]:
            colliders = self.get_colliders()
            for c in colliders:
                pygame.draw.rect(surface, "#FF0000", (c[0] + camera_pos[0], c[1] + camera_pos[1], c[2], c[3]), 4)        

class Group:
    def __init__(self, name: str = None, objects: list[Object] = []):
        """
        A Group holds multiple Objects in one place in the code for easy identifying.

        Objects in the group are not relative to any position, they are all free to move around separately.

        Group.get_pos() always returns (0, 0)
        """
        self.name = (self.__class__.__name__ if name == None else name)
        self.objects: list[Object] = objects

    def get_colliders(self) -> tuple[int, int, int, int]:
        """
        returns a list of rect tuples of the object's colliders, relative to the world:

        (x, y, w, h)
        """
        colliders = []
        for object in self.objects:
            colliders.extend(object.get_colliders())
        return colliders

    def get_objects_by_name(self, name: str):
        out = []
        for object in self.objects:
            if object.name == name:
                out.append(object)
    
    def draw(self, surface: pygame.Surface, camera_pos, debug_options: tuple[bool, bool, bool] = (True, False, False)):
        for object in self.objects:
            object.draw(surface, camera_pos, debug_options)

class Union(Group):
    def __init__(self, x: int, y: int, name = None, objects = []):
        super().__init__(name, objects)
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
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.objects: list[Object] = []
    
    def draw(self, surface: pygame.Surface, debug_options: tuple[bool, bool, bool] = (True, False, False)):
        # center camera pos
        camera_pos = (self.camera_x + (surface.get_width()//2), self.camera_y + (surface.get_height()//2))

        for object in self.objects:
            object.draw(surface, camera_pos, debug_options)

#endregion