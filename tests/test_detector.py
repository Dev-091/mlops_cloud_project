import numpy as np

from app.detector import count_fingers


def test_count_fingers_handles_blank_frame():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    count, landmarks = count_fingers(frame)

    assert count == 0
    assert landmarks == []
