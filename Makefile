SHELL=/bin/bash
TEST_DATA_URL=https://github.com/google-coral/test_data/raw/master
VENV_NAME=.env

.PHONY: venv deb download clean

venv:
	rm -rf $(VENV_NAME)
	python3 -m venv --system-site-packages $(VENV_NAME)
	$(SHELL) -c "source $(VENV_NAME)/bin/activate && pip3 install --upgrade pip"
	$(SHELL) -c "source $(VENV_NAME)/bin/activate && pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite-runtime pycoral"

deb:
	sudo apt-get install -y python3-numpy python3-pyaudio python3-opencv

coco_labels.txt:
	wget "$(TEST_DATA_URL)/$@" -P models/

ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite:
	wget "$(TEST_DATA_URL)/$@" -P models/

imagenet_labels.txt:
	wget "$(TEST_DATA_URL)/$@" -P models/

ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite:
	wget "$(TEST_DATA_URL)/$@" -P models/

tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite:
	wget "$(TEST_DATA_URL)/$@" -P models/

labels_gc2.raw.txt:
	wget "https://github.com/google-coral/project-keyword-spotter/raw/master/config/$@" -P models/

voice_commands_v0.7_edgetpu.tflite:
	wget "https://github.com/google-coral/project-keyword-spotter/raw/master/models/$@" -P models/

download: coco_labels.txt \
          ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
          imagenet_labels.txt \
          ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite \
          tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite \
          labels_gc2.raw.txt \
          voice_commands_v0.7_edgetpu.tflite

clean:
	rm -rf __pycache__ \
	       models
