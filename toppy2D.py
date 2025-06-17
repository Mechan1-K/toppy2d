import pygame
import random
from typing import overload

VER = 0.1

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

def load_image(path: str, size: tuple = None):
    if isinstance(size, tuple):
        return pygame.transform.scale(pygame.image.load(path), size)
    elif isinstance(size, float):
        return pygame.transform.scale_by(pygame.image.load(path))
    elif size == None:
        return pygame.image.load(path)
    else:
        raise TypeError("image size/scale must be a tuple/float/int")

class Object:
    def __init__(self, x, y, display_surface: pygame.Surface, collision_rect:tuple = None):
        self.__id = generate_id()

        self.x = x
        self.y = y

        self.surface = display_surface
        self.collider = collision_rect

        self.__delete = False
    
    def get_collider(self) -> tuple[int, int, int, int]:
        """
        returns a rect tuple of the object's collider, relative to the world:

        (x, y, w, h)
        """
        if self.collider == None:
            collider = self.surface.get_rect()
        else:
            collider = self.collider
        return (self.x + collider[0], self.y + collider[1], collider[2], collider[3])
    
    def get_pos(self) -> tuple[int, int]:
        """
        returns a tuple of the object's position, relative to the world:

        (x, y)
        """
        return self.x, self.y
    
    def delete(self):
        self.__delete = True
    
    def is_deleted(self):
        return self.__delete
    
    def get_id(self):
        return self.__id
    
    def draw(self, surface: pygame.Surface, camera_pos: tuple[int, int], debug: bool = False) -> None:
        if debug:
            c = self.get_collider()
            pygame.draw.rect(surface, "#FF00FF", (self.x + camera_pos[0], self.y + camera_pos[1], self.surface.get_width(), self.surface.get_height()), 3)
            pygame.draw.rect(surface, "#FF0000", (c[0] + camera_pos[0], c[1] + camera_pos[1], c[2], c[3]), 3)
            print((c[0] - camera_pos[0], c[1] - camera_pos[1], c[2], c[3]), camera_pos)
        else:
            self.surface.blit(surface, (self.x + camera_pos[0], self.y + camera_pos[1]))
        

class Engine:
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.__objects: list[Object] = []
    
    def add_object(self, object: Object):
        self.__objects.append(object)
    
    def add_objects(self, objects: list[Object]):
        self.__objects.extend(objects)
    
    def get_object_index_by_id(self, id: str):
        for i in range(len(self.__objects)):
            if self.__objects[i].get_id() == id:
                return i
    
    def delete_object(self, id: str):
        del self.__objects[self.get_object_index_by_id(id)]
    
    def get_objects(self):
        return self.__objects
    
    def draw(self, surface: pygame.Surface, debug:bool = False):
        # center camera pos
        camera_pos = (self.camera_x + (surface.get_width()//2), self.camera_y + (surface.get_height()//2))

        for object in self.__objects:
            object.draw(surface, camera_pos, debug)