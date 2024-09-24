import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pillow_heif
import io
from functions import apply_watermark, get_watermark_dimensions

# Register HEIF opener
pillow_heif.register_heif_opener()

st.title("Watermark Application")


# Upload image
uploaded_file = st.file_uploader("Upload your HEIC image", type=["heic", "jpeg", "jpg", "png", "gif"])

if uploaded_file:
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

        # Convert uploaded file to JPEG in memory
        # img = img.convert("RGBA")
        
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
        
            # Apply Gaussian blur if selected
        # if apply_blur == "Apply Gaussian Blur":
        #     img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        # elif apply_blur == "Apply Watermark":
        #     img = apply_watermark(img, watermark_text, font_size, opacity, x_pos, y_pos)
    
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
