# Copyright 2019 Google LLC
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

# Raspimon colors
r = (255, 0, 0)
g = (0, 255, 0)
b = (0, 0, 255)
k = (0, 0, 0)
w = (255, 255, 255)
c = (0, 255, 255)
y = (255, 255, 0)
o = (255, 128, 0)
n = (255, 128, 128)
p = (128, 0, 128)
d = (255, 0, 128)
l = (128, 255, 128)

class Volt:
  LOOK_UP = [
    o, y, y, y, y, y, y, o,
    o, o, n, y, y, n, o, o,
    y, k, w, y, y, w, k, y,
    y, k, k, y, y, k, k, y,
    y, y, y, k, k, y, y, y,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n
  ]
  LOOK_UP_RIGHT = [
    o, y, y, y, y, y, y, o,
    o, o, n, y, y, n, o, o,
    y, k, w, y, y, k, w, y,
    y, k, k, y, y, k, k, y,
    y, y, y, k, k, y, y, y,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n
  ]
  LOOK_UP_LEFT = [
    o, y, y, y, y, y, y, o,
    o, o, n, y, y, n, o, o,
    y, w, k, y, y, w, k, y,
    y, k, k, y, y, k, k, y,
    y, y, y, k, k, y, y, y,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n
  ]
  LOOK_DOWN = [
    o, y, y, y, y, y, y, o,
    o, o, n, y, y, n, o, o,
    y, k, k, y, y, k, k, y,
    y, k, w, y, y, w, k, y,
    y, y, y, k, k, y, y, y,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n
  ]
  LOOK_DOWN_RIGHT = [
    o, y, y, y, y, y, y, o,
    o, o, n, y, y, n, o, o,
    y, k, k, y, y, k, k, y,
    y, k, w, y, y, k, w, y,
    y, y, y, k, k, y, y, y,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n
  ]
  LOOK_DOWN_LEFT = [
    o, y, y, y, y, y, y, o,
    o, o, n, y, y, n, o, o,
    y, k, k, y, y, k, k, y,
    y, w, k, y, y, w, k, y,
    y, y, y, k, k, y, y, y,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n
  ]


# Chirp (bird) poses
class Chirp:
  STANDING = [
    k, k, k, l, r, y, k, k,
    k, k, k, l, l, k, k, k,
    k, k, g, w, w, g, k, k,
    k, k, g, w, w, g, k, k,
    k, k, l, w, w, l, k, k,
    k, k, l, w, w, l, k, k,
    k, k, k, l, l, k, k, k,
    k, k, o, k, k, o, k, k
  ]
  WINGS_UP = [
    k, k, k, k, k, k, k, k,
    k, k, k, l, r, y, k, k,
    k, k, k, l, l, k, k, k,
    l, g, g, w, w, g, g, l,
    k, l, g, w, w, l, g, k,
    k, k, l, w, w, l, k, k,
    k, k, k, l, l, k, k, k,
    k, k, o, k, k, o, k, k
  ]
