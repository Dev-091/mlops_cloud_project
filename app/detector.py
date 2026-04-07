# app/detector.py
import cv2
import mediapipe as mp
import numpy as np
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Initialize MediaPipe Tasks Hand Landmarker
model_path = os.path.join(os.path.dirname(__file__), "models", "hand_landmarker.task")
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
)
# Create detector (initialize only once)
detector = vision.HandLandmarker.create_from_options(options)


def count_fingers(frame):
    # Convert BGR to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    # Process hand landmarks
    detection_result = detector.detect(mp_image)

    count = 0
    landmarks = []

    if detection_result.hand_landmarks:
        # Results are a list of hand landmarks (one for each detected hand)
        for hand_landmarks in detection_result.hand_landmarks:
            # We map landmarks back to pixel coordinates for display and calculation
            h, w, _ = frame.shape
            lm_list = []
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            # Finger detection logic (Extended fingers)
            # Tip indices: Thumb (4), Index (8), Middle (12), Ring (16), Pinky (20)
            # PIP indices for comparison: Thumb (3), Index (6), Middle (10), Ring (14), Pinky (18)
            tips = [4, 8, 12, 16, 20]
            pips = [3, 6, 10, 14, 18]

            for tip, pip in zip(tips, pips):
                if tip == 4:  # Thumb
                    # Simple X-axis check for thumb extension (depends on hand side/orientation)
                    if lm_list[tip][1] < lm_list[pip][1]:
                        count += 1
                else:  # Other fingers
                    # Compare Y-axis (lower value is higher on screen)
                    if lm_list[tip][2] < lm_list[pip][2]:
                        count += 1
            landmarks = lm_list

    return count, landmarks
