import json
from flask import Flask, request, jsonify, make_response
import os
from numpy import round
from sklearn.cluster import KMeans
import numpy as np
from matplotlib.colors import rgb_to_hsv
from PIL import Image  
from io import BytesIO
from flask_cors import CORS
import time

from get_map import get_map_by_bbox

app = Flask(__name__)
CORS(app)

def get_image(data, with_features=False):
    response = service.image(
        'mapbox.satellite', 
        lon=data['deckViewState']['longitude'], 
        lat=data['deckViewState']['latitude'], 
        z=data['deckViewState']['zoom'],
        width=1280,
        height=1280,
        features= data['featureCollection'] if with_features else []
    )
    return response

def process_viewports(viewPorts):
    viewPort = viewPorts[0]
    response = service.image(
        'mapbox.satellite', 
        lon=viewPort['longitude'], 
        lat=viewPort['latitude'], 
        z=viewPort['zoom'],
        width=viewPort['width'],
        height=viewPort['height'],
    )
    return response
    
def rgb2hex(color):
    # https://stackoverflow.com/questions/3380726/converting-a-rgb-color-tuple-to-a-six-digit-code-in-python
    return f"#{''.join(f'{hex(int(round(c*255)))[2:].upper():0>2}' for c in color)}"
    
def analyse_response_data(data):
    t0 = time.time()
    im = get_map_by_bbox(data['bBoxes'][0])
    w, h = [im.width, im.height]
    im = im.resize((int(np.floor(w/10)), int(np.floor(h/10))))
    im_array = np.array(im)/255
    w, h, d = im_array.shape
    pixels = im_array.reshape((w*h, d))
    N = w*h

    n_clusters = int(data['k'])

    
    print(len(pixels))
    centroids = KMeans(n_clusters=n_clusters).fit_predict(pixels)
    t1 = time.time(); print("After fitting", t1-t0)

    colors = []
    frequencies = []
    for i in range(n_clusters):
        colors.append((
            np.mean(pixels[(centroids == i)][:,0]), 
            np.mean(pixels[(centroids == i)][:,1]),
            np.mean(pixels[(centroids == i)][:,2])
        ))
        frequencies.append(len(pixels[(centroids == i)])/N)
    return frequencies, colors

    
@app.route('/palettemap', methods=['GET', 'POST', 'OPTIONS'])
def palettemap():
    if request.method != "POST":
        return make_response()
    data = json.loads(request.data)
    print(data)
    t0 = time.time()
    frequencies, colors = analyse_response_data(data)
    t1 = time.time()
    print("Took", t1-t0)
    return jsonify({"colors": list(map(rgb2hex, colors))})

    
if __name__ == "__main__":
    app.run()
