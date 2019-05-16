# 6.835 Final Project - InstruMagic

## File Guide

- common/ - folder containing audio, graphics, and timekeeping framework from 6.809
- gesture_recognizer.py - script that interprets kinect data and outputs classified gestures
- kinect.py - XBox Kinect interfacing script
- main.py - main program controller, manages all program components
- pitch_tracker.py - script that interprets audio frames and outputs pitches/chords
- playback.py - script that manages audio playback, the metronome audio
- sfx/ - folder containing sound effect files
- tempo_processor.py - script that recognizes timestamped beats from the gesture controller and modifies the system's tempo accordingly
- ui.py - script that contains components for displaying user interface elements

## Running & Setup

Due to framework constraints and dependencies, InstruMagic only works on Windows computers.

Before running InstruMagic, make sure you have installed the following Python packages:
- Kivy
- PyAudio
- Numpy
- Aubio
- MatPlotLib
- PyKinect
- PyGame
- PyFluidSynth

After these packages have been installed and you computer has been connected to an XBox Kinect, launch InstruMagic by running 'main.py' with Python 2.x.
