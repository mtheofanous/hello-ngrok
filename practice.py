import streamlit as st
from PIL import Image, ImageFilter
import pillow_heif
import tempfile
import io
import os
import cv2  # OpenCV for handling video
import numpy as np

pillow_heif.register_heif_opener()

# Placeholder for watermark dimensions function
def get_watermark_dimensions(text, font_size):
    # Mock calculation for dimensions, needs to be defined properly
    return font_size * len(text) // 2, font_size

# Placeholder for applying watermark on image
def apply_watermark(img, text, font_size, opacity, x, y):
    # Watermark logic goes here
    return img

# Placeholder for extracting video frames
def get_frame(video_file):
    # Logic to extract a single frame using OpenCV
    cap = cv2.VideoCapture(video_file)
    success, frame = cap.read()
    cap.release()
    return frame if success else None

# Placeholder for rotating video frame
def rotated_frame(frame, rotation):
    # Rotate the video frame using OpenCV
    if rotation == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

# Placeholder for applying blur to frame
def blur_frame(frame, blur_strength):
    return cv2.GaussianBlur(frame, (blur_strength, blur_strength), 0)

# Placeholder for applying watermark to frame
def apply_watermark_to_frame(frame, text, font_size, opacity, x, y):
    # Convert frame to PIL for adding text
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # Apply the watermark as text
    img_pil = apply_watermark(img_pil, text, font_size, opacity, x, y)
    # Convert back to OpenCV format
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# Placeholder for processing the entire video
def rotated_video(video_file, rotation):
    # Logic to rotate full video using OpenCV
    return video_file

def blur_video(video_file, blur_strength):
    # Logic to blur full video using OpenCV
    return video_file

def apply_watermark_to_video(video_file, text, font_size, opacity, x, y):
    # Logic to apply watermark to full video
    return video_file

# Streamlit UI
st.title("Watermark Application")

# Upload image or video
uploaded_file = st.file_uploader("Upload your image or video", type=["heic", "jpeg", "jpg", "png", "gif", "mov", "mp4"])

image_type = ["heic", "jpeg", "jpg", "png", "gif"]
video_type = ["mov", "mp4", "avi"]

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension in image_type:  # Image processing
        img = Image.open(uploaded_file)
        if img.format == 'HEIC':
            img = pillow_heif.read_heif(uploaded_file)

        transform_option = st.selectbox("Rotate / Flip Image", ["Original", "Flip Horizontally", "Flip Vertically", "Rotate 90°", "Rotate 180°", "Rotate 270°"])

        if transform_option == "Flip Horizontally":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif transform_option == "Flip Vertically":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif transform_option == "Rotate 90°":
            img = img.rotate(270, expand=True)
        elif transform_option == "Rotate 180°":
            img = img.rotate(180, expand=True)
        elif transform_option == "Rotate 270°":
            img = img.rotate(90, expand=True)

        # Sidebar for further transformation
        apply_transformation = st.sidebar.selectbox("Transformation", ["Original", "Apply Blur", "Apply Watermark"])

        if apply_transformation == "Apply Blur":
            blur_radius = st.slider("Blur Radius", 50, 200, 70)
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        elif apply_transformation == "Apply Watermark":
            watermark_text = st.sidebar.text_input("Watermark Text", "linktr.ee/linas.secret")
            font_size = st.sidebar.slider("Font Size", 50, 500, round(img.size[0] * 0.07))
            opacity = st.sidebar.slider("Opacity", 0, 255, 100)

            watermark_width, watermark_height = get_watermark_dimensions(watermark_text, font_size)
            width, height = img.size
            
            with st.container():
                col1, col2 = st.columns([2, 2])  # Create two columns

            # X Position Slider
            with col1:
                x_pos = st.slider("Watermark X Position", 0, width - watermark_width, (width - watermark_width) // 2)

            # Y Position Slider
            with col2:
                y_pos = st.slider("Watermark Y Position", 0, height - watermark_height, height - font_size)

            img = apply_watermark(img, watermark_text, font_size, opacity, x_pos, y_pos)

        # Display result
        st.image(img, caption="Transformed Image", use_column_width=True)

        # Save and provide download button
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        st.download_button("Download Transformed Image", data=buf.getvalue(), file_name="transformed_image.jpg", mime="image/jpeg")

    elif file_extension in video_type:  # Video processing
         
        blur_strength = st.slider("Blur Strength:", min_value=1, max_value=301, step=2, value=101)

        if st.button("Blur Video"):
            if uploaded_file is not None:
                # Save uploaded video temporarily
                temp_input_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                with open(temp_input_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Process the video
                output_file = blur_video(temp_input_file, blur_strength)

                if output_file:
                    # Provide download link for the blurred video
                    with open(output_file, "rb") as f:
                        st.download_button("Download Blurred Video", f, file_name="blurred_video.mp4")

                    # Clean up temporary files
                    os.remove(temp_input_file)
                    os.remove(output_file)
                else:
                    st.error("Error blurring video.")
            else:
                st.error("Please upload a video file.")