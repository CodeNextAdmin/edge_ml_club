from sense_hat import SenseHat
from time import sleep
from math import floor
import vision
from pycoral.adapters.detect import BBox
from bestiary import Volt

FOV_COLUMNS =
FOV_ROWS =

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

  # Create a center-point box (a small box representing the face center)

  # Get coordinates for each box in the raspimon field of view (FOV)

  # Check which box in FOV currently intersects with the face center



def react_to_faces(faces):
  """Redraw the raspimon in response to detected faces."""
  # First get the location of the face (one of six positions)


# Main program ------------------------

# Load the neural network model

# Run a loop to get images and process them in real-time
  # Draw bounding boxes on the frame and display it
  # Pass faces to function that controls raspimon
