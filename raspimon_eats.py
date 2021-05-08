from sense_hat import SenseHat
from sense_hat import stick
from time import sleep
from random import randint

# Constants
D_UP = stick.DIRECTION_UP
D_DOWN = stick.DIRECTION_DOWN
D_LEFT = stick.DIRECTION_LEFT
D_RIGHT = stick.DIRECTION_RIGHT
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLANK = (0, 0, 0)
DELAY = 1.0

# Variables
raspimon = [2,4]
berries = []
direction = D_UP


def move():
  """Performs all LED updates in each game cycle, including eating berries."""

  global raspimon

  # Copy the current position
  next = list(raspimon)

  # Find the next pixel in the direction the slug is currently moving
  if direction == D_UP:
    if raspimon[1] - 1 == -1:
      next[1] = 7
    else:
      next[1] = raspimon[1] - 1

  elif direction == D_DOWN:
    if raspimon[1] + 1 == 8:
      next[1] = 0
    else:
      next[1] = raspimon[1] + 1

  ###
  ### Fill in the "left" and "right" conditions
  ###

  # Update the position
  sense.set_pixel(raspimon[0], raspimon[1], BLANK)
  sense.set_pixel(next[0], next[1], WHITE)

  # If next position is a berry, eat it
  if next in berries:
    berries.remove(next)

  raspimon = next


def joystick_moved(event):
  """
  Update the Raspimon's direction based on callback from joystick events.
  Args:
    event: An `InputEvent` from SenseHat.stick
  """
  global direction
  direction = event.direction


### Finish this function
def change_direction(label):
  """
  Change the Raspimon's direction based on voice command.
  Args:
    label (str): The recognized voice command label
  """
  global direction
  if label.endswith("up"):
    direction = D_UP
  elif label.endswith("down"):
    direction = D_DOWN


def generate_berries():
  """Draw a new berry at a random location."""
  while len(berries) < 5:
    x = randint(0, 7)
    y = randint(0, 7)
    if [x,y] in berries or [x,y] == raspimon:
      continue
    sense.set_pixel(x, y, RED)
    berries.append([x,y])



# Main program ------------------------

sense = SenseHat()
sense.clear()

# Set callback for joystick events
sense.stick.direction_any = joystick_moved

###
### Add listener for speech detection model
###

# Add berries to screen
generate_berries()

# Main game loop
while True:
  ###
  ### Respond to speech detection results
  ###

  move()
  sleep(DELAY)

  if len(berries) == 0:
    break

sense.clear()
