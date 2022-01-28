from concurrent.futures import thread
from distutils.log import debug
import pygame
import win32api
import win32con
import math
import sys
import threading
from time import sleep
import random

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

        self.hatchet = pygame.image.load("resources/hatchet.png").convert_alpha()
        self.background = pygame.image.load("resources/background.png").convert_alpha()

        self.command_background = pygame.image.load("resources/command_event_background.png").convert_alpha()
        self.stat_background = pygame.image.load("resources/hachet_stat_background.png").convert_alpha()

        self.bullseye = pygame.image.load("resources/bullseye.png").convert_alpha()
        self.projectile_dot = pygame.image.load("resources/projectile_dot.png").convert_alpha()

        pass
    def SetFontSize(self, size):
        self.font = pygame.font.Font("resources/Fonts/BalooChettan2-Bold.ttf", size)

class HatchetObject:
    def __init__(self, engine, graphic):
        self.sprites = pygame.sprite.Group()
        self.graphic = graphic
        self.engine = engine

        self.initial_posX = 200
        self.initial_posY = 240

        # Hatchet Icon
        self.hatchet_image = Image(self.graphic.hatchet)
        self.hatchet_image.rect.center = (self.initial_posX, self.initial_posY)
        self.sprites.add(self.hatchet_image)

        self.hatchetSpeed = 6
        self.hatchetSpinSpeed = 600

        self.limitHeight = 225
        self.limitAngleMin = -10
        self.limitVelicityMax = 110
        self.limitVelicityMin = 70

        self.angle = -random.randint(-self.limitAngleMin, 45)
        self.velocity = random.randint(self.limitVelicityMin, self.limitVelicityMax)

        self.is_being_thrown = False

        self.start_throwing_time = 0

        self.min_hit_distnace = 25

        self.target_position = (1248, 292)

        self.d2r = 3.14159265/180
        self.gravity = 9.81
        self.projectileStepSize = 1

        self.gameEnded = False
        self.playerWon = False
        self.resetTimerDuration = 5
        self.resetTimerCurrent = 5


        pass

    def IncreaseAngle(self, incrementValue):
        if (self.CheckHatchetLimitation(self.angle + incrementValue, self.velocity)):
            self.angle += incrementValue
            print("Increase Angle By: " + str(incrementValue))
        
    def IncreaseVelocity(self, incrementValue):
        if (self.CheckHatchetLimitation(self.angle, self.velocity + incrementValue)):
            self.velocity += incrementValue
            print("Increase Velocity By: " + str(incrementValue))

    def UpdateHatchet(self):

        if self.gameEnded:
            self.resetTimerCurrent -= self.engine.DeltaTime()

        if self.resetTimerCurrent <= 0 and self.gameEnded:
            self.ResetHatchet()

        self.hatchet_image.SetImage(pygame.transform.rotate(self.graphic.hatchet, (self.engine.Time() - self.start_throwing_time) * -self.hatchetSpinSpeed))

        if (self.is_being_thrown):
            local_totalTime = (self.engine.Time() - self.start_throwing_time) * self.hatchetSpeed
            self.hatchet_image.rect.center = (self.initial_posX + self.velocity * local_totalTime * math.cos(self.angle* self.d2r), self.initial_posY + self.velocity * local_totalTime * math.sin(self.angle* self.d2r) + 1/2 * self.gravity * local_totalTime * local_totalTime)
        else:
            self.hatchet_image.rect.center = (self.initial_posX, self.initial_posY)

        if self.is_being_thrown and self.playerWon == False:
            if math.dist(self.hatchet_image.rect.center,self.target_position) < self.min_hit_distnace:
                self.playerWon = True
            elif self.hatchet_image.rect.center[1] > self.engine.WINDOW_HEIGHT:
                self.playerWon = False
                

        if self.hatchet_image.rect.center[1] > self.engine.WINDOW_HEIGHT:
            self.EndGame()

    def RenderProjectile(self, renderQuality):
        renderX_Pos = 0
        renderY_Pos = 0
        
        projectileTime = 0

        projectileDeltaTime = self.projectileStepSize;
        self.sprites.empty() #not very optimize but it's fine for now

        for i in range(renderQuality):
            renderX_Pos = self.initial_posX + self.velocity * projectileTime * math.cos(self.angle* self.d2r)
            renderY_Pos = self.initial_posY + self.velocity * projectileTime * math.sin(self.angle* self.d2r) + 1/2 * + self.gravity * projectileTime * projectileTime
            projectileTime += projectileDeltaTime

            projectile_dot_graphic = Image(self.graphic.projectile_dot)
            projectile_dot_graphic.rect.center = (renderX_Pos, renderY_Pos)
            self.sprites.add(projectile_dot_graphic)

        self.sprites.add(self.hatchet_image)
        self.sprites.draw(self.engine._window)
        
        pass

    def CheckHatchetLimitation(self, angle, velocity):
        yMax = velocity * velocity * math.sin(angle * self.d2r) * math.sin(angle * self.d2r) / (2 * self.gravity)
        if (yMax > self.limitHeight or velocity > self.limitVelicityMax or angle >= self.limitAngleMin or velocity <= self.limitVelicityMin):
            return False
        else:
            return True

    def EndGame(self):

        if self.gameEnded == False:
            self.resetTimerCurrent = self.resetTimerDuration

        self.gameEnded = True

        if (self.playerWon):
            self.engine._scene.EventChatSendCommand("HMG", "Right on the ", "target!", (255,0,0))
        else:
            self.engine._scene.EventChatSendCommand("HMG", "Awww you missed the ", "target!", (255,255,255))

    def ResetHatchet(self):
        self.gameEnded = False

        self.is_being_thrown = False
        self.engine._scene.EventChatSendCommand("HMG", "The minigame has reset! ", "Try Again!", (255,255,0))

        self.engine._scene.ResetThrowTimer()

        self.angle = -random.randint(-self.limitAngleMin, 45)
        self.velocity = random.randint(self.limitVelicityMin, self.limitVelicityMax)

    def ThrowHatchet(self):            
        self.start_throwing_time = self.engine.Time()
        self.is_being_thrown = True

        print(str(self.angle) + ", " + str(self.velocity))
        pass



