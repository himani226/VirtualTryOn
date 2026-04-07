import streamlit as st
import io
from PIL import Image

# --- WORKAROUND FOR NAMESPACE ERROR ---
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("🚨 Critical Error: The 'google-genai' package is not installed correctly on the server.")
    st.info("To fix this: Ensure 'google-genai' is in your requirements.txt and REBOOT your Streamlit app.")
    st.stop()

# Page Config
st.set_page_config(page_title="AI Virtual Try-On", layout="wide")

# --- API KEY CONFIG ---
# This pulls from the Secrets you set in the Streamlit Dashboard
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("🔑 API Key Missing! Please add 'GEMINI_API_KEY' to your Streamlit Cloud Secrets.")
    st.stop()

st.title("👕 AI Virtual Try-On")
st.subheader("Upload a photo of yourself and the clothes you want to try!")

# Create two columns for uploading
col1, col2 = st.columns(2)

with col1:
    user_img_file = st.file_uploader("Step 1: Upload Your Photo", type=['jpg', 'jpeg', 'png'], key="user")
    if user_img_file:
        st.image(user_img_file, caption="User Photo", width=300)

with col2:
    cloth_img_file = st.file_uploader("Step 2: Upload Clothing Photo", type=['jpg', 'jpeg', 'png'], key="cloth")
    if cloth_img_file:
        st.image(cloth_img_file, caption="Clothing Photo", width=300)

# Process Button
if st.button("Generate Try-On 🚀"):
    if not user_img_file or not cloth_img_file:
        st.error("Please upload both images first.")
    else:
        try:
            with st.spinner("Stitching your outfit... this takes about 10-20 seconds."):
                # Convert uploaded files to PIL Images
                user_img = Image.open(user_img_file)
                cloth_img = Image.open(cloth_img_file)

                # Send to Gemini 2.5 Flash Image
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[
                        "This is a person, and this is a piece of clothing. Generate a realistic image of the person wearing this exact clothing. Maintain the person's identity, face, and pose.",
                        user_img, 
                        cloth_img
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                    ),
                )

                # Find the image in the response
                generated_image = None
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            generated_image = Image.open(io.BytesIO(part.inline_data.data))
                
                if generated_image:
                    st.divider()
                    st.success("Here is your look!")
                    st.image(generated_image, caption="Virtual Try-On Result", use_container_width=True)
                    
                    # Download Button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")
                    st.download_button("Download Image", buf.getvalue(), "try_on_result.png", "image/png")
                else:
                    st.warning("The AI didn't return an image. It might have been blocked by safety filters or prompt issues.")

        except Exception as e:
            st.error(f"An error occurred: {e}")