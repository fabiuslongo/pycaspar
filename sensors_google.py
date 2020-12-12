from __future__ import division
from phidias.Types import *
import threading
import sys


class TIMEOUT(Reactor): pass
class STT(Reactor): pass
class HOTWORD_DETECTED(Reactor): pass


# ----------- Google section

from google.cloud import speech
import pyaudio
from six.moves import queue
import time

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Audio recording parameters
STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
CWHITE  = '\33[0m'
BLUE = '\33[34m'

def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))

class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):

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

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""

        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset)
                        / chunk_time
                    )

                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b"".join(data)


client = speech.SpeechClient()
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=SAMPLE_RATE,
    language_code="en-US",
    max_alternatives=1,
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True
)


# ----------- Porcupine section

import os
import struct
from datetime import datetime
from threading import Thread
import pvporcupine

#  keywords available:
#  alexa, americano, blueberry, bumblebee, computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator

# -----------------------------------------------------------------------


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
                sys.stdout.write(CWHITE)
                FOUND_WORD = True

        audio_stream.close()
        pa.terminate()
        porcupine.delete()










class HotwordDetect(Sensor):

    def on_start(self):
       self.running = True
       print("\nStarting Hotword detection...")

    def on_stop(self):
        print("\nStopping Hotword detection...")
        self.running = False

    def sense(self):
        while self.running:
            sys.stdout.write(BLUE)
            PorcupineDemo().run()
            self.assert_belief(HOTWORD_DETECTED("ON"))
            self.running = False





class UtteranceDetect(Sensor):

    def on_start(self):
       self.running = True
       self.mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
       print("\nStarting utterance detection...")

    def on_stop(self):
        print("\nStopping utterance detection...")
        self.running = False
        self.mic_manager.closed = True

    def on_restart(self, *args):
        print("\nRestarting utterance detection...")
        self.running = True
        self.mic_manager.closed = False


    def sense(self):

        with self.mic_manager as stream:

            while self.running:
                sys.stdout.write(YELLOW)
                sys.stdout.write(
                    "\n" + str(STREAMING_LIMIT * stream.restart_counter) + ": NEW REQUEST\n"
                )

                stream.audio_input = []
                audio_generator = stream.generator()

                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )

                responses = client.streaming_recognize(streaming_config, requests)

                for response in responses:

                    if get_current_time() - stream.start_time > STREAMING_LIMIT:
                        stream.start_time = get_current_time()
                        break

                    if not response.results:
                        continue

                    result = response.results[0]

                    if not result.alternatives:
                        continue

                    transcript = result.alternatives[0].transcript

                    result_seconds = 0
                    result_micros = 0

                    if result.result_end_time.seconds:
                        result_seconds = result.result_end_time.seconds

                    if result.result_end_time.microseconds:
                        result_micros = result.result_end_time.microseconds

                    stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))

                    corrected_time = (
                            stream.result_end_time
                            - stream.bridging_offset
                            + (STREAMING_LIMIT * stream.restart_counter)
                    )
                    # Display interim results, but with a carriage return at the end of the
                    # line, so subsequent lines will overwrite them.

                    if result.is_final:

                        sys.stdout.write(GREEN)
                        sys.stdout.write("\033[K")
                        sys.stdout.write(str(corrected_time) + ": " + transcript + "\n")

                        stream.is_final_end_time = stream.result_end_time
                        stream.last_transcript_was_final = True

                        self.mic_manager.closed = True
                        self.running = False

                        self.assert_belief(STT(transcript.strip()))

                    else:
                        sys.stdout.write(RED)
                        sys.stdout.write("\033[K")
                        sys.stdout.write(str(corrected_time) + ": " + transcript + "\r")

                        stream.last_transcript_was_final = False


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