class HuntressMinigame:
    def __init__(self, engine, graphic):
        self.sprites = pygame.sprite.Group()
        self.graphic = graphic
        self.engine = engine

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

        self.countdownTimerDuration = 60 * 2
        self.streamDelay = 5
        self.countdownTimerCurrent = self.countdownTimerDuration + self.streamDelay

        # Backgounds
        self.backgound_image = Image(self.graphic.background)
        self.sprites.add(self.backgound_image)

        self.command_background = Image(self.graphic.command_background)
        self.command_background.rect.top = 5
        self.command_background.rect.left = 3
        self.stat_background = Image(self.graphic.stat_background)
        self.stat_background.rect.top = 220
        self.stat_background.rect.left = 8
        self.sprites.add(self.command_background)
        self.sprites.add(self.stat_background)

        # Bullseye Icon
        self.bullseye_image = Image(self.graphic.bullseye)
        self.bullseye_image.rect.left = 1210
        self.bullseye_image.rect.top = 240
        self.sprites.add(self.bullseye_image)

        # Projectile Object Render
        self.hatchet_object = HatchetObject(self.engine, self.graphic)

        # Hatchet Velocity Text
        self.graphic.SetFontSize(40)
        self.hatchet_velocity_text = Image(self.graphic.font.render(str(self.hatchet_object.velocity), True, (55,178,72)))
        self.hatchet_velocity_text.rect.center = (0, 246)
        self.hatchet_velocity_text.rect.left = 85
        self.sprites.add(self.hatchet_velocity_text)

        # Hatchet Angle Text
        self.graphic.SetFontSize(40)
        self.hatchet_angle_text = Image(self.graphic.font.render(str(-self.hatchet_object.angle), True, (252,21,68)))
        self.hatchet_angle_text.rect.center = (0, 296)
        self.hatchet_angle_text.rect.left = 85
        self.sprites.add(self.hatchet_angle_text)

        # Hatchet Event Text
        self.graphic.SetFontSize(50)        
        self.hatchet_event_text_name = Image(self.graphic.font.render(str("Linakija :"), True, (255,255,255)))
        self.hatchet_event_text_command = Image(self.graphic.font.render(str("Powerup"), True, (255,255,255)))
        self.hatchet_event_text = Image(self.graphic.font.render(str("the hatchet"), True, (255,255,255)))
        self.hatchet_event_text_name.rect.top = 0
        self.hatchet_event_text_name.rect.left = 12
        self.hatchet_event_text_command.rect.top = 0
        self.hatchet_event_text_command.rect.left = 12 + self.hatchet_event_text_name.rect.width
        self.hatchet_event_text.rect.top = 0
        self.hatchet_event_text.rect.left = 12 + self.hatchet_event_text_name.rect.width + self.hatchet_event_text_command.rect.width
        self.sprites.add(self.hatchet_event_text_name)
        self.sprites.add(self.hatchet_event_text_command)
        self.sprites.add(self.hatchet_event_text)

        # Hatchet CountdownTimer Text
        self.graphic.SetFontSize(60)
        self.hatchet_timer_text = Image(self.graphic.font.render(str(self.countdownTimerCurrent), True, (255,255,255)))
        self.hatchet_timer_text.rect.top = 0
        self.hatchet_timer_text.rect.left = 1167
        self.sprites.add(self.hatchet_timer_text)
        
        # User
        self.players_name = []

        self.EventChatSendCommand("Kokkak", "increase the hatched ", "ANGLE", (252,21,68))

        pass

    def ResetThrowTimer(self):
        self.players_name.clear()
        self.countdownTimerCurrent = self.countdownTimerDuration + self.streamDelay

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
        self.hatchet_object.UpdateHatchet()

        if self.countdownTimerCurrent > 0:
            self.countdownTimerCurrent -= self.engine.DeltaTime()

        if self.countdownTimerCurrent <= 0 and self.hatchet_object.is_being_thrown == False:
            self.hatchet_object.ThrowHatchet()
            self.countdownTimerCurrent = 0

        self.UpdateTimerRender()

        if self._upThrowKey and not self._upThrowKey_pressed:
            self.hatchet_object.IncreaseAngle(1)
            self.UpdateHatchetStatGraphic()
        if self._downThrowKey and not self._downThrowKey_pressed:
            self.hatchet_object.IncreaseAngle(-1)
            self.UpdateHatchetStatGraphic()

        if self._upMissedKey and not self._upMissedKey_pressed:
            self.hatchet_object.IncreaseVelocity(-5)
            self.UpdateHatchetStatGraphic()

        if self._downMissedKey and not self._downMissedKey_pressed:
            self.hatchet_object.IncreaseVelocity(5)
            self.UpdateHatchetStatGraphic()

        if self._resetCountKey and not self._resetCountKey_pressed:
            global bot
            bot.event_message("Message")
            self.hatchet_object.ThrowHatchet()
            self.UpdateHatchetStatGraphic()

            pass

        self.UpdateKeyPressed()
        pass
    
    def UpdateTimerRender(self):
        timerSeconds = math.floor(self.countdownTimerCurrent) % 60
        timerMin =  str(math.floor(math.floor(self.countdownTimerCurrent) / 60)).zfill(2)
        timerSeconds = str(timerSeconds).zfill(2)

        self.graphic.SetFontSize(80)
        self.hatchet_timer_text.SetImage(self.graphic.font.render(f"{timerMin}:{timerSeconds}", True, (252,21,68)))
        self.hatchet_timer_text.rect.top = -15
        self.hatchet_timer_text.rect.left = 1167

    def EventChatSendCommand(self, username, event_text, command, text_color):
        self.graphic.SetFontSize(50)
        self.hatchet_event_text_name.SetImage(self.graphic.font.render(str(username), True, (236, 91, 114)))
        self.hatchet_event_text.SetImage(self.graphic.font.render(str(" : " + event_text), True, (255,255,255)))
        self.hatchet_event_text_command.SetImage(self.graphic.font.render(str(command), True, text_color))
        self.hatchet_event_text_name.rect.top = 0
        self.hatchet_event_text_name.rect.left = 12
        self.hatchet_event_text.rect.top = 0
        self.hatchet_event_text.rect.left = 12 + self.hatchet_event_text_name.rect.width
        self.hatchet_event_text_command.rect.top = 0
        self.hatchet_event_text_command.rect.left = 12 + self.hatchet_event_text_name.rect.width + self.hatchet_event_text.rect.width
        pass

    def UpdateHatchetStatGraphic(self):
        self.graphic.SetFontSize(40)
        self.hatchet_velocity_text.SetImage(self.graphic.font.render(str(self.hatchet_object.velocity), True, (55,178,72)))
        self.hatchet_velocity_text.rect.center = (0, 246)
        self.hatchet_velocity_text.rect.left = 85

        self.hatchet_angle_text.SetImage(self.graphic.font.render(str(-self.hatchet_object.angle), True, (252,21,68)))
        self.hatchet_angle_text.rect.center = (0, 296)
        self.hatchet_angle_text.rect.left = 85

    def Render(self):
        self.sprites.draw(self.engine._window)
        self.hatchet_object.RenderProjectile(30)
        pass

