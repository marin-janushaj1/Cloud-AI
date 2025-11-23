from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
model_bundle = joblib.load('data/clean/best_model.pkl')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'model': model_bundle['model_name']})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    result = predict_price(**data)  # Use function from above
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
