from phidias.Types import *
import threading
import time
import azure.cognitiveservices.speech as speechsdk

class TIMEOUT(Reactor): pass
class STT(Reactor): pass
class HOTWORD_DETECTED(Reactor): pass

# ----------- Azure section

speech_key, service_region = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "westus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)


# ----------- Porcupine section

import os
import struct
from datetime import datetime
from threading import Thread
import pvporcupine
import pyaudio

#  keywords available:
#  alexa, americano, blueberry, bumblebee, computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator


class PorcupineDemo(Thread):

    def __init__(self):
        super(PorcupineDemo, self).__init__()

    def run(self):

        keywords = ["blueberry"]
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in keywords]
        sensitivities = [0.5] * len(keyword_paths)

        keywords = list()
        for x in keyword_paths:
            keywords.append(os.path.basename(x).replace('.ppn', '').split('_')[0])

        porcupine = pvporcupine.create(
            library_path=pvporcupine.LIBRARY_PATH,
            model_path=pvporcupine.MODEL_PATH,
            keyword_paths=keyword_paths,
            sensitivities=sensitivities)

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=None)

        print('\nListening {')
        for keyword, sensitivity in zip(keywords, sensitivities):
            print('  %s (%.2f)' % (keyword, sensitivity))
        print('}')

        FOUND_WORD = False

        while FOUND_WORD is False:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
                FOUND_WORD = True

        audio_stream.close()
        pa.terminate()
        porcupine.delete()



class HotwordDetect(Sensor):

    def on_start(self):
       self.running = True
       print("\nStarting Hotword detection...")
       # put instantiation hotword code here

    def on_stop(self):
        print("\nStopping Hotword detection...")
        self.running = False

    def sense(self):
        while self.running is True:
            PorcupineDemo().run()
            self.assert_belief(HOTWORD_DETECTED("ON"))
            self.running = False



class UtteranceDetect(Sensor):

    def on_start(self):
       self.running = True
       print("\nStarting utterance detection...")
       # instantiate hotword engine here

    def on_stop(self):
        print("\nStopping utterance detection...")
        speech_recognizer.stop_continuous_recognition()
        self.running = False

    def sense(self):
        while self.running:
           #time.sleep(1)
           # --------------> put utterance detection code here <---------------
           # when incoming new utterance detected: self.assert_belief(STT(utterance))

           start_time = time.time()
           result = speech_recognizer.recognize_once()

           # Checks result.
           if result.reason == speechsdk.ResultReason.RecognizedSpeech:
               print("Recognized: {}".format(result.text))

               detection_time = time.time() - start_time
               print("\nDetection time: ", detection_time)

               self.assert_belief(STT(result.text))



class Timer(Sensor):

    def on_start(self, uTimeout):
        evt = threading.Event()
        self.event = evt
        self.timeout = uTimeout()
        self.do_restart = False

    def on_restart(self, uTimeout):
        self.do_restart = True
        self.event.set()

    def on_stop(self):
        self.do_restart = False
        self.event.set()

    def sense(self):
        while True:
            self.event.wait(self.timeout)
            self.event.clear()
            if self.do_restart:
                self.do_restart = False
                continue
            if self.stopped:
                return
            else:
                self.assert_belief(TIMEOUT("ON"))
                return
