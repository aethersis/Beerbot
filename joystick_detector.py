import pygame

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

while 1:
    event = pygame.event.wait()
    if event.type == pygame.JOYAXISMOTION:
        e = event.dict
        print("Currently moving axis: " + str(e['axis']))