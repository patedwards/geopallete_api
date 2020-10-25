import json
from flask import Flask, request, jsonify, make_response, current_app
from datetime import timedelta
from functools import update_wrapper
import os
from numpy import round
from sklearn.cluster import KMeans
import numpy as np
from matplotlib.colors import rgb_to_hsv
from PIL import Image  
from io import BytesIO
from get_map import get_map_by_bbox
import logging

from flask_cors import CORS, cross_origin

app = Flask(__name__)

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
    im = get_map_by_bbox(data['bBoxes'][0])
    im_array = np.array(im)/255
    w, h, d = im_array.shape
    pixels = im_array.reshape((w*h, d))
    N = w*h

    n_clusters = 10

    centroids = KMeans(n_clusters=n_clusters).fit_predict(pixels)

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


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/api/create_pallete", methods=["POST", "OPTIONS"])
def geopallete():
    if request.method == "OPTIONS": # CORS preflight
        response = _build_cors_prelight_response()
        logging.info("OPTIONS", response.headers)
        import pdb; pdb.set_trace()
        return response
    elif request.method == "POST": # The actual request following the preflight
        data = json.loads(request.data)
        print(data['bBoxes'])
        frequencies, colors = analyse_response_data(data)
        response = jsonify({"colors": list(map(rgb2hex, colors))})
        logging.info("POST",response)
        import pdb; pdb.set_trace()
        return _corsify_actual_response(response.headers)
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))
    

    
if __name__ == "__main__":
    app.run(port=80)