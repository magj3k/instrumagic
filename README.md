# InstruMagic - 6.835 Final Project

## Overview

InstruMagic is a musical improvisation interface that allows experienced and aspiring musicians alike to experiment with music in an intuitive and tangible way. Simply stand in front of the Kinect, conduct a tempo, sing a chord progression, and finally, go crazy! Piano, guitar, and drum set not included.

Learn more about InstruMagic here: https://www.youtube.com/watch?v=b3TeQufmkDg

Read more about our process here: https://docs.google.com/document/d/1PM2lt1YP-Bp9QAlkMpTJrxJeTNwm8qZh99uFIJx2-Fs/edit?usp=sharing

## File Guide

- common/ - folder containing audio, graphics, and timekeeping framework from 6.809
- kinect.py - XBox Kinect interfacing script, beat recognition logic
- main.py - main program controller, manages all program components, also contains gesture recognition logic for Kinect input
- pitch_tracker.py - script that interprets audio frames and outputs pitches/chords
- playback.py - script that manages audio playback, the metronome audio
- sfx/ - folder containing sound effect files
- tempo_processor.py - script that recognizes timestamped beats from the gesture controller and modifies the system's tempo accordingly
- ui.py - script that contains components for displaying user interface elements
- gesture_recognizer.py - outdated script that outputs classified gestures from Leap data

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

Also, make sure to download the MIDI soundfont file (named FluidR3_GM.sf2) from https://www.dropbox.com/s/5urjooxtapuo7mz/FluidR3_GM.sf2?dl=0 and put it in the sfx/ directory of the InstruMagic project.

After these packages have been installed and you computer has been connected to an XBox Kinect, launch InstruMagic by running 'main.py' with Python 2.x.
