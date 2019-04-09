import pysynth
import pygame, pygame.sndarray
import numpy
import fluidsynth
import time

fs = fluidsynth.Synth()
fs.start()

sfid = fs.sfload("example.sf2")
fs.program_select(0, sfid, 0, 0)

fs.noteon(0, 60, 30)
fs.noteon(0, 67, 30)
fs.noteon(0, 76, 30)

time.sleep(1.0)

fs.noteoff(0, 60)
fs.noteoff(0, 67)
fs.noteoff(0, 76)

time.sleep(1.0)

fs.delete()



# test = ( ('c', 4), ('e', 4) )
# pysynth.make_wav(test, fn = "test.wav")
# pygame.init()

# pygame.mixer.music.load("test.wav")
# pygame.mixer.music.play()
# pygame.event.wait()
# print("done")







# sample_rate = 44100
# def sine_wave(hz, peak, n_samples=sample_rate):
#     """Compute N samples of a sine wave with given frequency and peak amplitude.
#        Defaults to one second.
#     """
#     length = sample_rate / float(hz)
#     omega = numpy.pi * 2 / length
#     xvalues = numpy.arange(int(length)) * omega
#     onecycle = peak * numpy.sin(xvalues)
#     return numpy.resize(onecycle, (n_samples,)).astype(numpy.int16)

# def play_for(sample_wave, ms):
#     """Play the given NumPy array, as a sound, for ms milliseconds."""
#     sound = pygame.sndarray.make_sound(sample_wave)
#     sound.play(-1)
#     pygame.time.delay(ms)
#     sound.stop()

# play_for(sum([sine_wave(440, 4096), sine_wave(880, 4096)]), 1000)








# from mingus.containers import Note, Bar
# import fluidsynth

# n = Note("C", 4)
# fluidsynth.play_Note(n)

# b = Bar()
# b.meter
# b.place_notes("A-4", 4)