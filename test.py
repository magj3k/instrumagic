import pysynth
import pygame


test = ( ('a', 16), ('b', 16), ('a', 16), ('c', 16) )
pysynth.make_wav(test, fn = "test.wav")

pygame.init()

pygame.mixer.music.load("test.wav")
pygame.mixer.music.play()
pygame.event.wait()
