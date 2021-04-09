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

"""Keyword spotter model."""

import logging
import platform
import queue
import sys
import threading

import numpy as np

import audio_recorder
import mel_features

import tflite_runtime.interpreter as tflite

_EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]

logging.basicConfig(
    stream=sys.stdout,
    format="%(levelname)-8s %(asctime)-15s %(name)s %(message)s")
audio_recorder.logger.setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Uint8LogMelFeatureExtractor(object):
  """Provide uint8 log mel spectrogram slices from an AudioRecorder object.

  This class provides one public method, get_next_spectrogram(), which gets
  a specified number of spectral slices from an AudioRecorder.
  """

  def __init__(self, num_frames_hop=33):
    self.spectrogram_window_length_seconds = 0.025
    self.spectrogram_hop_length_seconds = 0.010
    self.num_mel_bins = 32
    self.frame_length_spectra = 198
    if self.frame_length_spectra % num_frames_hop:
        raise ValueError('Invalid num_frames_hop value (%d), '
                         'must devide %d' % (num_frames_hop,
                                             self.frame_length_spectra))
    self.frame_hop_spectra = num_frames_hop
    self._norm_factor = 3
    self._clear_buffers()

  def _clear_buffers(self):
    self._audio_buffer = np.array([], dtype=np.int16).reshape(0, 1)
    self._spectrogram = np.zeros((self.frame_length_spectra, self.num_mel_bins),
                                 dtype=np.float32)

  def _spectrogram_underlap_samples(self, audio_sample_rate_hz):
    return int((self.spectrogram_window_length_seconds -
                self.spectrogram_hop_length_seconds) * audio_sample_rate_hz)

  def _frame_duration_seconds(self, num_spectra):
    return (self.spectrogram_window_length_seconds +
            (num_spectra - 1) * self.spectrogram_hop_length_seconds)

  def _compute_spectrogram(self, audio_samples, audio_sample_rate_hz):
    """Compute log-mel spectrogram and scale it to uint8."""
    samples = audio_samples.flatten() / float(2**15)
    spectrogram = 30 * (
        mel_features.log_mel_spectrogram(
            samples,
            audio_sample_rate_hz,
            log_offset=0.001,
            window_length_secs=self.spectrogram_window_length_seconds,
            hop_length_secs=self.spectrogram_hop_length_seconds,
            num_mel_bins=self.num_mel_bins,
            lower_edge_hertz=60,
            upper_edge_hertz=3800) - np.log(1e-3))
    return spectrogram

  def _get_next_spectra(self, recorder, num_spectra):
    """Returns the next spectrogram.

    Compute num_spectra spectrogram samples from an AudioRecorder.
    Blocks until num_spectra spectrogram slices are available.

    Args:
      recorder: an AudioRecorder object from which to get raw audio samples.
      num_spectra: the number of spectrogram slices to return.

    Returns:
      num_spectra spectrogram slices computed from the samples.
    """
    required_audio_duration_seconds = self._frame_duration_seconds(num_spectra)
    logger.info("required_audio_duration_seconds %f",
                required_audio_duration_seconds)
    required_num_samples = int(
        np.ceil(required_audio_duration_seconds *
                recorder.audio_sample_rate_hz))
    logger.info("required_num_samples %d, %s", required_num_samples,
                str(self._audio_buffer.shape))
    audio_samples = np.concatenate(
        (self._audio_buffer,
         recorder.get_audio(required_num_samples - len(self._audio_buffer))[0]))
    self._audio_buffer = audio_samples[
        required_num_samples -
        self._spectrogram_underlap_samples(recorder.audio_sample_rate_hz):]
    spectrogram = self._compute_spectrogram(
        audio_samples[:required_num_samples], recorder.audio_sample_rate_hz)
    assert len(spectrogram) == num_spectra
    return spectrogram

  def get_next_spectrogram(self, recorder):
    """Get the most recent spectrogram frame.

    Blocks until the frame is available.

    Args:
      recorder: an AudioRecorder instance which provides the audio samples.

    Returns:
      The next spectrogram frame as a uint8 numpy array.
    """
    assert recorder.is_active
    logger.info("self._spectrogram shape %s", str(self._spectrogram.shape))
    self._spectrogram[:-self.frame_hop_spectra] = (
        self._spectrogram[self.frame_hop_spectra:])
    self._spectrogram[-self.frame_hop_spectra:] = (
        self._get_next_spectra(recorder, self.frame_hop_spectra))
    # Return a copy of the internal state that's safe to persist and won't
    # change the next time we call this function.
    logger.info("self._spectrogram shape %s", str(self._spectrogram.shape))
    spectrogram = self._spectrogram.copy()
    spectrogram -= np.mean(spectrogram, axis=0)
    if self._norm_factor:
      spectrogram /= self._norm_factor * np.std(spectrogram, axis=0)
      spectrogram += 1
      spectrogram *= 127.5
    return np.maximum(0, np.minimum(255, spectrogram)).astype(np.uint8)

