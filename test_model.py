from detector import predict_image
from PIL import Image

image = Image.open("test.jpg")
label, confidence = predict_image(image)
print(f"Prediction: {label}")
print(f"Confidence: {confidence:.2%}")