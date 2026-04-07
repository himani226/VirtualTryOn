import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# Page Config
st.set_page_config(page_title="AI Virtual Try-On", layout="wide")
st.title("👕 AI Virtual Try-On")
st.subheader("Upload a photo of yourself and the clothes you want to try!")

# Sidebar for API Key
with st.sidebar:
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your free key from [Google AI Studio](https://aistudio.google.com)")

# Create two columns for uploading
col1, col2 = st.columns(2)

with col1:
    user_img_file = st.file_uploader("Step 1: Upload Your Photo", type=['jpg', 'jpeg', 'png'])
    if user_img_file:
        st.image(user_img_file, caption="User Photo", width=300)

with col2:
    cloth_img_file = st.file_uploader("Step 2: Upload Clothing Photo", type=['jpg', 'jpeg', 'png'])
    if cloth_img_file:
        st.image(cloth_img_file, caption="Clothing Photo", width=300)

# Process Button
if st.button("Generate Try-On 🚀"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
    elif not user_img_file or not cloth_img_file:
        st.error("Please upload both images first.")
    else:
        try:
            with st.spinner("Stitching your outfit... this takes about 10-20 seconds."):
                client = genai.Client(api_key=api_key)
                
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
                    st.warning("The AI didn't return an image. It might have been blocked by safety filters.")

        except Exception as e:
            st.error(f"An error occurred: {e}")