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
import queue
import os.path
import select
import sys
import termios
import time
import threading
import tty

import vision

from pycoral.utils.dataset import read_label_file

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

@contextlib.contextmanager
def worker(process):
  requests = queue.Queue()

  def run():
    while True:
      request = requests.get()
      if request is None:
        break
      process(request)
      requests.task_done()

  def submit(request):
    requests.put(request)

  thread = threading.Thread(target=run)
  thread.start()
  try:
    yield submit
  finally:
    requests.put(None)
    thread.join()

def save_frame(request):
  filename, frame = request
  vision.save_frame(filename, frame)
  print('Saved: %s' % filename)

def main():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--labels', '-l', type=str, default=None, help='Labels file')
  parser.add_argument('--output_dir', '-d', type=str, default='capture', help='Output director')
  args = parser.parse_args()

  print("Press buttons '0' .. '9' to save images from the camera.")

  labels = {}
  if args.labels:
    labels = read_label_file(args.labels)
    for key in sorted(labels):
      print(key, '-', labels[key])

  with nonblocking(sys.stdin) as get_char, worker(save_frame) as submit:
    # Handle key events from GUI window.
    def handle_key(key, frame):
      if key == ord('q') or key == ord('Q'):
        return False  # Stop processing frames.
      if ord('0') <= key <= ord('9'):
        label_id = key - ord('0')
        class_dir = labels.get(label_id, str(label_id))
        name = str(round(time.time() * 1000)) + '.png'
        filename = os.path.join(args.output_dir, class_dir, name)
        submit((filename, frame.copy()))
      return True  # Keep processing frames.

    for frame in vision.get_frames(handle_key=handle_key):
      # Handle key events from console.
      ch = get_char()
      if ch is not None and not handle_key(ord(ch), frame):
        break

if __name__ == '__main__':
  main()
