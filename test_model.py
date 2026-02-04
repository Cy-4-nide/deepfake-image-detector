from detector import detect_deepfake

label, confidence = detect_deepfake("test.jpg")

print(f"Prediction: {label}")
print(f"Confidence: {confidence:.2f}")
