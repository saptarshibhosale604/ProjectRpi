import cv2
import numpy as np

# Initialize the camera
# ~ cap = cv2.VideoCapture(0)
# ~ import cv2
from picamera2 import Picamera2


picam2 = Picamera2()
picam2.start()

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# Define the color range for the pen (you may need to adjust these values)
# Example for a blue pen
lower_color = np.array([100, 150, 0])
upper_color = np.array([140, 255, 255])

# Create a blank image to draw the path
path_image = np.zeros((480, 640, 3), dtype=np.uint8)

while True:
    # ~ ret, frame = cap.read()
    # ~ if not ret:
        # ~ break
	
    frame = picam2.capture_array()
    print(frame.shape)

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the pen color
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours of the masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the center of the contour
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Draw the path on the path image
            cv2.circle(path_image, (cX, cY), 5, (255, 255, 255), -1)

            # Draw the path on the original frame
            cv2.circle(frame, (cX, cY), 5, (0, 255, 0), -1)

    # Combine the original frame with the path image
    combined = cv2.addWeighted(frame, 0.7, path_image, 0.3, 0)

    # Show the combined image
    cv2.imshow('Tracking', combined)

    # Write the frame to the output file
    out.write(combined)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
out.release()
cv2.destroyAllWindows()
