import streamlit as st
from detector import predict_image
from PIL import Image

st.set_page_config(
    page_title="Deepfake Image Detector",
    page_icon="🕵️",
    layout="centered"
)

# Header
st.title("🕵️ Deepfake Image Detector")
st.caption("Upload an image to check whether it is Real or AI-Generated (Fake)")
st.divider()

# Upload section
uploaded_file = st.file_uploader(
    "Upload a face image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    # Show uploaded image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, caption="Uploaded Image", use_column_width=True)
    
    st.divider()
    
    # Analyze button
    if st.button("🔍 Analyze Image", use_container_width=True):
        with st.spinner("Analyzing image... please wait"):
            label, confidence = predict_image(image)
        
        st.divider()
        
        # Result display
        if confidence < 0.70:
            # Uncertain
            st.warning("⚠️ Result: **Uncertain**")
            st.write("The model is not confident enough to make a clear decision.")
        
        elif "real" in label.lower():
            # Real
            st.success("✅ Result: **REAL IMAGE**")
            st.write("This image appears to be a genuine, real photograph.")
        
        else:
            # Fake
            st.error("🚨 Result: **FAKE / AI-GENERATED IMAGE**")
            st.write("This image appears to be artificially generated or manipulated.")
        
        # Confidence meter
        st.subheader("Confidence Score")
        st.progress(confidence)
        st.write(f"**{confidence:.1%}** confidence in this prediction")
        
        # Explanation
        st.divider()
        st.subheader("📊 What does this mean?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Prediction",
                value=label
            )
        with col2:
            st.metric(
                label="Confidence",
                value=f"{confidence:.1%}"
            )
        with col3:
            if confidence >= 0.90:
                certainty = "Very High"
            elif confidence >= 0.70:
                certainty = "Moderate"
            else:
                certainty = "Low"
            st.metric(
                label="Certainty",
                value=certainty
            )
        
        st.divider()
        st.warning("⚠️ Note: No AI detector is 100% accurate. Always use human judgment alongside AI predictions.")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About This Tool")
    st.write("""
    This tool uses a **Vision Transformer (ViT)** 
    deep learning model to detect whether an 
    image is real or AI-generated.
    """)
    
    st.divider()
    
    st.subheader("🎯 How to use")
    st.write("""
    1. Upload a face image
    2. Click Analyze
    3. View the result and confidence score
    """)
    
    st.divider()
    
    st.subheader("📈 Confidence Guide")
    st.write("""
    - **90%+** → Very reliable result
    - **70-90%** → Moderately reliable  
    - **Below 70%** → Uncertain result
    """)
    
    st.divider()
    st.caption("Built with PyTorch + Hugging Face + Streamlit")
