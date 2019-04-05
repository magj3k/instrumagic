from time import time
from gesture_recognizer import *
from playback import *
from ui import *

playbackSystem = PlaybackSystem()
gestureRecognizer = GestureRecognizer(playbackSystem)

# main on_update loop
now_old = time()
while True:
    now = time() # timekeeping
    dt = now-now_old # units in seconds

    playbackSystem.on_update(dt)
    gestureRecognizer.on_update(dt)

    now_old = now # timekeeping