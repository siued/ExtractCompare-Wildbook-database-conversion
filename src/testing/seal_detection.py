import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np

# an attempt at running the detection locally instead of relying on the wildbook detection algorithm

# Load the pre-trained ResNet50 model
model = ResNet50(weights='imagenet')

# Load and preprocess your input image
img_path = '/src/seal_image.JPG'
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = preprocess_input(x)
x = np.expand_dims(x, axis=0)

# Make predictions using the model
preds = model.predict(x)
decoded_preds = decode_predictions(preds, top=3)[0]

# Print the top predictions
for pred in decoded_preds:
    print(pred[1], pred[2])

# gives scores of what the image is, doesn't provide a bounding box
