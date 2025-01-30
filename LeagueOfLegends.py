import cv2
import numpy as np
import os
from scipy.spatial import distance
from collections import defaultdict
from glob import glob

# Function to compute color histogram from an image array
def compute_histogram_from_array(image, bins=(8, 8, 8)):
    if image is None:
        raise ValueError("Invalid image provided.")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convert to HSV for consistent color representation
    hist = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

# Function to compute histogram from an image file
def compute_histogram_from_file(image_path, bins=(8, 8, 8)):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Error loading image: {image_path}")
    return compute_histogram_from_array(image, bins)

# Function to find best match using an image array instead of a file path
def find_best_match(input_image_array, image_library_path):
    input_hist = compute_histogram_from_array(input_image_array)

    similarities = defaultdict(float)

    # Load all valid image files in the library
    for img_path in glob(os.path.join(image_library_path, '*.*')):  # Load all image types
        if img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):  # Ensure it's an image
            hist = compute_histogram_from_file(img_path)
            sim = distance.euclidean(input_hist, hist)  # Use Euclidean distance for similarity
            similarities[img_path] = sim

    if not similarities:
        raise ValueError("No valid images found in the library.")

    # Find the closest image (smallest distance)
    best_match_path = min(similarities, key=similarities.get)

    # Extract filename without extension
    best_match_name = os.path.splitext(os.path.basename(best_match_path))[0]

    return best_match_name

image_library = "AllLeagueChampions"