def read_labels(filename):
  # The labels file can be made something like this.
  f = open(filename, "r")
  lines = f.readlines()
  return ['negative'] + [l.rstrip() for l in lines]

def get_output(interpreter):
    """Returns entire output, threshold is applied later."""
    return output_tensor(interpreter, 0)

def output_tensor(interpreter, i):
    """Returns dequantized output tensor if quantized before."""
    output_details = interpreter.get_output_details()[i]
    output_data = np.squeeze(interpreter.tensor(output_details['index'])())
    if 'quantization' not in output_details:
        return output_data
    scale, zero_point = output_details['quantization']
    if scale == 0:
        return output_data - zero_point
    return scale * (output_data - zero_point)

def input_tensor(interpreter):
    """Returns the input tensor view as numpy array."""
    tensor_index = interpreter.get_input_details()[0]['index']
    return interpreter.tensor(tensor_index)()[0]

def set_input(interpreter, data):
    """Copies data to input tensor."""
    interpreter_shape = interpreter.get_input_details()[0]['shape']
    input_tensor(interpreter)[:,:] = np.reshape(data, interpreter_shape[1:3])

def make_interpreter(model_file):
  model_file, *device = model_file.split('@')
  return tflite.Interpreter(
      model_path=model_file,
      experimental_delegates=[tflite.load_delegate(_EDGETPU_SHARED_LIB,
                              {'device': device[0]} if device else {})])

def classify_audio(model_file, labels_file, callback,
                   audio_device_index=0, sample_rate_hz=16000,
                   negative_threshold=0.6, num_frames_hop=33):
  """Acquire audio, preprocess, and classify."""
  downsample_factor = 1
  if sample_rate_hz == 48000:
    downsample_factor = 3
  # Most microphones support this
  # Because the model expects 16KHz audio, we downsample 3 fold
  recorder = audio_recorder.AudioRecorder(
      sample_rate_hz,
      downsample_factor=downsample_factor,
      device_index=audio_device_index)
  feature_extractor = Uint8LogMelFeatureExtractor(num_frames_hop=num_frames_hop)
  labels = read_labels(labels_file)

  interpreter = make_interpreter(model_file)
  interpreter.allocate_tensors()

  keep_listening = True
  prev_detection = -1
  with recorder:
    print("Ready for voice commands...")
    while keep_listening:
      spectrogram = feature_extractor.get_next_spectrogram(recorder)
      if spectrogram.mean() < 0.001:
        print("Warning: Input audio signal is nearly 0. Mic may be off ?")

      set_input(interpreter, spectrogram.flatten())
      interpreter.invoke()
      result = get_output(interpreter)

      if result[0] >= negative_threshold:
        prev_detection = -1
        continue

      detection = np.argmax(result)
      if detection == 0:
        prev_detection = -1
        continue

      if detection != prev_detection:
        keep_listening = callback(labels[detection], result[detection])
        prev_detection = detection

class AudioClassifier:
  def __init__(self, model_file, labels_file, audio_device_index=0):
    self._thread = threading.Thread(target=classify_audio,
      args=(model_file, labels_file, self._callback, audio_device_index), daemon=True)
    self._queue = queue.Queue()
    self._thread.start()

  def _callback(self, label, score):
    self._queue.put((label, score))
    return True

  def next(self, block=True):
    try:
      result = self._queue.get(block)
      self._queue.task_done()
      return result
    except queue.Empty:
      return None

VOICE_MODEL = 'models/voice_commands_v0.7_edgetpu.tflite'
VOICE_LABELS = 'models/labels_gc2.raw.txt'
