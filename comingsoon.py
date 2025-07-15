import pygame
import math

# interactions
# fully customizable dialog boxes
# some sort of way to handle windows easily, maybe an optionally used ready Game() class
# optimizations to player collisions

class Interaction:
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
            
class DialogBox:
    def __init__(self):
        self.title = ""

        self.visible = False
        self.to_show = ""
        self.showing = ""

        self.typewriter_stage = 0
        self.typewriter_finished = False

        self.setDefaults()

    def setDefaults(self):
        """
        set all styling attributes to default values
        """
        # its all here so you can configure it later with eg. instance.text_color = "#FF0000" or instance.BG_color = color.RED
        self.title_font = pygame.font.Font("assets/fonts/comicbd.ttf", 24)
        self.desc_font = pygame.font.Font("assets/fonts/comic.ttf", 16)
        self.skip_font = pygame.font.Font("assets/fonts/comici.ttf", 12)
        self.typewrite_step = 1
        self.BG_color = "#000000"
        self.title_color = "#EEEEEE"
        self.text_color = "#FFFFFF"
        self.border_color = "#FFFFFF"

    def showText(self, title:str, text:str):
        """
        Shows dialog box, and automatically starts the typewriting effect.
        """
        self.hideText()
        self.title = title
        self.visible = True
        self.to_show = text
        self.typewriter_finished = False

    def hideText(self):
        """
        Hides dialog box
        """
        self.visible = False
        self.title = ""
        self.to_show = ""
        self.showing = ""
        self.typewriter_stage = 0
        self.typewriter_finished = False # did it finish typing?

    def skip(self):
        """
        Skips typewriting effect if it's still going, if typewriter already finished executes hideText()
        """
        if self.typewriter_stage < len(self.to_show):
            self.showing = self.to_show
            self.typewriter_stage = len(self.to_show)
        else:
            self.hideText()

    def draw(self, screen:pygame.Surface):
        if self.visible:
            # progresses dialog typewriter effect
            if self.typewriter_stage < len(self.to_show):
                self.typewriter_stage += 1
                self.showing = self.to_show[:self.typewriter_stage]
            else:
                self.typewriter_finished = True


            # draw dialog box
            pygame.draw.rect(screen, self.BG_color, (5, 400, 790, 195), 0, 20)
            pygame.draw.rect(screen, self.border_color, (5, 400, 790, 195), 3, 20)

            # draw text
            screen.blit(self.title_font.render(self.title, True, self.title_color), (20, 415))
            description = self.showing.split("\n")
            for i in range(len(description)):
                screen.blit(self.desc_font.render(description[i], True, self.text_color), (30, 455 + 22*i))

            # draw skip hint text
            if self.typewriter_finished:
                screen.blit(self.skip_font.render("Press 'SPACE' to close...", True, "#EEEEEE"), (630, 569))
            else:
                screen.blit(self.skip_font.render("Press 'SPACE' to skip...", True, "#EEEEEE"), (630, 569))