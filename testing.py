import streamlit as st
from PIL import Image
import pillow_heif
import numpy as np
import cv2
from io import BytesIO
from functions_1 import apply_transformations



def main():
    pillow_heif.register_heif_opener()

    st.title("Image App")
    st.write("Welcome to the Image App!")

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
            scaling_factor = round(original_longest_side // thumbnail_longest_side)
            st.write(f"Scaling factor: {scaling_factor}")
            
            img_np = np.array(preview_img)  # Convert preview to a numpy array for OpenCV

            # Rotation selection
            rotation_option = st.selectbox("Rotation", ["Original", "90", "180", "270"])

            # Apply transformation to preview
            apply_transformation = st.sidebar.selectbox("Transformation", ("Original", "Apply Blur", "Watermark"))
            if apply_transformation == "Apply Blur":
                blur_strength = st.slider("Blur Strength", 31, 301, step=12, value=181)
                blur_strength_original = round(blur_strength * scaling_factor)
                if blur_strength_original % 2 == 0:
                    blur_strength_original += 1 # Scale blur strength to original image size
                size = st.slider("Size", 1.0, 8.0, step=0.25, value=4.0)
            else:
                blur_strength = size = None
                
            

            # Apply transformations to the preview image
            transformed_preview = apply_transformations(img_np, rotation_option, apply_transformation, blur_strength, size)
            st.image(transformed_preview)

            # Download button for the original high-quality image as JPEG
            st.write("When you're ready, download the original high-quality image as JPEG:")
            download_button = st.button("Download Original as JPG")
            if download_button:
                # Convert the original image to a numpy array for OpenCV transformations
                original_img_np = np.array(original_img)
                
                # Apply the same transformations to the original high-quality image
                transformed_original = apply_transformations(original_img_np, rotation_option, apply_transformation, blur_strength_original, size)

                # Convert the transformed original image back to PIL format for saving as JPG
                transformed_original_pil = Image.fromarray(transformed_original)
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


