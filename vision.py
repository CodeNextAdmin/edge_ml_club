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

import os.path
import platform
import sys

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.adapters import detect

_EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]

FACE_DETECTION_MODEL = 'ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite'
OBJECT_DETECTION_MODEL = 'ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite'
OBJECT_DETECTION_LABELS = 'coco_labels.txt'
CLASSIFICATION_MODEL = 'tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite'
CLASSIFICATION_LABELS = 'imagenet_labels.txt'

CORAL_COLOR = (86, 104, 237)

def make_interpreter(model_file):
  model_file, *device = model_file.split('@')
  return tflite.Interpreter(
      model_path=model_file,
      experimental_delegates=[tflite.load_delegate(_EDGETPU_SHARED_LIB,
                              {'device': device[0]} if device else {})])

class Detector:
  def __init__(self, model):
    self.interpreter = make_interpreter(model)
    self.interpreter.allocate_tensors()

  def get_objects(self, frame, threshold=0.01):
    height, width, _ = frame.shape
    _, scale = common.set_resized_input(self.interpreter, (width, height),
                                        lambda size: cv2.resize(frame, size, fx=0, fy=0,
                                                                interpolation=cv2.INTER_CUBIC))
    self.interpreter.invoke()
    return detect.get_objects(self.interpreter, threshold, scale)

class Classifier:
  def __init__(self, model):
    self.interpreter = make_interpreter(model)
    self.interpreter.allocate_tensors()

  def get_classes(self, frame, top_k=1, threshold=0.0):
    size = common.input_size(self.interpreter)
    common.set_input(self.interpreter, cv2.resize(frame, size, fx=0, fy=0, interpolation = cv2.INTER_CUBIC))
    self.interpreter.invoke()
    return classify.get_classes(self.interpreter, top_k, threshold)

def draw_objects(frame, objs, labels=None, color=CORAL_COLOR, thickness=5):
  for obj in objs:
    bbox = obj.bbox
    cv2.rectangle(frame, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), color, thickness)
    if labels:
      cv2.putText(frame, labels.get(obj.id), (bbox.xmin + thickness, bbox.ymax - thickness),
                  fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=CORAL_COLOR, thickness=2)

def draw_classes(frame, classes, labels, color=CORAL_COLOR):
  for index, score in classes:
    label = '%s (%.2f)' % (labels.get(index, 'n/a'), score)
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2.0, color, 2)

def get_frames(title='Raspimon camera', size=(640, 480), handle_key=None):
  width, height = size

  if not handle_key:
    def handle_key(key, frame):
      if key == ord('q') or key == ord('Q'):
        return False
      return True

  attempts = 5
  while True:
    cap = cv2.VideoCapture(0)
    success, _ = cap.read()
    if success:
      print("Camera started successfully.")
      break

    if attempts == 0:
      print("Cannot initialize camera!", file=sys.stderr)
      sys.exit(1)

    cap.release()
    attempts -= 1

  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
  while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if success:
      yield frame
      cv2.imshow(title, frame)

    key = cv2.waitKey(1)
    if key != -1 and not handle_key(key, frame):
      break

  cap.release()
  cv2.destroyAllWindows()

def save_frame(filename, frame):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  cv2.imwrite(filename, frame)
