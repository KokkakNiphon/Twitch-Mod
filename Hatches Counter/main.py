import pygame
import win32api
import win32con
from time import sleep

class Image(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.SetImage(image)

    def SetImage(self, image):
        self.image = image
        self.rect = self.image.get_rect()

class Button(Image):
    def __init__(self, image):
        Image.__init__(self, image)
    def Clicked(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x,y):
            return True
        return False

class Graphic:
    def __init__(self):
        self.font = pygame.font.Font("resources/Fonts/BalooChettan2-Bold.ttf", 50)

        self.hatch = pygame.image.load("resources/hatchet.png").convert_alpha()
        self.hatch_missed = pygame.image.load("resources/hatchet_missed.png").convert_alpha()
        pass
    def SetFontSize(self, size):
        self.font = pygame.font.Font("resources/Fonts/BalooChettan2-Bold.ttf", size)

class HatchetCounterScene:
    def __init__(self, engine, graphic):
        self.sprites = pygame.sprite.Group()
        self.graphic = graphic
        self.engine = engine

        self.current_hatchet_throw = 1000
        self.current_hatchet_missed = 1000

        self._upThrowKey = False
        self._downThrowKey = False
        self._upMissedKey = False
        self._downMissedKey = False
        self._resetCountKey = False

        self._upThrowKey_pressed = False
        self._downThrowKey_pressed = False
        self._upMissedKey_pressed = False
        self._downMissedKey_pressed = False
        self._resetCountKey_pressed = False

        # Hatchet Icon
        self.hatchet_image = Image(self.graphic.hatch)
        self.sprites.add(self.hatchet_image)

        # Hatchet Count Text
        self.graphic.SetFontSize(90)
        self.hatchet_count = Image(self.graphic.font.render(str(self.current_hatchet_throw), True, (45,213,243)))
        self.hatchet_count.rect.center = (0, self.engine.WINDOW_HEIGHT / 2)
        self.hatchet_count.rect.left = 128
        self.sprites.add(self.hatchet_count)

        self._spacing = 10
        self.offsetting = 128 + self.hatchet_count.rect.width + self._spacing

        # Hatchet missed Icon
        self.hatchet_missed_image = Image(self.graphic.hatch_missed)
        self.hatchet_missed_image.rect.left = self.offsetting
        self.sprites.add(self.hatchet_missed_image)

        # Hatchet Missed Count Text
        self.graphic.SetFontSize(90)
        self.hatchet_missed_count = Image(self.graphic.font.render(str(self.current_hatchet_missed), True, (243,45,45)))
        self.hatchet_missed_count.rect.center = (0, self.engine.WINDOW_HEIGHT / 2)
        self.hatchet_missed_count.rect.left = self.offsetting + 128
        self.sprites.add(self.hatchet_missed_count)

        pass

    def UpdateKey(self):
        self._upThrowKey = (win32api.GetKeyState(win32con.VK_NUMPAD1) & (1 << 7)) != 0
        self._downThrowKey = (win32api.GetKeyState(win32con.VK_NUMPAD4) & (1 << 7)) != 0
        self._upMissedKey = (win32api.GetKeyState(win32con.VK_NUMPAD2) & (1 << 7)) != 0
        self._downMissedKey = (win32api.GetKeyState(win32con.VK_NUMPAD5) & (1 << 7)) != 0
        self._resetCountKey = (win32api.GetKeyState(win32con.VK_NUMPAD9) & (1 << 7)) != 0
    
    def UpdateKeyPressed(self):
        self._upThrowKey_pressed = self._upThrowKey
        self._downThrowKey_pressed = self._downThrowKey 
        self._upMissedKey_pressed = self._upMissedKey
        self._downMissedKey_pressed = self._downMissedKey
        self._resetCountKey_pressed = self._resetCountKey

    def Update(self):
        self.sprites.update()
        self.UpdateKey()

        if self._upThrowKey and not self._upThrowKey_pressed:
            self.current_hatchet_throw = self.current_hatchet_throw + 1
            self.UpdateHatchetCount()
        if self._downThrowKey and not self._downThrowKey_pressed:
            self.current_hatchet_throw = self.current_hatchet_throw - 1
            self.UpdateHatchetCount()

        if self._upMissedKey and not self._upMissedKey_pressed:
            self.current_hatchet_missed = self.current_hatchet_missed + 1
            self.UpdateHatchetCount()
        if self._downMissedKey and not self._downMissedKey_pressed:
            self.current_hatchet_missed = self.current_hatchet_missed - 1
            self.UpdateHatchetCount()
        
        if self._resetCountKey and not self._resetCountKey_pressed:
            self.current_hatchet_throw = 0
            self.current_hatchet_missed = 0
            self.UpdateHatchetCount()

        self.UpdateKeyPressed()
        pass

    def UpdateHatchetCount(self):
        self.hatchet_count.SetImage(self.graphic.font.render(str(self.current_hatchet_throw), True, (45,213,243)))
        self.hatchet_count.rect.center = (0, self.engine.WINDOW_HEIGHT/2)
        self.hatchet_count.rect.left = 128
        
        self.offsetting = 128 + self.hatchet_count.rect.width + self._spacing

        self.hatchet_missed_image.rect.left = self.offsetting

        self.hatchet_missed_count.SetImage(self.graphic.font.render(str(self.current_hatchet_missed), True, (243,45,45)))
        self.hatchet_missed_count.rect.center = (0, self.engine.WINDOW_HEIGHT / 2)
        self.hatchet_missed_count.rect.left = self.offsetting + 128
    
    def Render(self):
        self.sprites.draw(self.engine._window)
        pass

class Engine:
    def __init__(self):
        self._isRunning = True
        self.WINDOW_WIDTH = 680
        self.WINDOW_HEIGHT = 140

        self._window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.font.init()
        pygame.display.set_caption("Hatchet Counter")
        pygame.display.set_icon(pygame.image.load("resources/Logo.png").convert_alpha())
        # pygame.display.set_icon(pygame.image.load("").convert_alpha())
        pygame.init()

        self._deltaTime = 0.0
        self._lastTime = 0.0
        self._scene = HatchetCounterScene(self, Graphic())

        self.event = pygame.event.get()
    def Update(self):
        self._scene.Update()
    def Render(self):
        self._window.fill((0,255,0))
        self._scene.Render()
        pygame.display.update()

    def Input(self):
        self.event = pygame.event.get()
        for event in self.event:
            if event.type == pygame.QUIT:
                self._isRunning = False
                self.Quit()

    def UpdateTime(self):
        pass
    def Run(self):
        while self._isRunning:
            t = pygame.time.get_ticks()
            self._deltaTime = (t - self._lastTime) / 1000.0
            self._lastTime = t
            self.Update()
            self.Render()
            self.Input()
            sleep(0.05)
                
    def Quit(self):
        pygame.quit()

    def DeltaTime(self):
        return self._deltaTime
        pass

    def Time(self):
        return pygame.time.get_ticks() / 1000.0
        pass

def main():
    engine = Engine()
    engine.Run()

main()