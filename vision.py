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

FACE_DETECTION_MODEL = 'models/ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite'
OBJECT_DETECTION_MODEL = 'models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite'
OBJECT_DETECTION_LABELS = 'models/coco_labels.txt'
CLASSIFICATION_MODEL = 'models/tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite'
CLASSIFICATION_LABELS = 'models/imagenet_labels.txt'

VIDEO_SIZE = (640, 480)
CORAL_COLOR = (86, 104, 237)
BLUE = (255, 0, 0) # BGR (not RGB)

def make_interpreter(model_file):
  model_file, *device = model_file.split('@')
  return tflite.Interpreter(
      model_path=model_file,
      experimental_delegates=[tflite.load_delegate(_EDGETPU_SHARED_LIB,
                              {'device': device[0]} if device else {})])

#########################
### VISION MODEL APIS ###
#########################

class Detector:
  """Performs inferencing with an object detection model.

  Args:
    model: Path to a `.tflite` file (compiled for the Edge TPU). Must be an SSD model.
  """
  def __init__(self, model):
    self.interpreter = make_interpreter(model)
    self.interpreter.allocate_tensors()

  def get_objects(self, frame, threshold=0.01):
    """
    Gets a list of objects detected in the given image frame.

    Args:
      frame: The bitmap image to pass through the model.
      threshold: The minimum confidence score for returned results.

    Returns:
      A list of `Object` objects, each of which contains a detected object's
      id, score, and bounding box as `BBox`.
      See https://coral.ai/docs/reference/py/pycoral.adapters/#pycoral.adapters.detect.Object
    """
    height, width, _ = frame.shape
    _, scale = common.set_resized_input(self.interpreter, (width, height),
                                        lambda size: cv2.resize(frame, size, fx=0, fy=0,
                                                                interpolation=cv2.INTER_CUBIC))
    self.interpreter.invoke()
    return detect.get_objects(self.interpreter, threshold, scale)

class Classifier:
  """Performs inferencing with an image classification model.

  Args:
    model: Path to a `.tflite` file (compiled for the Edge TPU). Must be a classification model.
  """
  def __init__(self, model):
    self.interpreter = make_interpreter(model)
    self.interpreter.allocate_tensors()

  def get_classes(self, frame, top_k=1, threshold=0.0):
    """
    Gets classification results as a list of ordered classes.

    Args:
      frame: The bitmap image to pass through the model.
      top_k: The number of top results to return.
      threshold: The minimum confidence score for returned results.

    Returns:
      A list of `Class` objects representing the classification results, ordered by scores.
      See https://coral.ai/docs/reference/py/pycoral.adapters/#pycoral.adapters.classify.Class
    """
    size = common.input_size(self.interpreter)
    common.set_input(self.interpreter, cv2.resize(frame, size, fx=0, fy=0, interpolation = cv2.INTER_CUBIC))
    self.interpreter.invoke()
    return classify.get_classes(self.interpreter, top_k, threshold)

#############################
### CAMERA & DISPLAY APIS ###
#############################

def draw_objects(frame, objs, labels=None, color=CORAL_COLOR, thickness=5):
  """
  Draws bounding boxes for detected objects on the display output.

  Args:
    frame: The bitmap frame to draw upon.
    objs: A list of `Object` objects for which you want to draw bounding boxes on the frame.
    labels: The labels file corresponding to the model used for object detection.
    color: The RGB color to use for the bounding box.
    thickness: The bounding box pixel thickness.
  """
  for obj in objs:
    bbox = obj.bbox
    cv2.rectangle(frame, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), color, thickness)
    if labels:
      cv2.putText(frame, labels.get(obj.id), (bbox.xmin + thickness, bbox.ymax - thickness),
                  fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=CORAL_COLOR, thickness=2)

def draw_circle(frame, point, radius, color=CORAL_COLOR, thickness=5):
  """Draws a circle onto the frame."""
  cv2.circle(frame, point, radius, color, thickness)


def draw_rect(frame, bbox, color=BLUE, thickness=5):
  """Draws a rectangle onto the frame."""
  cv2.rectangle(frame, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), color, thickness)


def draw_classes(frame, classes, labels, color=CORAL_COLOR):
  """
  Draws the image classification name on the display output.

  Args:
    frame: The bitmap frame to draw upon.
    classes: A list of `Class` objects representing the classified objects.
    labels: The labels file corresponding to model used for image classification.
    color: The RGB color to use for the text.
  """
  for index, score in classes:
    label = '%s (%.2f)' % (labels.get(index, 'n/a'), score)
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2.0, color, 2)

def get_frames(title='Raspimon camera', size=VIDEO_SIZE, handle_key=None,
               capture_device_index=0):
  """
  Gets a stream of image frames from the default camera.

  Args:
    title: A title for the display window.
    size: The image resolution for all frames, as a tuple (x, y).
    handle_key: A callback function that accepts arguments (key, frame) for a key event and
      the image frame from the moment the key was pressed.
  Returns:
    An iterator that yields each image frame from the default camera.
  """
  width, height = size

  if not handle_key:
    def handle_key(key, frame):
      if key == ord('q') or key == ord('Q'):
        return False
      return True

  attempts = 5
  while True:
    cap = cv2.VideoCapture(capture_device_index)
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

  try:
    while True:
      success, frame = cap.read()
      frame = cv2.flip(frame, 1)
      if success:
        yield frame
        cv2.imshow(title, frame)

      key = cv2.waitKey(1)
      if key != -1 and not handle_key(key, frame):
        break
  finally:
    cap.release()
    cv2.destroyAllWindows()

def save_frame(filename, frame):
  """
  Saves an image to a specified location.

  Args:
    filename: The path where you'd like to save the image.
    frame: The bitmap image to save.
  """
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  cv2.imwrite(filename, frame)
