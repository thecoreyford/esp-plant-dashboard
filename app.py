from flask import Flask, request, jsonify, render_template, Response
from pymongo import MongoClient
from datetime import datetime
from io import StringIO
import os
import csv

app = Flask(__name__)

# MongoDB URI
MONGO_URI = os.environ.get('MONGO_URI') or "mongodb+srv://student:austral-clash-sawyer-blaze@espplantcluster.3yopiy3.mongodb.net/?retryWrites=true&w=majority&appName=ESPPlantCluster"
client = MongoClient(MONGO_URI)
db = client['esp_data']
collection = db['sensor_readings']

@app.route('/')
def home():
    return "ESP32 + MongoDB API is running!"

@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.get_json()
    if not data or 'temperature' not in data:
        return jsonify({'error': 'Missing data'}), 400
    data['timestamp'] = datetime.utcnow()
    collection.insert_one(data)
    return jsonify({'message': 'Data saved'}), 200

@app.route('/data')
def get_data():
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/download')
def download_csv():
    data = list(collection.find({}, {'_id': 0}))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['temperature', 'timestamp'])
    for entry in data:
        writer.writerow([entry['temperature'], entry['timestamp']])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=sensor_data.csv'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
