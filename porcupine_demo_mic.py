#
# Copyright 2018-2020 Picovoice Inc.
#
# You may not use this file except in compliance with the license. A copy of the license is located in the "LICENSE"
# file accompanying this source.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

import argparse
import os
import struct
from datetime import datetime
from threading import Thread

import numpy as np
import pvporcupine
import pyaudio
import soundfile


#  keywords available:
#  alexa, americano, blueberry, bumblebee, computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator


class PorcupineDemo():

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

        print('Listening {')
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

                #porcupine.delete()
                #audio_stream.close()
                #pa.terminate()



def main():

    PorcupineDemo().run()



if __name__ == '__main__':
    main()
