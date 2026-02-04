import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

model_name = "dima806/deepfake_vs_real_image_detection"

processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

image = Image.open("test.jpg").convert("RGB")

inputs = processor(images=image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits
predicted_class = logits.argmax(-1).item()

label = model.config.id2label[predicted_class]
confidence = torch.softmax(logits, dim=1)[0][predicted_class].item()

print(f"Prediction: {label}")
print(f"Confidence: {confidence:.2f}")
