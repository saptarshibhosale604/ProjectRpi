import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_still_configuration()
config["controls"]["AwbEnable"] = False  # Disable Auto White Balance
picam2.configure(config)
picam2.start()


def apply_gains(picam2, red_gain, blue_gain):
    # Dynamically set color gains
    picam2.set_controls({"ColourGains": (red_gain, blue_gain)})


while True:
	
	# User input for red and blue gains
	user_input = input("Enter red gain and blue gain (e.g., '1.5 1.2') or 'q' to quit: ")
	
	try:
		# Parse the user input
		red_gain, blue_gain = map(float, user_input.split())
	
		# Apply new gain values
		apply_gains(picam2, red_gain, blue_gain)
		print(f"Applied gains - Red: {red_gain}, Blue: {blue_gain}")
	
	except ValueError:
		print("Invalid input. Please enter two floating-point numbers separated by a space.")

	
	frame = picam2.capture_array()
	print(frame.shape)
	
	# Process the frame (resize in your case)
	frame1 = cv2.resize(frame, (640, 480))
	cv2.imshow("Frame", frame1)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

picam2.stop()
cv2.destroyAllWindows()
