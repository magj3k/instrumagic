from gesture_recognizer import *
from playback import *

gestureRecognizer = GestureRecognizer()

# main on_update loop
while True:
    gestureRecognizer.on_update()