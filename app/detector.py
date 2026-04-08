# app/detector.py
import cv2
import mediapipe as mp
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

_detector = None


def _get_detector():
    global _detector
    if _detector is not None:
        return _detector

    # Initialize MediaPipe Tasks Hand Landmarker lazily
    model_path = os.path.join(
        os.path.dirname(__file__), "models", "hand_landmarker.task"
    )
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
    )
    try:
        _detector = vision.HandLandmarker.create_from_options(options)
    except Exception:
        _detector = None
    return _detector


def count_fingers(frame):
    detector = _get_detector()
    if detector is None:
        return 0, []

    # Pre-resize for faster detection
    h, w, _ = frame.shape
    if w > 640:
        scale = 640 / w
        frame_proc = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    else:
        frame_proc = frame

    frame_rgb = cv2.cvtColor(frame_proc, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    # Process hand landmarks
    detection_result = detector.detect(mp_image)

    count = 0
    landmarks = []

    if detection_result.hand_landmarks:
        for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
            # Get handedness (Left or Right)
            handedness = detection_result.handedness[i][0].category_name

            h_proc, w_proc, _ = frame_proc.shape
            lm_list = []
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w_proc), int(lm.y * h_proc)
                lm_list.append((id, cx, cy))

            # Finger detection logic (Robust)
            if handedness == "Right":
                if lm_list[4][0] < lm_list[3][0]:  # Thumb
                    count += 1
            else:  # Left hand
                if lm_list[4][0] > lm_list[3][0]:  # Thumb
                    count += 1

            # Other fingers: Check if tip is above the PIP joint
            for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
                if lm_list[tip][2] < lm_list[pip][2]:
                    count += 1

            # Scale landmarks back for display
            display_lms = []
            scale_x = w / w_proc
            scale_y = h / h_proc
            for id, x, y in lm_list:
                display_lms.append((id, int(x * scale_x), int(y * scale_y)))
            landmarks = display_lms

    return count, landmarks
