import pygame
import random
from typing import overload
import copy
import math

VER = "0.6.0"
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

class Interaction:
    player_instance = None
    def __init__(self, x:int, y:int, title:str, key_str:str="E", key_int:pygame.key=pygame.K_e, time:int=1, activation_dist:int=20, active:bool=True):
        self.active = active
        self.activated = False

        self.x = x
        self.y = y

        self.title = title
        self.key = key_int
        self.key_str = key_str

        self.time = time
        self.time_passed = 0
        self.time_offset = 0

        self.activation = activation_dist
    
    def draw(self, screen):
        player = Interaction.player_instance

        # compute the distance of the players center from the interaction prompt
        # self.x - player.x + (player.size[0]//2) < self.activation and self.y - player.y + (player.size[1]//2) < self.activation 

        distance = math.sqrt((self.x - (player.x + (player.size[0]//2)))**2 + (self.y - (player.y + (player.size[1]//2)))**2)
        
        if distance <= self.activation and self.active: # responsible for activating the prompt if proximity is maintained
            # define frames, fonts and text
            font = pygame.font.Font("assets/fonts/comicbd.ttf", 12)
            bigfont = pygame.font.Font("assets/fonts/comicbd.ttf", 12)
            text = font.render(self.title, True, "#FFFFFF")
            
            frame = pygame.Surface((35+text.get_width(), 30), pygame.SRCALPHA)

            # draw menu
            frame.fill("#11111199")

        if pygame.key.get_pressed()[self.key] and distance <= self.activation and self.active:
            if self.time_passed == 0:
                self.time_offset = pygame.time.get_ticks()
                self.time_passed = 1
            else:
                self.time_passed = pygame.time.get_ticks() - self.time_offset
            
            pygame.draw.circle(frame, "#111111", (15, 15), 10)
            keytext = bigfont.render(self.key_str, True, "#FFFFFF")

            for i in range(int(625)): # 2 * pi = 6.25, idk trigonometry, but i do know point around a circle
                if i%5 == 0 and i <= (self.time_passed/self.time)*625:
                    pygame.draw.rect(frame, "#FFFFFF", (15+round(math.sin(i/100)*10), 15+round(math.cos(i/100)*-10), 1, 1))

            if self.time_passed >= self.time:
                self.active = False
                self.activated = True

            frame.blit(keytext, (14-(keytext.get_width()//2), 14-(keytext.get_height()//2)))
        elif distance <= self.activation and self.active:
            self.time_passed = 0
            pygame.draw.circle(frame, "#FFFFFF", (15, 15), 10)
            keytext = bigfont.render(self.key_str, True, "#111111")
            frame.blit(keytext, (14-(keytext.get_width()//2), 14-(keytext.get_height()//2)))
        else:
            self.time_passed = 0
        
        if distance <= self.activation and self.active:
            frame.blit(text, (30, 5))

            screen.blit(frame, (screen.get_width()//2-player.texture.get_width()//2-player.x+self.x-15,
                                screen.get_height()//2-player.texture.get_height()//2-player.y+self.y-15))

class Object:
    def __init__(self, x: int, y: int, name: str = None, texture_surface: pygame.Surface = NULL_SURFACE, collision_rect:tuple = None):
        self.name = (self.__class__.__name__ if name == None else name)
        self.type = self.__class__.__name__

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
    def __init__(self, x, y, name = None, texture_surface = NULL_SURFACE, collision_rect = None, speed = 5, controls: list[bool, bool, bool, bool] = []):
        """
        controls is a list with keyboard keys, examples:

        "w", "LEFT", "RETURN", "1", etc...

        if controls is not defined, you are expected to use the move() method manually with bools
        """
        super().__init__(x, y, name, texture_surface, collision_rect)
        self.speed = speed
        self.controls = controls
        self.controls_auto = True
    
    def control(self):
        bools = []
        keys = pygame.key.get_pressed()
        for key in self.controls:
            bools.append(keys[getattr(pygame, "K_"+key)])
        self.move(*bools)

    def move(self, up: bool, down: bool, left: bool, right: bool):
        self.x += (right - left) * self.speed
        self.y += (down - up) * self.speed

class Group:
    def __init__(self, name: str = None, objects: list[Object] = []):
        """
        A Group holds multiple Objects in one place in the code for easy identifying.

        Objects in the group are not relative to any position, they are all free to move around separately.

        Group.get_pos() always returns (0, 0)
        """
        self.type = self.__class__.__name__
        self.name = (self.__class__.__name__ if name == None else name)
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

    def get_objects_by_name(self, name: str):
        out = []
        for object in self.objects:
            if object.name == name:
                out.append(object)
    
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
        self.camera_lock = None
        self.objects: list[Object] = []
        self.players: list[Player] = []
    
    def lock_camera(self, player_name: str):
        self.camera_lock = player_name
    
    def unlock_camera(self):
        self.camera_lock = None
    
    def players_tick(self):
        for player in self.players:
            if player.controls_auto:
                player.control()
        
        if self.camera_lock != None:
            for player in self.players:
                if player.name == self.camera_lock:
                    self.camera_x, self.camera_y = player.x + (player.surface.get_rect().w//2), player.y + (player.surface.get_rect().h//2)
                    break
    
    def extract_objects(self):
        out = super().extract_objects()
        out.extend(self.players)
        return out

    def draw(self, surface: pygame.Surface, debug_options: tuple[bool, bool, bool] = (True, False, False)):
        # center camera pos
        camera_pos = (self.camera_x - (surface.get_width()//2), self.camera_y - (surface.get_height()//2))

        super().draw(surface, camera_pos, debug_options)

#endregion