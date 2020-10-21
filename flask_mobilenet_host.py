import numpy as np
import keras
from keras.models import Sequential, Model
from keras.layers import Dropout
from keras.layers.core import Dense, Flatten
from keras.preprocessing import image as keras_image
from keras.applications.mobilenetv2 import preprocess_input

import subprocess

import base64
import io
from PIL import Image
from flask import request,jsonify,Flask

app=Flask(__name__)
print(' * TRY 1 ...')
def get_model():
    global model
    base_model = keras.applications.mobilenetv2.MobileNetV2(input_shape=(224, 224, 3), include_top=False,
                                                            weights='imagenet')
    top_model = Sequential()
    top_model.add(Flatten(input_shape=base_model.output_shape[1:]))
    top_model.add(Dense(256, activation='relu'))
    top_model.add(Dropout(0.5))
    top_model.add(Dense(9, activation='softmax'))
    model = Model(inputs=base_model.input, outputs=top_model(base_model.output))
    model.load_weights('temp4wizbase.h5')
    print(" * Model loaded!")


def preprocess_image(image,target_size):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image = keras_image.img_to_array(image)
    # print(image)
    # print('shape of image: ', np.shape(image))
    image = np.expand_dims(image,axis=0)
    image = preprocess_input(image)
    return image

print(" * Loading Keras model...")
get_model()

@app.route("/predict",methods=["POST"])

# def predict():
#     message = request.get_json(force=True)
#     encoded = message['image']
#     print(' * image length: ', len(encoded))
#     decoded = base64.b64decode(encoded)
#     image = Image.open(io.BytesIO(decoded))
#     processed_image = preprocess_image(image,target_size=(224,224))
#
#     prediction = model.predict(processed_image)
#     print(prediction)
#     print(prediction.tolist())
#     response = {
#         'prediction': prediction.tolist()
#     }
#     return jsonify(response)

def predict():
    print('xxx')
    message = request.get_json(force=True)
    encoded = message['image']
    # print(encoded)
    decoded = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(decoded))
    processed_image = preprocess_image(image,target_size=(224,224))
    prediction = model.predict(processed_image)
    # prediction=[[0.40749478340148926, 0.006855021230876446, 0.3607226014137268, 0.009623372927308083, 0.13762150704860687, 0.000964827137067914, 0.05141974985599518, 0.013240553438663483, 0.012057550251483917]]
    p = prediction
    # print('Prediction: ',prediction)
    classes = ['apple','bean','cabbage','carrot','cauliflower','cucumber','eggplant','mashroom','pitaya']
    predict_result = classes[np.argmax(prediction)]
    print('Predict result: ', predict_result)
    predict_result = 'sounds/' + predict_result + '.mp3'
    print(predict_result)
    subprocess.call(["omxplayer", predict_result,"-o","local"])
    response = {
        'prediction': {
            'possibily': predict_result,
            'apple': p[0][0].tolist(),
            'bean': p[0][1].tolist(),
            'cabbage': p[0][2].tolist(),
            'carrot': p[0][3].tolist(),
            'cauliflower': p[0][4].tolist(),
            'cucumber': p[0][5].tolist(),
            'eggplant': p[0][6].tolist(),
            'mashroom': p[0][7].tolist(),
            'pitaya': p[0][8].tolist()
        }
    }
    print(response)
    return jsonify(response)