from __future__ import division
from phidias.Types import *
import threading
import time

import re
import sys

class TIMEOUT(Reactor): pass
class STT(Reactor): pass


from google.cloud import speech

import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self


    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)




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

        language_code = "en-US"  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=RATE, language_code=language_code)
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

        while self.running:

            with MicrophoneStream(RATE, CHUNK) as stream:
                audio_generator = stream.generator()
                requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

                responses = client.streaming_recognize(streaming_config, requests)

                num_chars_printed = 0
                for response in responses:
                    if not response.results:
                        continue

                    result = response.results[0]
                    if not result.alternatives:
                        continue

                    transcript = result.alternatives[0].transcript
                    overwrite_chars = " " * (num_chars_printed - len(transcript))

                    if not result.is_final:

                        sys.stdout.write(transcript + overwrite_chars + "\r")
                        sys.stdout.flush()

                        num_chars_printed = len(transcript)

                    else:
                        if self.running:
                            print("transcript: ", transcript + overwrite_chars)
                            self.assert_belief(STT(transcript + overwrite_chars))
                            num_chars_printed = 0
                        else:
                            stream.__exit__(None, None, None)





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
