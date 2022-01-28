import pygame
import win32api
import win32con
import sounddevice as sd
import numpy as np
import threading
from time import sleep

is_running = True

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

        self.avatar_1 = pygame.image.load("resources/Avatar_1.png").convert_alpha()
        self.avatar_2 = pygame.image.load("resources/Avatar_2.png").convert_alpha()
        # self.hatch_missed = pygame.image.load("resources/hatchet_missed.png").convert_alpha()
        pass
    def SetFontSize(self, size):
        self.font = pygame.font.Font("resources/Fonts/BalooChettan2-Bold.ttf", size)

class AvatarAnimatorScene:
    def __init__(self, engine, graphic):
        self.sprites = pygame.sprite.Group()
        self.graphic = graphic
        self.engine = engine

        self.current_hatchet_throw = 1000
        self.current_hatchet_missed = 1000

        self._upThrowKey = False
        self._downThrowKey = False

        self._upThrowKey_pressed = False
        self._downThrowKey_pressed = False

        # Hatchet Icon
        self.hatchet_image = Image(self.graphic.avatar_1)
        self.sprites.add(self.hatchet_image)

        pass

    def UpdateKey(self):
        self._upThrowKey = (win32api.GetKeyState(win32con.VK_NUMPAD1) & (1 << 7)) != 0
        self._downThrowKey = (win32api.GetKeyState(win32con.VK_NUMPAD4) & (1 << 7)) != 0
    
    def UpdateKeyPressed(self):
        self._upThrowKey_pressed = self._upThrowKey
        self._downThrowKey_pressed = self._downThrowKey

    def Update(self):
        self.sprites.update()
        self.UpdateKey()

        if self._upThrowKey and not self._upThrowKey_pressed:
            self.hatchet_image.SetImage(self.graphic.avatar_2)
        if self._downThrowKey and not self._downThrowKey_pressed:
            self.hatchet_image.SetImage(self.graphic.avatar_1)

        self.UpdateKeyPressed()
        pass

    def UpdateAvatarVisual(self, is_talking):
        if is_talking:
            self.hatchet_image.SetImage(self.graphic.avatar_2)
        else:
            self.hatchet_image.SetImage(self.graphic.avatar_1)
        pass
    
    def Render(self):
        self.sprites.draw(self.engine._window)
        pass

class Engine:
    def __init__(self):
        self._isRunning = True
        self.WINDOW_WIDTH = 956
        self.WINDOW_HEIGHT = 968

        self._window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.font.init()
        pygame.display.set_caption("Avatar Animator")
        pygame.display.set_icon(pygame.image.load("resources/Logo.png").convert_alpha())
        # pygame.display.set_icon(pygame.image.load("").convert_alpha())
        pygame.init()

        self._deltaTime = 0.0
        self._lastTime = 0.0
        self._scene = AvatarAnimatorScene(self, Graphic())

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
            sleep(0.1)
                
    def Quit(self):
        global is_running
        pygame.quit()
        is_running = False

    def DeltaTime(self):
        return self._deltaTime
        pass

    def Time(self):
        return pygame.time.get_ticks() / 1000.0
        pass

engine = Engine()
is_talking = False

def detect_sound(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata)*10
    
    global is_talking
    global engine    
    if (volume_norm > 9 and is_talking == False): #adjust the magic number to change the sensitivity (lower = more sensitive)
        is_talking = True
        engine._scene.UpdateAvatarVisual(is_talking)
    elif (volume_norm <= 9 and is_talking == True):
        is_talking = False
        engine._scene.UpdateAvatarVisual(is_talking)


# with sd.Stream(callback=detect_sound):
#     print("start talking")

class detectSoundThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global is_running
        with sd.InputStream(callback=detect_sound):
            while True:
                if is_running == False:
                    break

newDetectSoundThread = detectSoundThread()

newDetectSoundThread.start()
engine.Run()