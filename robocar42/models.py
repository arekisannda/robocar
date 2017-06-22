
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.preprocessing.image import img_to_array, load_img
from keras.preprocessing.image import flip_axis, random_shift
from keras.utils import to_categorical

import config
from camera import Camera

def model(load, shape, tr_model=None):
    '''
    Returns a convolutional model from file or to train on.
    '''
    if load and tr_model: return load_model(tr_model)

    conv3x3_l, dense_layers = [24, 32, 40, 48], [512, 64, 16]

    model = Sequential()
    model.add(Conv2D(16, (5, 5), activation='elu', input_shape=shape))
    model.add(MaxPooling2D())
    for i in range(len(conv3x3_l)):
        model.add(Conv2D(conv3x3_l[i], (3, 3), activation='elu'))
        if i < len(conv3x3_l) - 1:
            model.add(MaxPooling2D())
    model.add(Flatten())
    for dl in dense_layers:
        model.add(Dense(dl, activation='elu'))
        model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, activation='softmax'))
    model.compile(
        loss='categorical_crossentropy',
        optimizer="adam",
        metrics=['accuracy']
    )
    return model