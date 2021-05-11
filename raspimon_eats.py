from sense_hat import SenseHat
from sense_hat import stick
from time import sleep
from random import randint
import voice

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
direction = D_RIGHT


def move_and_draw():
  """Performs all LED updates in each game cycle, including eating berries."""

  global raspimon

  # Copy the current position
  next = list(raspimon)

  # Find the next pixel in the direction the Raspimon is currently moving
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
  elif direction == D_LEFT:
    if raspimon[0] - 1 == -1:
      next[0] = 7
    else:
      next[0] = raspimon[0] - 1
  elif direction == D_RIGHT:
    if raspimon[0] + 1 == 8:
      next[0] = 0
    else:
      next[0] = raspimon[0] + 1

  # Update the position
  sense.set_pixel(raspimon[0], raspimon[1], BLANK)
  sense.set_pixel(next[0], next[1], WHITE)

  # If next position is a berry, eat it
  if next in berries:
    berries.remove(next)

  raspimon = next


def generate_berries():
  """Draw a new berry at a random location."""
  while len(berries) < 5:
    x = randint(0, 7)
    y = randint(0, 7)
    if [x,y] in berries or [x,y] == raspimon:
      continue
    sense.set_pixel(x, y, RED)
    berries.append([x,y])


def respond_to_joystick(event):
  """
  Update the Raspimon's direction based on a callback from joystick events.
  Args:
    event: An `InputEvent` from SenseHat.stick
  """
  global direction
  if event.direction == D_UP:
    direction = D_UP
  elif event.direction == D_DOWN:
    direction = D_DOWN
  elif event.direction == D_LEFT:
    direction = D_LEFT
  elif event.direction == D_RIGHT:
    direction = D_RIGHT


### 3. FILL IN THIS FUNCTION
def respond_to_voice(command):
  """
  Update the Raspimon's direction based on a voice command.
  Args:
    command: A voice command, as given by AudioClassifier.next()
  """


# Main program ------------------------

sense = SenseHat()
sense.clear()

# Add berries to the screen
generate_berries()

# Set callback for joystick events
sense.stick.direction_any = respond_to_joystick

### 1. CREATE LISTENER FOR SPEECH CLASSIFIER

# Main game loop
while True:
  ### 2. RESPOND TO SPEECH CLASSIFICATIONS

  move_and_draw()
  sleep(DELAY)

  if len(berries) == 0:
    break

sense.clear()
