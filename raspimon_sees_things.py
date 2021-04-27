from pycoral.utils.dataset import read_label_file
import vision
from sense_hat import SenseHat
from threading import Thread
from queue import Queue

def react_to_things(queue):
    while True:
        classes = queue.get()
        if classes:
            label_id = classes[0].id
            score = classes[0].score
            label = labels.get(label_id)
            if score > 0.5:
                sense.show_message(label, scroll_speed=0.05)

# Main program ------------------------

classes_queue = Queue()
sensehat_thread = Thread(target=react_to_things, args=[classes_queue], daemon=True)
sensehat_thread.start()

sense = SenseHat()
sense.clear()

# Load the neural network model
classifier = vision.Classifier(vision.CLASSIFICATION_MODEL)
labels = read_label_file(vision.CLASSIFICATION_LABELS)

# Run a loop to get images and process them in real-time
for frame in vision.get_frames():
  # Get list of all recognized objects in the frame
  classes = classifier.get_classes(frame)
  label_id = classes[0].id
  score = classes[0].score
  label = labels.get(label_id)
  print(label, score)
  # Draw the label name on the video
  vision.draw_classes(frame, classes, labels)
  classes_queue.put(classes)

