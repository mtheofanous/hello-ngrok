import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pillow_heif
import io
import tempfile
import os
import cv2
from functions import apply_watermark, get_watermark_dimensions
import subprocess


# Register HEIF opener
def main():
    pillow_heif.register_heif_opener()

    st.title("Watermark Application")

    # Upload image
    uploaded_file = st.file_uploader("Upload your image or video", type=["heic", "jpeg", "jpg", "png", "gif", "mov", "mp4"])

    image_type = ["heic", "jpeg", "jpg", "png", "gif"]
    video_type = ["mov", "mp4", "avi"]

    if uploaded_file:

        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension in image_type: # one of the image type

            # Open and display the uploaded image
            img = Image.open(uploaded_file)
            if img.format == 'HEIC':
                img = pillow_heif.read_heif(uploaded_file)

            transform_option = st.selectbox(
                "Rotate / Flip Image",
                ("Original", "Flip Horizontally", "Flip Vertically", "Rotate 90°", "Rotate 180°", "Rotate 270°")
            )

            # Perform the transformation based on the user's choice
            if transform_option == "Flip Horizontally":
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif transform_option == "Flip Vertically":
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif transform_option == "Rotate 90°":
                img = img.rotate(270, expand=True)  # PIL uses counterclockwise rotation
            elif transform_option == "Rotate 180°":
                img = img.rotate(180, expand=True)
            elif transform_option == "Rotate 270°":
                img = img.rotate(90, expand=True)
                
            apply_transformation = st.sidebar.selectbox("Transformation",("Original","Apply Blur","Apply Watermark"))

            if apply_transformation == "Apply Blur":
                blur_radius = st.slider("Blur Radius", 50, 200, 70)
                img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                
            elif apply_transformation == "Apply Watermark":

                # Get image dimensions
                width, height = img.size

                # Input fields for watermark settings
                watermark_text = st.sidebar.text_input("Watermark Text", "linktr.ee/linas.secret")
                font_size = st.sidebar.slider("Font Size", 50, 500, round(width * 0.07))
                opacity = st.sidebar.slider("Opacity", 0, 255, 100)
                
                watermark_width, watermark_height = get_watermark_dimensions(watermark_text, font_size)
                
                with st.container():
                    col1, col2 = st.columns([2, 2])  # Create two columns

                    # X Position Slider
                    with col1:
                        x_pos = st.slider("Watermark X Position", 0, width - watermark_width, (width - watermark_width) // 2)

                    # Y Position Slider
                    with col2:
                        y_pos = st.slider("Watermark Y Position", 0, height - watermark_height, height - font_size)
                        
                img = apply_watermark(img, watermark_text, font_size, opacity, x_pos, y_pos)
                

            # Display the result
            st.image(img, caption="Transformed Image", use_column_width=True)

            # Save the result
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            st.download_button(
                label="Download Transformed Image",
                data=buf.getvalue(),
                file_name="transformed_image.jpg",
                mime="image/jpeg"
                )


        if file_extension in video_type:
        #     # Open and display the uploaded video
            if uploaded_file is not None:
                # Save the uploaded video to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                    temp_file.write(uploaded_file.read())
                    temp_file_path = temp_file.name
                    
                # Open the video file
                video = cv2.VideoCapture(temp_file_path)
                fps = video.get(cv2.CAP_PROP_FPS)
                width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                
                
                blur_option = st.selectbox("Apply Blur",("No","Yes"))
                if blur_option == "Yes":
                    blur_radius = st.slider("Blur Radius", 51, 301, 101)
                    st.write("Applying blur to the video...")
                    # Create a temporary directory to store the frames
                    with tempfile.TemporaryDirectory() as temp_dir:
                        frame_paths = []
                        for i in range(total_frames):
                            success, frame = video.read()
                            if not success:
                                break
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(frame)
                            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.jpg")
                            img.save(frame_path)
                            frame_paths.append(frame_path)
                            
                        # Create a video from the blurred frames
                        blurred_video_path = os.path.join(temp_dir, "blurred_video.mp4")
                        subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(temp_dir, "frame_%04d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p", blurred_video_path])
                        
                        # Display the blurred video
                        st.video(blurred_video_path)
                        
                        # Download the blurred video
                        st.download_button(
                            label="Download Blurred Video",
                            data=open(blurred_video_path, "rb").read(),
                            file_name="blurred_video.mp4",
                            mime="video/mp4"
                        )
                        
                else:
                    st.video(temp_file_path)
                    st.download_button(
                        label="Download Video",
                        data=open(temp_file_path, "rb").read(),
                        file_name="uploaded_video.mp4",
                        mime="video/mp4"
                    )
                    
                     
if __name__ == "__main__":
    main()