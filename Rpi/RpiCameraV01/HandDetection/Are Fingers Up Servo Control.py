import cv2
from collections import Counter
from module import findnameoflandmark,findpostion,speak
import math

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
from time import *


kit.servo[0].angle = 140
kit.servo[1].angle = 140
kit.servo[2].angle = 130
kit.servo[3].angle = 160
kit.servo[4].angle = 140

#kit.servo[x].angle = 90
# 1 = Thumb
# 0 = Index
# 4 = Middle
# 2 = Ring
# 3 = Pinkie


cap = cv2.VideoCapture(0)
tip=[8,12,16,20]
tipname=[8,12,16,20]
fingers=[]
finger=[]


while True:

     ret, frame = cap.read()
     #flipped = cv2.flip(frame, flipCode = -1)
     frame1 = cv2.resize(frame, (640, 480))

     
     a=findpostion(frame1)
     b=findnameoflandmark(frame1)
     
      
     
     if len(b and a)!=0:
        finger=[]
        if a[0][1:] < a[4][1:]: 
           finger.append(1)
           print (b[4])
           
           
           #My Additions
           kit.servo[0].angle = 50
           kit.servo[1].angle = 40
           kit.servo[2].angle = 40
           kit.servo[3].angle = 40
           kit.servo[4].angle = 40
                      
        else:
           finger.append(0)   

        
        
        
        fingers=[] 
        for id in range(0,4):
            if a[tip[id]][2:] < a[tip[id]-2][2:]:
               
               
               print(b[tipname[id]])
               
               if a[tip[2]] < a[tip[2]-2]:
                   kit.servo[0].angle = 50
               
                   
              
               #My Additions
                #kit.servo[0].angle = 140
                #kit.servo[1].angle = 140
                #kit.servo[2].angle = 130
                #kit.servo[3].angle = 160
                #kit.servo[4].angle = 140
               
               
               
               
               fingers.append(1)
    
            else:
               fingers.append(0)
               
               #MY ADDITIONS
               kit.servo[0].angle = 140
               kit.servo[1].angle = 140
               kit.servo[2].angle = 130
               kit.servo[3].angle = 160
               kit.servo[4].angle = 140
               
               
     x=fingers + finger
     c=Counter(x)
     up=c[1]
     down=c[0]
     print(up)
     print(down)
     
     
     cv2.imshow("Frame", frame1);
     key = cv2.waitKey(1) & 0xFF
     if key == ord("q"):
        speak("sir you have"+str(up)+"fingers up  and"+str(down)+"fingers down") 
                    
     if key == ord("s"):
       break
