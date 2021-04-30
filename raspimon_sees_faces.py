from sense_hat import SenseHat
from time import sleep
import vision
from pycoral.adapters.detect import BBox
from bestiary import Volt

# Set the number of "field of view" squares
FOV_COLUMNS = 3
FOV_ROWS = 2


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


def react_to_faces(faces):
  """Redraw the raspimon in response to the face location in FOV squares."""
  if (len(faces) == 1):
    # First get the location of the face (one of six positions)
    face_loc = get_location(faces[0].bbox, vision.VIDEO_SIZE)
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


def get_location(bbox, image_size):
  """Returns the index position of the cell where the given BBox
     currently appears. The image_size is (width, height) """

  # Get the center point for the face bounding-box
  face_x, face_y = get_center_point(bbox)

  # Get coordinates for each box in the raspimon field of view (FOV)
  fov_bboxes = get_fov_bboxes(image_size)

  # Find which FOV box currently holds the center point
  for index, fov_bbox in enumerate(fov_bboxes):
    if is_point_in_box(face_x, face_y, fov_bbox):
      return index


def is_point_in_box(x, y, bbox):
    """Check if the given (x,y) point lies within the given box."""
    if (x > bbox.xmin and x < bbox.xmax) and (y > bbox.ymin and y < bbox.ymax):
        return True
    return False


def get_center_point(bbox):
    """Return the center point for the given box, as (x,y) position"""
    width = bbox.xmax - bbox.xmin
    height = bbox.ymax - bbox.ymin

    half_width = int(width / 2)
    half_height = int(height / 2)

    x_middle = bbox.xmin + half_width
    y_middle = bbox.ymin + half_height

    return (x_middle, y_middle)


# Main program ------------------------

# initialize SenseHat instance and set raspimon
sense = SenseHat()
sense.set_pixels(Volt.LOOK_UP)

# Load the neural network model
detector = vision.Detector(vision.FACE_DETECTION_MODEL)

# Run a loop to get images and process them in real-time
for frame in vision.get_frames():
  faces = detector.get_objects(frame)
  # Draw bounding boxes on the frame and display it
  vision.draw_objects(frame, faces)
  # Experiment code:
  if faces:
      bbox = faces[0].bbox
      print("xmin: ", bbox.xmin)
      x, y = get_center_point(bbox)
      print("center: ", x, y)
      vision.draw_circle(frame, (x,y), 10)
  # Pass faces to function that controls raspimon
  react_to_faces(faces)
