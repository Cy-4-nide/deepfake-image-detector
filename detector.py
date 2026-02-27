import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_NAME = "Wvolf/ViT_Deepfake_Detection"

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
model.eval()

print("LABEL MAP:", model.config.id2label)

def predict_image(image: Image.Image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    print("ALL PROBS:", probs)

    pred_id = torch.argmax(probs, dim=1).item()
    confidence = probs[0][pred_id].item()
    label = model.config.id2label[pred_id]

    return label, confidence