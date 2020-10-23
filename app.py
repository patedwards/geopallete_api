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

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of basestring if using Python 3.x
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of basestring if using Python 3.x
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


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

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/',  methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def geopallete():
    print("Method = ", request.method, "!")
    data = json.loads(request.data)
    print(data['bBoxes'])
    frequencies, colors = analyse_response_data(data)
    
    response = jsonify({"colors": list(map(rgb2hex, colors))})
    return response

    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)