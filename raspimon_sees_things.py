from sense_hat import SenseHat
from threading import Thread
from queue import Queue
from pycoral.utils.dataset import read_label_file
import vision

# Initialize SenseHat instance and clear the LED matrix
sense = SenseHat()
sense.clear()

# Load the neural network model
labels = read_label_file(vision.CLASSIFICATION_LABELS)
classifier = vision.Classifier(vision.CLASSIFICATION_MODEL)


def react_to_things(queue):
  """Redraw the raspimon in response to detected things."""
  while True:
    classes = queue.get()
    if classes:
      label_id, score = classes[0]
      label = labels.get(label_id, 'n/a')
      if score > 0.5:
        sense.show_message(label, scroll_speed=0.06)
      else:
        sense.show_letter('?')


# Create thread and queue to update the SenseHat
classes_queue = Queue()
sensehat_thread = Thread(target=react_to_things,
                         args=[classes_queue],
                         daemon=True)
sensehat_thread.start()


# Run a loop to run the model in real-time
for frame in vision.get_frames():
  # Get list of all recognized objects in the frame
  classes = classifier.get_classes(frame)

  # Draw the label name on the video
  vision.draw_classes(frame, classes, labels)

  # Pass the classification results to the raspimon
  if classes:
    classes_queue.put(classes)
