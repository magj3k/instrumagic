#####################################################################
#
# audiocfg.py
#
# Copyright (c) 2018, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

# common import
import sys
import re
sys.path.append('.')
sys.path.append('..')

from common.core import *
from common.audio import *
from kivy.core.window import Window

from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

# useful for creating a fixed label where the size and text_size is setup correctly
# so that they text can be laied out properly in a FloatLayout
def create_fixed_label(txt, pos_hint):
    label = Label(text=txt)
    label.texture_update()
    label.size = label.texture_size
    label.size_hint = (None, None)
    label.pos_hint = pos_hint
    return label

# create a text input widget, given a width hint and pos_hint
def create_text_input(txt, width, pos_hint):
    ti = TextInput(text=txt, size_hint = (None, None), multiline=False)
    ti.size = (Window.width * width, ti.minimum_height)
    ti.pos_hint = pos_hint
    return ti

# create a DropDown, including the button that activates it.
# returns (button, dropdown). Caller should add_widget(button) and bind(dropdown)
def create_dropdown(options, width, pos_hint, init_idx):
    dd = DropDown()

    # create a big main button. Calculate the proper height.
    mainbutton = Button(text=options[init_idx], pos_hint=pos_hint)
    mainbutton.texture_update()
    height = int(mainbutton.texture_size[1] * 1.6) # button height = text size + padding

    mainbutton.size_hint=(None, None)
    mainbutton.size=( int(width * Window.width), height)
    mainbutton.bind(on_release=dd.open)

    for txt in options:
        btn = Button(text = txt, size_hint_y = None, height = height)
        btn.bind(on_release=lambda btn: dd.select(btn.text))
        dd.add_widget(btn)

    dd.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x) )

    # return mainbutton (for widget addition) and dropdown (for binding to on_select)
    return mainbutton, dd


class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

        # current config data
        self.config_data = load_audio_config()
        print(self.config_data)

        # list of available input / output devices
        devs = get_audio_devices()
        input_devices = devs['input']
        output_devices = devs['output']

        # float layout allows us to specify positions as percentage of screen dimensions
        layout = FloatLayout(size=(Window.width, Window.height))
        self.add_widget(layout)

        # label
        layout.add_widget(create_fixed_label("Audio Buffer Size", {'x':.02, 'y':.9}))

        # text input
        ti = create_text_input(str(self.config_data['buffersize']), 0.1, {'x':.02, 'y':.85})
        ti.bind(on_text_validate = self.set_buffersize)
        layout.add_widget(ti)

        # label
        layout.add_widget(create_fixed_label("Sample Rate", {'x':.02, 'y':.75}))

        # text input
        ti = create_text_input(str(self.config_data['samplerate']), 0.1, {'x':.02, 'y':.70})
        ti.bind(on_text_validate = self.set_samplerate)
        layout.add_widget(ti)

        # label
        layout.add_widget(create_fixed_label("Input Device", {'x':.02, 'y':.60}))

        # drop down menu
        idx = self.choose_device(input_devices, self.config_data['inputdevice'])
        self.input_options = ['{name} [{index}]'.format(**d) for d in input_devices]
        mb, dd = create_dropdown(self.input_options, .4, {'x':.02, 'y':.55}, idx)
        layout.add_widget(mb)
        dd.bind(on_select=self.set_input)

        # label
        layout.add_widget(create_fixed_label("Output Device", {'x':.02, 'y':.45}))

        # drop down menu
        idx = self.choose_device(output_devices, self.config_data['outputdevice'])
        self.output_options = ['{name} [{index}]'.format(**d) for d in output_devices]
        mb, dd = create_dropdown(self.output_options, .4, {'x':.02, 'y':.40}, idx)
        layout.add_widget(mb)
        dd.bind(on_select=self.set_output)

    # find the device based on index value and return its position in the devices list
    def choose_device(self, devices, index):
        options = [i for i,d in enumerate(devices) if d['index'] == index]
        if len(options):
            return options[0]
        else:
            return 0

    def set_buffersize(self, textinput):
        if textinput.text.isdigit():
            self.config_data['buffersize'] = int(textinput.text)
            save_audio_config(self.config_data)
        else:
            textinput.text = str(self.config_data['buffersize'])

    def set_samplerate(self, textinput):
        if textinput.text.isdigit():
            self.config_data['samplerate'] = int(textinput.text)
            save_audio_config(self.config_data)
        else:
            textinput.text = str(self.config_data['samplerate'])

    # find the number in the square brackets, like [0] or [1], also [None]
    def index_from_device_text(self, txt):
        mo = re.search('\[(\d+|None)\]', txt)
        return mo.groups()[-1]

    def set_input(self, obj, txt):
        idx = self.index_from_device_text(txt)
        self.config_data['inputdevice'] = idx
        save_audio_config(self.config_data)

    def set_output(self, obj, txt):
        idx = self.index_from_device_text(txt)
        self.config_data['outputdevice'] = idx
        save_audio_config(self.config_data)



run(MainWidget)
