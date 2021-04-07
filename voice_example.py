# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import voice

def callback(label, score):
  print(label, score)
  if label.startswith('exit'):
    return False # stop listening
  return True # keep listening

def run_classify_audio():
  voice.classify_audio(model_file=voice.VOICE_MODEL,
                       labels_file=voice.VOICE_LABELS,
                       callback=callback)

def run_audio_classifier():
  c = voice.AudioClassifier(model_file=voice.VOICE_MODEL,
                            labels_file=voice.VOICE_LABELS,
                            audio_device_index=2)
  while True:
    label, score = c.next()
    print(label, score)

if __name__ == '__main__':
  #run_classify_audio()
  run_audio_classifier()