class Engine:
    def __init__(self):
        self._isRunning = True
        self.WINDOW_WIDTH = 1400
        self.WINDOW_HEIGHT = 350

        self._window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.font.init()
        pygame.display.set_caption("Huntress Minigame")
        pygame.display.set_icon(pygame.image.load("resources/Logo.png").convert_alpha())
        pygame.init()

        self._deltaTime = 0.0
        self._lastTime = 0.0
        self._scene = HuntressMinigame(self, Graphic())

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
            sleep(0.015)
                
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
    
from twitchio.ext import commands

engine = Engine()

class Bot(commands.Bot):
    global engine

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token='ntv5w3631gh7c8yvjdzvfz2008lymp', nick='HuntressMinigame', prefix='!', initial_channels=['Jinlamang'])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    @commands.command()
    async def aimup(self, ctx: commands.Context):
        print(commands.Context)
        engine._scene.hatchet_object.IncreaseAngle(-5)
        engine._scene.UpdateHatchetStatGraphic()
        engine._scene.EventChatSendCommand(ctx.author.name, "increase the hatched ", "ANGLE", (252,21,68))
        engine._scene.players_name.append(ctx.author.name)
        await ctx.send(f'{ctx.author.name} aimed the hatched up!')

    @commands.command()
    async def aimdown(self, ctx: commands.Context):
        engine._scene.hatchet_object.IncreaseAngle(5)
        engine._scene.UpdateHatchetStatGraphic()
        engine._scene.EventChatSendCommand(ctx.author.name, "decrease the hatched ", "ANGLE", (252,21,68))
        engine._scene.players_name.append(ctx.author.name)
        await ctx.send(f'{ctx.author.name} aimed the hatched down!')

    @commands.command()
    async def powerup(self, ctx: commands.Context):
        engine._scene.hatchet_object.IncreaseVelocity(10)
        engine._scene.UpdateHatchetStatGraphic()
        engine._scene.EventChatSendCommand(ctx.author.name, "increase the hatchet ", "POWER", (55,178,72))
        engine._scene.players_name.append(ctx.author.name)
        await ctx.send(f'{ctx.author.name} increase the hatchet power!')

    @commands.command()
    async def powerdown(self, ctx: commands.Context):
        engine._scene.hatchet_object.IncreaseVelocity(-10)
        engine._scene.UpdateHatchetStatGraphic()
        engine._scene.EventChatSendCommand(ctx.author.name, "decrease the hatchet ", "POWER", (55,178,72))
        engine._scene.players_name.append(ctx.author.name)
        await ctx.send(f'{ctx.author.name} decrease the hatchet power!')
    
    async def event_message(self, message):
        await self.handle_commands(message)



    # @commands.command()
    # async def throw(self, ctx: commands.Context):
    #     engine._scene.hatchet_object.ThrowHatchet()
    #     engine._scene.UpdateHatchetStatGraphic()
    #     engine._scene.EventChatSendCommand(ctx.author.name, "throwed the hatchet!")
    #     engine._scene.players_name.append(ctx.author.name)
    #     await ctx.send(f'{ctx.author.name} throwed the hatched!')

    # @commands.command()
    # async def resethatchet(self, ctx: commands.Context):
    #     engine._scene.hatchet_object.ResetHatchet()
    #     await ctx.send(f'{ctx.author.name} reset the hatched!')

bot = Bot()

class EngineThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        bot.run()
        

newEngineThread = EngineThread()
newEngineThread.start()

engine.Run()

bot = None
