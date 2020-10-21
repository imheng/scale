import io
import socket
import struct
from PIL import Image
import requests
import base64
import json


client_socket = socket.socket()
client_socket.connect(('192.168.2.218', 8000)) #connect pi zero
connection = client_socket.makefile('rb')
print(' * connected...')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        print(' * image_len: ', image_len)
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        img = image.resize((224, 224))

        print(' * image received ...')

finally:
    stream_data = image_stream.getvalue()
    # res = base64.b64encode(stream_data)
    # print(res)
    headers = {'Content-Type': 'application/json'}
    d = {'image': base64.b64encode(stream_data)}
    r = requests.post("http://192.168.2.168:5000/predict", json=d)
    print(' * request :',r)
    print(' * post done ...')
    connection.close()
    client_socket.close()
