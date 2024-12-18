#Import the necessary Packages and scritps for this software to run (Added speak in
#there too as an easer egg)
import cv2
from collections import Counter
from module import findnameoflandmark,findpostion,speak
import math
from picamera2 import Picamera2

print("initialized")

#Use CV2 Functionality to create a Video stream and add some values + variables
# ~ cap = cv2.VideoCapture(0)


picam2 = Picamera2()
config = picam2.create_still_configuration()
config["controls"]["AwbEnable"] = False  # Disable Auto White Balance
picam2.configure(config)
picam2.start()            


def apply_gains(picam2, red_gain, blue_gain):
	# Dynamically set color gains
	picam2.set_controls({"ColourGains": (red_gain, blue_gain)})
				
				
 
tip=[8,12,16,20]
tipname=[8,12,16,20]
fingers=[]
finger=[]

#Create an infinite loop which will produce the live feed to our desktop and that will search for hands
while True:
	
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
									                                             
	#Determines the frame size, 640 x 480 offers a nice balance between speed and accurate identification
	frame1 = cv2.resize(frame, (640, 480))
	
	#Below is used to determine location of the joints of the fingers 
	a=findpostion(frame1)
	b=findnameoflandmark(frame1)
	
	#Below is a series of If statement that will determine if a finger is up or down and
	#then will print the details to the console
	if len(b and a)!=0:
		finger=[]
		if a[0][1:] < a[4][1:]: 
			finger.append(1)
			print (b[4])
		  
		else:
			finger.append(0)   
		
		fingers=[] 
		for id in range(0,4):
			if a[tip[id]][2:] < a[tip[id]-2][2:]:
			   print(b[tipname[id]])
		
			   fingers.append(1)
		
			else:
			   fingers.append(0)
			   
	#Below will print to the terminal the number of fingers that are up or down          
	x=fingers + finger
	c=Counter(x)
	up=c[1]
	down=c[0]
	print('This many fingers are up - ', up)
	print('This many fingers are down - ', down)
	
	
	#Below shows the current frame to the desktop 
	cv2.imshow("Frame", frame1);
	key = cv2.waitKey(1) & 0xFF
	
	
	#Below will speak out load when |s| is pressed on the keyboard about what fingers are up or down
	if key == ord("q"):
		speak("you have"+str(up)+"fingers up  and"+str(down)+"fingers down") 
	
	#Below states that if the |s| is press on the keyboard it will stop the system
	if key == ord("s"):
		break
	
