from __future__ import division
from phidias.Types import *
import threading
import time
import sys
import os

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
    enable_automatic_punctuation=True
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True
)


# snowboy section -------------------------------------------------------

import snowboydecoder

interrupted = False


def interrupt_callback():
    global interrupted
    return interrupted

detector = snowboydecoder.HotwordDetector("Caspar.pmdl", sensitivity=0.5)




# -----------------------------------------------------------------------






class HotwordDetect(Sensor):

    def on_start(self):
       print("\nStarting Hotword detection...")
       self.running = True
       detector.set_running(True)
       evt = threading.Event()
       self.event = evt

    def on_stop(self):
        self.running = False
        detector.terminate()
        print("\nStopping Hotword detection...")
        self.event.set()

    def on_restart(self):
        print("\nRestarting hotword detection...")
        self.running = True
        detector.set_running(True)
        self.event.set()

    def sense(self):
        while self.running:
            self.event.clear()
            print("\nRunning Hotword detection...")
            detector.start(detected_callback=snowboydecoder.play_audio_file, interrupt_check=interrupt_callback, sleep_time=0.03)
            self.assert_belief(HOTWORD_DETECTED("ON"))





class UtteranceDetect(Sensor):

    def on_start(self):
       self.running = True
       self.mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
       print("\nStarting utterance detection...")

       evt = threading.Event()
       self.event = evt

    def on_stop(self):
        print("\nStopping utterance detection...")
        self.running = False
        self.mic_manager.closed = True
        self.event.set()

    def on_restart(self):
        print("\nRestarting utterance detection...")
        self.running = True
        self.mic_manager.closed = False
        self.event.set()


    def sense(self):

        while self.running:
            self.event.clear()

            with self.mic_manager as stream:

                while self.mic_manager.closed is False:
                    sys.stdout.write(YELLOW)
                    sys.stdout.write("\n" + str(STREAMING_LIMIT * stream.restart_counter) + ": NEW REQUEST\n")

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

                            stream.closed = True
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
