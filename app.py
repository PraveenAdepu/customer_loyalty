from __future__ import division, print_function
# coding=utf-8
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import yaml as yaml
import pickle

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

print("Processing : Loading configuration file")
config = yaml.safe_load(open(
    r"C:\Users\adepup\Documents\Prav-Development\Research\github\customer_loyalty\config\config.yaml"))
n_clusters = config['parameters']['n_clusters']


# Define a flask app
app = Flask(__name__)

kmeans_model_path = config['parameters']['kmeans_model_path']

with open(kmeans_model_path, 'rb') as handle:
    kmeans_cal = pickle.load(handle)   

print('Model loaded. Check http://127.0.0.1:5000/')

def model_predict(frequency, kmeans_cal):
    cluster = kmeans_cal.predict((pd.DataFrame({'frequency_cal':[frequency]})))[0]
    if cluster == 0:
        customer = "cluster {} : Non Loyal Customer".format(cluster)
    else:
        customer = "cluster {} : Loyal Customer".format(cluster)
    return customer

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        frequency = request.form['text']

        # Make prediction
        result = model_predict(frequency, kmeans_cal)
        
        return result
    return None

if __name__ == '__main__':
    app.run(debug=True)
