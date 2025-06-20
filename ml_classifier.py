import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Paths
model_path = "/mnt/e/ASEP2/waste_classifier/models/20250609-205224_testmodel.h5"
image_path = "stone_70.jpg"
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

# Write label to file
with open(output_file, "w") as f:
    f.write("null")
    f.write(label)

print(f"Prediction label written to {output_file}: {label}")
