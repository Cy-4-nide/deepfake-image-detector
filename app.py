import streamlit as st
st.set_page_config(page_title="Deepfake Image Detector", layout="centered")

from detector import detect_deepfake
from PIL import Image
import tempfile

st.title("🕵️ AI-Powered Deepfake Image Detector")
st.caption("Upload an image to check whether it is real or fake.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_image_path = tmp.name

    if st.button("Analyze Image"):
        with st.spinner("Analyzing..."):
            label, confidence = detect_deepfake(temp_image_path)

        st.success(f"Prediction: {label}")
        st.info(f"Confidence: {confidence:.2f}")
        st.warning("Note: AI predictions may not be 100% accurate.")
