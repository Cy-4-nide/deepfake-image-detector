import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_NAME = "dima806/deepfake_vs_real_image_detection"

processor = None
model = None


def load_model():
    global processor, model
    if processor is None or model is None:
        processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
        model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)


def detect_deepfake(image_path: str):
    load_model()

    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_class = logits.argmax(-1).item()

    label = model.config.id2label[predicted_class]
    confidence = torch.softmax(logits, dim=1)[0][predicted_class].item()

    return label, confidence
