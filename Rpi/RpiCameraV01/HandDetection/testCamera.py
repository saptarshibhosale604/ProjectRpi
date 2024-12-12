# ~ import cv2

#cap = cv2.VideoCapture(0)  # Initialize the camera (adjust index if needed)
# ~ from picamera2 import Picamera2


# ~ cap = cv2.VideoCapture(0)
# ~ print(f"Camera opened: {cap.isOpened()}")



# ~ if not cap.isOpened():
    # ~ print("Error: Could not open the camera.")
    # ~ exit()
import cv2
from picamera2 import Picamera2


picam2 = Picamera2()
picam2.start()



while True:
    # ~ #ret, frame = cap.read()
	# ~ ret, frame = cap.read()
	# ~ print(f"Frame captured: {ret}, Frame is None: {frame}")

    #if not ret is None:
        #print("Error: Failed to capture a ret.")
        #break
    #if frame is None:
     #   print("Error: Failed to capture a frame.")
      #  break
    
	# ~ picam2 = Picamera2()
	# ~ picam2.start()
    
	frame = picam2.capture_array()
	print(frame.shape)

	# Process the frame (resize in your case)
	frame1 = cv2.resize(frame, (640, 480))
	cv2.imshow("Frame", frame1)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# ~ cap.release()

picam2.stop()
cv2.destroyAllWindows()
