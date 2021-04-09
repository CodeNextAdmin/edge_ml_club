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

import vision
from pycoral.utils.dataset import read_label_file

def run_object_detector_example():
  detector = vision.Detector(vision.OBJECT_DETECTION_MODEL)
  labels = read_label_file(vision.OBJECT_DETECTION_LABELS)
  for frame in vision.get_frames('Object Detector', size=(640, 480)):
    objects = detector.get_objects(frame, threshold=0.2)
    vision.draw_objects(frame, objects, labels)

def run_face_detector_example():
  detector = vision.Detector(vision.FACE_DETECTION_MODEL)
  for frame in vision.get_frames('Face Detector', size=(640, 480)):
    faces = detector.get_objects(frame)
    vision.draw_objects(frame, faces)

def run_classifier_example():
  labels = read_label_file(vision.CLASSIFICATION_LABELS)
  classifier = vision.Classifier(vision.CLASSIFICATION_MODEL)
  for frame in vision.get_frames('Object Classifier', size=(640, 480)):
    classes = classifier.get_classes(frame)
    vision.draw_classes(frame, classes, labels)

if __name__ == '__main__':
  #run_classifier_example()
  run_object_detector_example()
