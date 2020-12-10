from phidias.Types import *
import threading
import time
import azure.cognitiveservices.speech as speechsdk

class TIMEOUT(Reactor): pass
class STT(Reactor): pass


speech_key, service_region = "9e4463eb92de493f890a025a9ce1fd24", "westus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

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
           time.sleep(1)
           # --------------> put hotword detection code here <---------------
           # when right hotword is detected: self.assert_belief(HOTWORD_DETECTED("ON"))




class UtteranceDetect(Sensor):

    def on_start(self):
       self.running = True
       print("\nStarting utterance detection...")
       # instantiate hotword engine here

    def on_stop(self):
        print("\nStopping utterance detection...")
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
