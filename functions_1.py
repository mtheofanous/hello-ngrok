import streamlit as st
import cv2
import numpy as np

def apply_transformations(img, rotation_option, apply_transformation, blur_strength=None, size=None):
    """Apply the selected transformations to the image."""
    # Apply rotation
    if rotation_option == "90":
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif rotation_option == "180":
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rotation_option == "270":
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Apply blur transformation if selected
    if apply_transformation == "Apply Blur" and blur_strength and size:
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

    
