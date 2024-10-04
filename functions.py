import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pillow_heif
import io
import numpy as np
import tempfile
import cv2
import os
import subprocess
import time
from moviepy.editor import VideoFileClip, vfx


def apply_watermark(image, watermark_text, font_size, opacity, x_pos, y_pos):
    img = image.convert("RGBA")
    
    draw = ImageDraw.Draw(img)

    # Define the watermark
    watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark)

    # Load font
    font = ImageFont.truetype("arial.ttf", font_size)

    # Add text to the watermark
    watermark_draw.text((x_pos, y_pos), watermark_text, font=font, fill=(255, 255, 255, opacity))

    # Combine the original image with the watermark
    watermarked_image = Image.alpha_composite(img, watermark)
    
    # Convert back to 'RGB'
    watermarked_image = watermarked_image.convert("RGB")

    return watermarked_image

def get_watermark_dimensions(watermark_text, font_size):
    font = ImageFont.truetype("arial.ttf", font_size)
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    
    # Get bounding box of the text
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    
    # bbox gives (x_min, y_min, x_max, y_max)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    return text_width, text_height

def apply_watermark_to_frame(frame, watermark_text, font_size, opacity, x_pos, y_pos):
    # Convert frame to PIL image
    pil_img = Image.fromarray(frame)
    
    # Apply watermark
    width, height = pil_img.size
    watermark_width, watermark_height = get_watermark_dimensions(watermark_text, font_size)
    pil_img = apply_watermark(pil_img, watermark_text, font_size, opacity, x_pos, y_pos)
    
    # Convert back to numpy array
    return np.array(pil_img)


def blur_video(input_file, blur_strength):
    # Open the input video file
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        st.error("Could not open video file.")
        return None

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a temporary output file
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Break the loop if there are no frames left

        # Apply Gaussian blur
        blurred_frame = cv2.GaussianBlur(frame, (blur_strength, blur_strength), 0)

        # Write the blurred frame to the output video
        out.write(blurred_frame)

    # Release resources
    cap.release()
    out.release()

    return output_file
