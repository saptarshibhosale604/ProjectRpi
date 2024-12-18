#Import the necessary Packages for this software to run
import mediapipe
import cv2
from picamera2 import Picamera2

print("initialized")
#Use MediaPipe to draw the hand framework over the top of hands it identifies in Real-Time
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

picam2 = Picamera2()
config = picam2.create_still_configuration()
config["controls"]["AwbEnable"] = False  # Disable Auto White Balance
picam2.configure(config)
picam2.start()            


def apply_gains(picam2, red_gain, blue_gain):
	# Dynamically set color gains
	picam2.set_controls({"ColourGains": (red_gain, blue_gain)})
	

# ~ fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

#Add confidence values and extra settings to MediaPipe hand tracking. As we are using a live video stream this is not a static
#image mode, confidence values in regards to overall detection and tracking and we will only let two hands be tracked at the same time
#More hands can be tracked at the same time if desired but will slow down the system
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:

	#Create an infinite loop which will produce the live feed to our desktop and that will search for hands
	while True:
		# User input for red and blue gains
		# ~ user_input = input("Enter red gain and blue gain (e.g., '1.5 1.2') or 'q' to quit: ")
		user_input = "1 3"
		try:
			# Parse the user input
			red_gain, blue_gain = map(float, user_input.split())
		
			# Apply new gain values
			apply_gains(picam2, red_gain, blue_gain)
			print(f"Applied gains - Red: {red_gain}, Blue: {blue_gain}")
		
		except ValueError:
			print("Invalid input. Please enter two floating-point numbers separated by a space.")

		frame = picam2.capture_array()  
		
		# Convert the 4-channel image (BGRA) to a 3-channel image (BGR)
		if frame.shape[2] == 4:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
		
		print(frame.shape) 
		
		#Unedit the below line if your live feed is produced upsidedown
		#flipped = cv2.flip(frame, flipCode = -1)
		
		#Determines the frame size, 640 x 480 offers a nice balance between speed and accurate identification
		frame1 = cv2.resize(frame, (640, 480))
		
		#produces the hand framework overlay ontop of the hand, you can choose the colour here too)
		results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
		
		#Incase the system sees multiple hands this if statment deals with that and produces another hand overlay
		if results.multi_hand_landmarks != None:
			for handLandmarks in results.multi_hand_landmarks:
				drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)
			  
			#   Added Code to find Location of Index Finger !!
			for point in handsModule.HandLandmark:
				
				normalizedLandmark = handLandmarks.landmark[point]
				pixelCoordinatesLandmark= drawingModule._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, 640, 480)
				
				if point == 8:
					print(point)
					print(pixelCoordinatesLandmark)
					print(normalizedLandmark)
							
		#Below shows the current frame to the desktop 
		cv2.imshow("Frame", frame1);
		key = cv2.waitKey(1) & 0xFF
		
		#Below states that if the |q| is press on the keyboard it will stop the system
		if key == ord("q"):
		  break
	
	
