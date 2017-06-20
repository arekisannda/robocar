
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.preprocessing.image import img_to_array, load_img
from keras.preprocessing.image import flip_axis, random_shift
from keras.utils import to_categorical

from google.cloud import bigquery

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

if __name__ == '__main__':
    bigquery_client = bigquery.Client()

    dataset_name = 'test_set'
    dataset = bigquery_client.dataset(dataset_name)

    if not dataset.exists():
        print('Data {} does not exist.'.format(dataset_name))
        exit(0)

    table = dataset.table('test_table')

    right = load_img('right.bmp', target_size=(320,240))
    left = load_img('left.bmp', target_size=(320,240))
    import base64
    import cStringIO

    buffer = cStringIO.StringIO()
    right.save(buffer, format="BMP")
    rt_img_str = base64.b64encode(buffer.getvalue())
    left.save(buffer, format="BMP")
    lf_img_str = base64.b64encode(buffer.getvalue())
    info = (
        'test',
        0,
        rt_img_str,
        lf_img_str,
        0,
        'hello'
    )
    table.reload()
    error = table.insert_data([info])
    if error:
        print("error")