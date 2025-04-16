from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
import io
import csv

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get('MONGO_URI') or "mongodb+srv://student:austral-clash-sawyer-blaze@espplantcluster.3yopiy3.mongodb.net/?retryWrites=true&w=majority&appName=ESPPlantCluster"
client = MongoClient(MONGO_URI)
db = client["esp_data"]
collection = db["moisture_readings"]

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/upload", methods=["POST"])
def upload_data():
    data = request.get_json()
    if not data or "avgMoisture" not in data or "deviceID" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    now = datetime.utcnow()
    data["timestamp"] = now
    data["date"] = now.strftime("%Y-%m-%d")

    collection.insert_one(data)
    return jsonify({"message": "Data stored successfully"}), 200

@app.route("/data", methods=["GET"])
def get_data():
    device_id = request.args.get("deviceID")
    query = {"deviceID": device_id} if device_id else {}
    data = list(collection.find(query, {"_id": 0}))
    return jsonify(data), 200

@app.route("/download", methods=["GET"])
def download_csv():
    device_id = request.args.get("deviceID")
    query = {"deviceID": device_id} if device_id else {}
    data = list(collection.find(query, {"_id": 0}))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["deviceID", "avgMoisture", "timestamp", "date"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv", as_attachment=True, download_name="moisture_data.csv")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
