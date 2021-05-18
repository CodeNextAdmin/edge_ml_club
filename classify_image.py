# Copyright 2021 Google LLC
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

import argparse
import contextlib
import select
import sys
import termios
import tty

from cv2 import imread
from pycoral.utils.dataset import read_label_file
import vision

classifier = vision.Classifier(vision.CLASSIFICATION_MODEL)
labels = read_label_file(vision.CLASSIFICATION_LABELS)

@contextlib.contextmanager
def nonblocking(f):
  def get_char():
    if select.select([f], [], [], 0) == ([f], [], []):
      return sys.stdin.read(1)
    return None

  old_settings = termios.tcgetattr(sys.stdin)
  try:
    tty.setcbreak(f.fileno())
    yield get_char
  finally:
    termios.tcsetattr(f, termios.TCSADRAIN, old_settings)

def classify_image(frame):
  classes = classifier.get_classes(frame)
  label_id = classes[0].id
  score = classes[0].score
  label = labels.get(label_id)
  print(label, score)
  return classes

def classify_live():
  with nonblocking(sys.stdin) as get_char:
    # Handle key events from GUI window.
    def handle_key(key, frame):
      if key == 32: # Spacebar
        classify_image(frame)
      if key == ord('q') or key == ord('Q'):
        return False  # Quit the program
      return True  # Keep the camera alive, wait for keys

    first_pass = True
    for frame in vision.get_frames(handle_key=handle_key):
      if first_pass:
        print('Press the spacebar to classify an image from your camera.')
        first_pass = False
      # Handle key events from console.
      ch = get_char()
      if ch is not None and not handle_key(ord(ch), frame):
        break

def main():
  global classifier, labels
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-m', '--model',
                      help='File path of .tflite file. Default is vision.CLASSIFICATION_MODEL')
  parser.add_argument('-l', '--labels',
                      help='File path of labels file. Default is vision.CLASSIFICATION_LABELS')
  parser.add_argument('-i', '--input',
                      help='Image to be classified. If not given, use spacebar to capture an image.')
  args = parser.parse_args()

  if args.model:
    classifier = vision.Classifier(args.model)

  if args.labels:
    labels = read_label_file(args.labels)

  if args.input:
    frame = imread(args.input)
    classify_image(frame)
  else:
    classify_live()


if __name__ == '__main__':
  main()


