import cv2
import numpy as np
from PCA9685_MC import Motor_Controller
from Motor_Encoder import Encoder
from picamera2 import Picamera2
from libcamera import controls

tracker = cv2.TrackerKCF_create() 
# cap = cv2.VideoCapture(0)
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_width = 640  
frame_height = 480
cap = Picamera2()
cap.configure(cap.create_preview_configuration(main={"format": 'XRGB8888', "size": (frame_height, frame_width)}))
cap.set_controls({"AfMode": controls.AfModeEnum.Continuous})
cap.start()

motor = Motor_Controller()
enc = Encoder()

def tracking(frame, x,y,w,h):
    
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(frame, "Tracking", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'q' to quit", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, f"X:{x} , Y: {y}", (x ,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # Calculate the center of Bounding Box 
    center_x = x + w // 2
    center_y = y + h // 2
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Draw a circle at the center
    # Tracking Logic 
    enc.encoder() 
    if center_y < 220 and center_y > 100:
        if center_x < 300:
            print("Turn Left")
            motor.AntiClock_Rotate(20) 
        if center_x > 340:
            print("Turn Right")
            motor.Clock_Rotate(20)
        else:
            motor.Forward(20)
    elif center_y > 240 and center_y < 440:
        if center_x < 300:
            print("Turn Left")
            motor.AntiClock_Rotate(10)
        if center_x > 340:
            print("Turn Right")
            motor.Clock_Rotate(10)
        else:
            motor.Forward(10)
    else:
        motor.Brake()
    
    

def main(): 
    frame = cap.capture_array()
    bbox = cv2.selectROI(frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("ROI selector")
 
    # Initialize tracker with first frame and bounding box
    tracker.init(frame, bbox)

    # if not cap.isOpened():
    #     print("Error: Could not open video capture.")
    #     return
    # print(f"Tracking started with ROI: {bbox}")
    
    while True:
        frame = cap.capture_array()  # Read frame
        # Tracking mode: update the tracker and draw the tracked bounding box
        success, box = tracker.update(frame)  # Update the tracker with the new frame
        if success:
            (x, y, w, h) = [int(v) for v in box]
            tracking(frame, x,y,w,h)
        else:
            cv2.putText(frame, "Tracking failure", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            motor.Brake() 
        cv2.imshow('Tracking_Area', frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.stop()  # Release the video capture when done

try:
    if __name__ == '__main__':
        main()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
    motor.cleanup()
    enc.stop()
finally:
    cv2.destroyAllWindows()
    print("Program Terminated \nExiting....")