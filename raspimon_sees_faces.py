from sense_hat import SenseHat
import vision
from time import sleep
from pycoral.adapters.detect import BBox
from bestiary import Volt

#   The video image is divided into
#   numbered squares like this:
#
#   -------------------
#   |     |     |     |
#   |  0  |  1  |  2  |
#   -------------------
#   |     |     |     |
#   |  3  |  4  |  5  |
#   -------------------

### Set the number of squares for the "field of view" (FOV)
FOV_COLUMNS =
FOV_ROWS =

# Set the available poses; length must match the total FOV squares
VOLT_POSES = [
  Volt.LOOK_UP_LEFT,
  Volt.LOOK_UP,
  Volt.LOOK_UP_RIGHT,
  Volt.LOOK_DOWN_LEFT,
  Volt.LOOK_DOWN,
  Volt.LOOK_DOWN_RIGHT
]

def get_fov_bboxes(image_size):
  """
  Gets a list of bounding-boxes, representing each cell in the FOV.

  Args:
    image_size (x,y): A tuple with the image height and width
  Returns:
    A list of `BBox` objects representing each cell in the
    Raspimon's field of view (FOV). These are in sequence from
    left-to-right and top-to-bottom (top-left is first).
    See https://coral.ai/docs/reference/py/pycoral.adapters/#pycoral.adapters.detect.BBox
  """
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
  """
  Get the FOV cell where the given BBox currently appears.

  Args:
    bbox: The `BBox` you want to locate
    image_size (x,y): A tuple with the image height and width
  Returns:
    The FOV cell that contains the BBox (based on the BBox center point); this is
    the cell's index position, from left-to-right and top-to-bottom in the image
    (top-left is position 0).
  """

  # Get the center point for the face bounding-box
  face_x, face_y = get_center_point(bbox)

  # Get coordinates for each box in the raspimon field of view (FOV)
  fov_bboxes = get_fov_bboxes(image_size)

  # Find which FOV box currently holds the center point
  for index, fov_bbox in enumerate(fov_bboxes):
    if is_point_in_box(face_x, face_y, fov_bbox):
      return index
  return None


def react_to_faces(faces):
  """
  Redraw the Raspimon in response to the face location.

  Args:
    faces: A list of `Object` objects, representing detected faces.
    See https://coral.ai/docs/reference/py/pycoral.adapters/#pycoral.adapters.detect.Object
  """
  if (len(faces) == 1):
    # Get the location of the face (one of six positions)
    face_loc = get_location(faces[0].bbox, vision.VIDEO_SIZE)
    # Set the Raspimon pose
    if face_loc is not None:
        sense.set_pixels(VOLT_POSES[face_loc])


### CREATE A LOOP TO SHOW ALL RASPIMON POSES
def roll_eyes():
    print("roll eyes")


### FIX IN THIS FUNCTION
def is_point_in_box(x, y, bbox):
    """
    Check if the given (x,y) point lies within the given box.

    Args:
      x (int): The X-coordinate for the point
      y (int): The Y-coordinate for the point
      bbox (BBox): A `BBox` (bounding box) object
    Returns:
      True if the point is inside the bounding box; False otherwise
    """
    if x < 200 and y < 200:
        return True
    return False


### FIX IN THIS FUNCTION
def get_center_point(bbox):
    """
    Return the center point for the given box, as (x,y) position.

    Args:
      bbox (BBox): A `BBox` (bounding box) object
    Returns:
      A tuple as (x,y), representing the center of the box
    """
    x_middle = 42
    y_middle = 42

    # HINT: bbox.xmin, bbox,xmax, bbox.ymin, bbox.ymax
    return (x_middle, y_middle)


### FINISH THIS CODE ------------------------

# initialize SenseHat instance and set raspimon
sense = SenseHat()
sense.set_pixels(Volt.LOOK_UP)
#sense.set_rotation(270)

# Load the neural network model

# Run a loop to get images and process them in real-time

    # Draw bounding boxes on the frame and display it

    # Experiment code:


    # Pass faces to function that controls raspimon
