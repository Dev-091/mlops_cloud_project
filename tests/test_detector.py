# test_detector.py
import cv2
from app.detector import count_fingers

cap = cv2.VideoCapture(0)
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret: 
        break
        
    count, landmarks = count_fingers(frame)
    
    # Draw landmarks manually since solutions.drawing_utils is gone
    for lm in landmarks:
        cv2.circle(frame, (lm[1], lm[2]), 5, (0, 255, 0), -1)
        
    cv2.putText(frame, f"Fingers: {count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Finger Counter", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()