import streamlit as st
import pillow_heif
import numpy as np
import cv2
from io import BytesIO
from functions_1 import apply_rotate, get_watermark_dimensions, apply_watermark, apply_blur
from PIL import Image, ImageDraw, ImageFont
import math

def main():
    pillow_heif.register_heif_opener()

    st.title("Image Edit App")
    st.write("Welcome to the Image Edit App!")

    uploaded_file = st.file_uploader("Upload your image", type=["heic", "jpeg", "jpg", "png", "gif"])

    image_type = ["heic", "jpeg", "jpg", "png", "gif"]

    if uploaded_file:
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension in image_type:  # One of the image types
            # Open the uploaded image
            img = Image.open(uploaded_file)
            original_img = img.copy()
            original_width, original_height = original_img.size
            original_longest_side = max(original_width, original_height)# Keep the original for transformations on download
            
            # Convert HEIC to RGB if necessary
            if img.format == 'heic':
                img = pillow_heif.read_heif(uploaded_file)
        
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Create a temporary low-resolution preview
            preview_img = img.copy()
            preview_img.thumbnail((600, 600))  # Resize for faster preview
            # Get the dimensions of the thumbnail image
            thumbnail_width, thumbnail_height = preview_img.size
            thumbnail_longest_side = max(thumbnail_width, thumbnail_height)
            
            # Calculate how many times smaller the thumbnail is
            scaling_factor = math.ceil(original_longest_side / thumbnail_longest_side)
            st.write(f"Scaling factor: {scaling_factor}")
            
            img_np = np.array(preview_img)  # Convert preview to a numpy array for OpenCV

            # Rotation selection
            rotation_option = st.selectbox("Rotation", ["Original", "90", "180", "270"])
            
            img_np = apply_rotate(img_np, rotation_option)
            transformed_preview = img_np

            # Apply transformation to preview
            apply_transformation = st.sidebar.selectbox("Transformation", ("Rotation", "Apply Blur", "Apply Watermark"))
            
            if apply_transformation == "Apply Blur":
                blur_strength = st.slider("Blur Strength", 31, 301, step=12, value=181)
                blur_strength_original = round(blur_strength * scaling_factor)
                if blur_strength_original % 2 == 0:
                    blur_strength_original += 1 # Scale blur strength to original image size
                size = st.slider("Size", 1.0, 8.0, step=0.25, value=1.0)
                
                # Apply transformations to the preview image
                transformed_preview = apply_blur(img_np, size, blur_strength)
                
            elif apply_transformation == "Apply Watermark":
                watermark_text = st.sidebar.text_input("Watermark Text", "linktr.ee/linas.secret")
                font_size = st.sidebar.slider("Font Size", 20, 500, round(img_np.shape[1] * 0.07)) # Scale font size to image width
                opacity = st.sidebar.slider("Opacity", 0, 255, 100)

                watermark_width, watermark_height = get_watermark_dimensions(watermark_text, font_size)
                width, height = img_np.shape[1], img_np.shape[0]
                
                with st.container():
                    col1, col2 = st.columns([2, 2])  # Create two columns

                # X Position Slider
                with col1:
                    x_pos = st.slider("Watermark X Position", 0, width - watermark_width, (width - watermark_width) // 2)

                # Y Position Slider
                with col2:
                    y_pos = st.slider("Watermark Y Position", 0, height - watermark_height, height - font_size)

            # Apply transformations to the preview image
                transformed_preview = apply_watermark(img_np, watermark_text, font_size, opacity, x_pos, y_pos)
            st.image(transformed_preview)

            # Download button for the original high-quality image as JPEG
            st.write("When you're ready, download the original high-quality image as JPEG:")
            download_button = st.button("Download Original as JPG")
            if download_button:
                # Convert the original image to a numpy array for OpenCV transformations
                original_img_np = np.array(original_img)
                
                # Apply the same transformations to the original high-quality image
                if apply_transformation == "Rotation":
                    original_img_np = apply_rotate(original_img_np, rotation_option)
                elif apply_transformation == "Apply Blur":
                    original_img_np = apply_blur(original_img_np, size, blur_strength_original)
                elif apply_transformation == "Apply Watermark":
                    
                    original_width, original_height = original_img_np.shape[1], original_img_np.shape[0]
                    
                    # Calculate relative positions for the original image based on preview dimensions
                    relative_x_pos = x_pos / width
                    relative_y_pos = y_pos / height
                    
                            # Convert relative positions back to original image dimensions
                    x_pos_original = int(relative_x_pos * original_width)
                    y_pos_original = int(relative_y_pos * original_height)
        

                    original_img_np = apply_watermark(original_img_np, watermark_text, font_size * scaling_factor, opacity , x_pos_original, y_pos_original)

                # Convert the transformed original image back to PIL format for saving as JPG
                transformed_original_pil = Image.fromarray(original_img_np)
                img_buffer = BytesIO()
                transformed_original_pil = transformed_original_pil.convert("RGB")  # Ensure it's in RGB mode for JPEG format
                transformed_original_pil.save(img_buffer, format="JPEG")
                img_buffer.seek(0)  # Reset buffer pointer

                # Create download button for the converted JPEG
                st.download_button(
                    label="Download JPG",
                    data=img_buffer,
                    file_name="downloaded_image.jpg",
                    mime="image/jpeg"
                )
    else:
        st.write("Upload an image to get started.")

if __name__ == '__main__':
    main()


