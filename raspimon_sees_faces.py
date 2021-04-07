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

from sense_hat import SenseHat
from time import sleep
from math import floor
import vision
from detect import BBox
from bestiary import Volt

FOV_COLUMNS = 3
FOV_ROWS = 2

# initialize SenseHat instance and clear the LED matrix
sense = SenseHat()
sense.set_pixels(Volt.LOOK_UP)


def get_fov_bboxes(image_size):
  """Returns a list of BBox objects representing each cell in the
     raspimon's field of view (FOV)."""
  cell_width = image_size[0] / FOV_COLUMNS
  cell_height = image_size[1] / FOV_ROWS
  bboxes = []
  ymin = 0
  for row in range(FOV_ROWS):
    xmin = 0
    for column in range(FOV_COLUMNS):
      bbox = BBox(xmin, ymin, xmin + cell_width, ymin + cell_height)
      bboxes.append(bbox)
      xmin = xmin + cell_width
    ymin = ymin + cell_height
  return bboxes


def get_location(bbox, image_size):
  """Returns the index position of the cell where the given BBox
     currently appears. The image_size is (width, height) """
  fov_bboxes = get_fov_bboxes(image_size)
  # Create a center-point box (a small box representing the face center)
  pbox = BBox(bbox.xmin, bbox.ymin, bbox.xmin + 1, bbox.ymin + 1)
  pbox = pbox.translate(floor(bbox.width/2), floor(bbox.height/2))
  # Check which cell the currently intersects with the face center
  for index, fov_box in enumerate(fov_bboxes):
    if BBox.iou(pbox, fov_box) > 0:
      return index


def react_to_faces(faces):
  """Redraw the raspimon in response to detected faces."""
  if (len(faces) == 1):
    face_loc = get_location(faces[0].bbox, (640, 480))
    if face_loc == 0:
      sense.set_pixels(Volt.LOOK_UP_LEFT)
    elif face_loc == 1:
        sense.set_pixels(Volt.LOOK_UP)
    elif face_loc == 2:
        sense.set_pixels(Volt.LOOK_UP_RIGHT)
    elif face_loc == 3:
        sense.set_pixels(Volt.LOOK_DOWN_LEFT)
    elif face_loc == 4:
        sense.set_pixels(Volt.LOOK_DOWN)
    elif face_loc == 5:
        sense.set_pixels(Volt.LOOK_DOWN_RIGHT)


# load the neural network model (obfuscates use of TF and Edge TPU)
detector = vision.Detector(vision.FACE_DETECTION_MODEL)

# run a loop to run the model in real-time
for frame in vision.get_frames():
  faces = detector.get_objects(frame)
  # Draw bounding boxes on the frame and display it
  vision.draw_objects(frame, faces)
  # Pass faces to function that controls raspimon
  react_to_faces(faces)
