import streamlit as st
from detector import detect_deepfake
from PIL import Image
import tempfile

st.set_page_config(page_title="Deepfake Image Detector", layout="centered")

st.title("🕵️ Deepfake Image Detection")
st.write("Upload an image to check whether it is **Real** or **Fake**.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_image_path = tmp.name

    if st.button("Analyze Image"):
        with st.spinner("Analyzing..."):
            label, confidence = detect_deepfake(temp_image_path)

        st.success(f"Prediction: **{label}**")
        st.info(f"Confidence: **{confidence:.2f}**")
