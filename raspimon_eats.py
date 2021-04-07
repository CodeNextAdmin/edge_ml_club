from sense_hat import SenseHat
from time import sleep
from random import randint
import voice

sense = SenseHat()

# Variables ---------------------------
raspimon = [2,4]
berries = []
direction = "right"
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLANK = (0, 0, 0)
DELAY = 1.0

# Functions ---------------------------
def move():
  global raspimon, pause

  # Copy the current position
  next = list(raspimon)

  # Find the next pixel in the direction the slug is currently moving
  if direction == "right":
    # Move along the column
    if raspimon[0] + 1 == 8:
      next[0] = 0
    else:
      next[0] = raspimon[0] + 1

  elif direction == "left":
    if raspimon[0] - 1 == -1:
      next[0] = 7
    else:
      next[0] = raspimon[0] - 1

  elif direction == "down":
    if raspimon[1] + 1 == 8:
      next[1] = 0
    else:
      next[1] = raspimon[1] + 1

  elif direction == "up":
    if raspimon[1] - 1 == -1:
      next[1] = 7
    else:
      next[1] = raspimon[1] - 1

  # Update the position
  sense.set_pixel(raspimon[0], raspimon[1], BLANK)
  sense.set_pixel(next[0], next[1], WHITE)

  # If next position is a berry, eat it
  if next in berries:
    berries.remove(next)

  raspimon = next

def joystick_moved(event):
  global direction
  direction = event.direction

def change_direction(label):
  global direction
  if label.endswith("up"):
    direction = "up"
  elif label.endswith("down"):
    direction = "down"
  elif label.endswith("left"):
    direction = "left"
  elif label.endswith("right"):
    direction = "right"

def add_berry():
  x = randint(0, 7)
  y = randint(0, 7)
  new = [x, y]
  sense.set_pixel(x, y, RED)
  berries.append(new)

# Main program ------------------------
sense.clear()
sense.stick.direction_any = joystick_moved
listener = voice.AudioClassifier(model_file=voice.VOICE_MODEL,
                                 labels_file=voice.VOICE_LABELS,
                                 audio_device_index=2)

for _ in range(5):
  add_berry()

while True:
  command = listener.next(block=False)
  if command:
    label, score = command
    change_direction(label)
    print(label, score)
  move()
  sleep(DELAY)
  if len(berries) == 0:
    break

sense.clear()
