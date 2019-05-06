
import speech_recognition as sr # also implicity requires pyaudio

class SpeechController(object):
    def __init__(self, output_func):
        self.output_func = output_func
        self.recognizer = None
        self.microphone = None
        self.stop_listening = None

    def process_audio(self, recognizer, audio):
        try:
            recognized_speech = recognizer.recognize_google(audio)
            if recognized_speech != None:
                print(recognized_speech)

        except sr.UnknownValueError:
            # print("Speech recognition could not understand audio")
            pass
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))

    def start(self):
        print("Speech control addon started")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # starts listening in the background
        self.stop_listening = self.recognizer.listen_in_background(self.microphone, self.process_audio)
        
    def stop(self):
        print("Speech control addon stopped")
        if self.stop_listening != None: self.stop_listening()
        