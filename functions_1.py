import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
from moviepy.editor import VideoFileClip


# Placeholder for watermark dimensions function
def get_watermark_dimensions(watermark_text, font_size):
    font = ImageFont.truetype("arial.ttf", font_size) # use PIL's ImageFont module to load the font
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1))) # create a new RGBA image to draw the text
    
    # Get bounding box of the text
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    
    # bbox gives (x_min, y_min, x_max, y_max)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    return text_width, text_height

# function to apply watermark on img_array
def apply_watermark(img, watermark_text, font_size, opacity, x_pos, y_pos):
    """
    Apply a watermark to a given image array.

    Args:
        img_array (numpy.ndarray): The image in NumPy array format (RGB).
        watermark_text (str): The text to use as a watermark.
        font_size (int): The font size of the watermark text.
        opacity (int): The opacity level of the watermark (0-255).
        x_pos (int): The x-position of the watermark.
        y_pos (int): The y-position of the watermark.

    Returns:
        numpy.ndarray: The image with the watermark applied.
    """
    # Convert the image array to a PIL image
    img = Image.fromarray(img)
    
    # Convert the image to RGBA mode
    img = img.convert("RGBA")
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # Load the font
    font = ImageFont.truetype("arial.ttf", font_size)
    
    # Create a new RGBA image for the watermark
    watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark)
    
    # Add the text to the watermark
    watermark_draw.text((x_pos, y_pos), watermark_text, font=font, fill=(255, 255, 255, opacity))
    
    # Combine the original image with the watermark
    watermarked_image = Image.alpha_composite(img, watermark)
    
    # Convert the image back to RGB mode
    watermarked_image = watermarked_image.convert("RGB")
    
    return np.array(watermarked_image)
   

def apply_rotate(img, rotation_option):
    """Rotate the image based on the selected option."""
    if rotation_option == "90":
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif rotation_option == "180":
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rotation_option == "270":
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
    return img 

def apply_blur(img, size, blur_strength):

    # Apply blur transformation if selected
    mask = np.zeros(img.shape[:2], dtype="uint8")
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    x_min = round(center[0] - (center[0] // size))
    x_max = round(center[0] + (center[0] // size))
    y_min = round(center[1] - (center[1] // size))
    y_max = round(center[1] + (center[1] // size))
    
    cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
    blurred_img = cv2.GaussianBlur(img, (blur_strength, blur_strength), 0)
    img = np.where(mask[..., None] == 255, blurred_img, img)
        
    return img

def resize_video(file_path, new_height, new_width):
    """
    Resize the video to a specified width and height.
    """
    # Load the video
    video_clip = VideoFileClip(file_path)
    
    # Resize the video to the new width and height
    resized_clip = video_clip.resize(newsize=(new_height, new_width))
    
    # Create a temporary file for the resized video
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        output_path = temp_file.name

    # Write the resized video to the temp file
    resized_clip.write_videofile(output_path,
        codec="libx264",  # Efficient video codec
        preset="fast",  # Better compression (slower = better)
        ffmpeg_params=[
            "-crf", "28",
            "-b:a", "64k"
        ],
        audio_codec="aac"  # Audio codec for better compression
    )

    return output_path

