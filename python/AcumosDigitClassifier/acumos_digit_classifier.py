# -*- coding: utf-8 -*-
# ===============LICENSE_START=======================================================
# Acumos Apache-2.0
# ===================================================================================
# Copyright (C) 2017-2019 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by AT&T and Tech Mahindra
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# 
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================
"""
Acumos implementation of Tensorflow tutorial model for classification of handwritten digits
trained on MNIST dataset.

First part (before Acumos stuff) copied from https://www.tensorflow.org/tutorials,
slightly edited to use keras directly rather than tensorflow.

Microservice accepts an arbitrary binary object as input, which it interprets as an image,
and returns the predicted digit.
"""

import keras
mnist = keras.datasets.mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = keras.models.Sequential([
  keras.layers.Flatten(input_shape=(28, 28)),
  keras.layers.Dense(512, activation='relu'),
  keras.layers.Dropout(0.2),
  keras.layers.Dense(10, activation='softmax')
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5)
model.evaluate(x_test, y_test)

#
# Now add Acumos stuff
#

# Our model accepts a binary image file as input, reformats it into a numpy array to be classified,
# and then predicts the class

from acumos.modeling import Model
from acumos.session import AcumosSession
from acumos.metadata import Requirements
from PIL import Image
import numpy as np
import io


# Reformat an arbitrary binary object containing an image into a 28 x 28 numpy array of real numbers between 0 and 1
def reformat_image(imdata):
    buffer = io.BytesIO(imdata)
    img = Image.open(buffer).convert('L').resize((28, 28), resample=Image.BICUBIC)
    return 1.0 - np.array(img) / 255.0        # Map white (255) to 0.0 and black (0) to 1.0


# Predictor function for Acumos
def classify(imdata: bytes) -> int:
    x = reformat_image(imdata)
    return model.predict_classes(np.expand_dims(x, axis=0))[0]


reqs = Requirements(req_map={'PIL': 'pillow'})   # Needed because PIL is installed as pillow, alas

# Dump model on desktop with endpoint predict bound to classify() function
AcumosSession().dump(Model(predict=classify), 'DigitClassifier', '~/Desktop', reqs)
