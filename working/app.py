from flask import Flask, render_template, jsonify, send_file
import requests
import os

app = Flask(__name__)

ESP32_URL = "http://192.168.106.53/capture"  # Update this IP if needed
OUTPUT_JPEG = "static/captured.jpg"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/trigger", methods=["GET"])
def trigger():
    try:
        print("Requesting image from ESP32-CAM...")
        response = requests.get(ESP32_URL, timeout=10)

        if response.status_code == 200:
            with open(OUTPUT_JPEG, "wb") as f:
                f.write(response.content)
            print("✅ Image captured and saved.")
            return jsonify({
                "message": "Image captured successfully",
                "img_url": f"/{OUTPUT_JPEG}"
            })
        else:
            print("❌ Failed to capture image. HTTP Status:", response.status_code)
            return jsonify({"message": "Failed to capture image", "img_url": None})

    except requests.exceptions.RequestException as e:
        print("❌ Request error:", e)
        return jsonify({"message": "Request to ESP32 failed", "img_url": None})

@app.route("/static/captured.jpg")
def serve_image():
    if not os.path.exists(OUTPUT_JPEG):
        return "No image found", 404
    return send_file(OUTPUT_JPEG, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(debug=True)
