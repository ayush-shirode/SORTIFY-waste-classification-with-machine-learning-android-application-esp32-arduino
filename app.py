from flask import Flask, render_template, jsonify, send_file
import requests
import os

app = Flask(__name__)

ESP32_URL = "http://192.168.106.53/capture"  # Update this IP if needed
OUTPUT_JPEG = "static/captured.jpg"

@app.route("/")
def home():
    return render_template("index.html")

import qrcode
from flask import send_file
import io

@app.route("/api/prediction_qr")
def prediction_qr():
    try:
        with open("prediction.txt", "r") as file:
            content = file.read()

        qr_img = qrcode.make(content)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/api/trigger", methods=["GET"])
def trigger():
    try:
        print("Requesting image from ESP32-CAM...")
        response = requests.get(ESP32_URL, timeout=10)

        if response.status_code == 200:
            with open(OUTPUT_JPEG, "wb") as f:
                f.write(response.content)
            print("✅ Image captured and saved.")
            import tensorflow as tf
            from tensorflow.keras.models import load_model
            from tensorflow.keras.preprocessing.image import load_img, img_to_array
            import numpy as np

            # Paths
            model_path = "models/20250609-205224_testmodel.h5"
            image_path = "static/captured.jpg"
            output_file = "prediction.txt"

            # Load the model
            model = load_model(model_path)
            print("Model loaded")

            # Define input size of model
            IMG_SIZE = (224, 224)  # Adjust if needed

            # Load and preprocess the image
            img = load_img(image_path, target_size=IMG_SIZE)
            img_array = img_to_array(img) / 255.0  # Normalize to [0,1]
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

            # Print shape for debug
            print(f"Input image shape: {img_array.shape}")

            # Predict
            pred = model.predict(img_array)

            # Flatten prediction array to 1D for convenience
            prediction_array = pred.flatten()

            # Print raw prediction array
            print(f"Raw model prediction array: {prediction_array}")

            # Determine label based on prediction value
            threshold = 0.5
            if prediction_array[0] > threshold:
                label = "recyclable"
            else:
                label = "non-recyclable"

            # open("prediction.txt", "w").close()  # Truncates the file

            # Clean up prediction.txt
            # if os.path.exists("prediction.txt"):
            #     os.remove("prediction.txt")
            #     print("Previous prediction file deleted.")

            empty = ""
            with open(output_file, "w") as f:
                f.write(empty)            
            
            print(f"Text file empty")
            
            # Write label to file
            with open(output_file, "w") as f:
                f.write(label)

            print(f"Prediction label written to {output_file}: {label}")

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
