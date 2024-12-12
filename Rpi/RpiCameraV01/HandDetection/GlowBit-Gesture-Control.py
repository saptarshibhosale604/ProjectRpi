import cv2
from collections import Counter
from module import findnameoflandmark,findpostion,speak
import math

import os
from time import *

import glowbit
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
matrix = glowbit.matrix4x4(brightness = 255, rateLimitFPS = 80)

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
           
           #volume = 100
           #command = ["amixer", "sset", "Master", "{}%".format(volume)]
           #subprocess.Popen(command)
           
                      
        else:
           finger.append(0)     
        
        
        
        fingers=[] 
        for id in range(0,4):
            if a[tip[id]][2:] < a[tip[id]-2][2:]:
               
               
               print(b[tipname[id]])
               
               if a[tip[2]] < a[tip[2]-2]:
                   kit.servo[0].angle = 50
               
                   
               
               
               fingers.append(1)
    
            else:
               fingers.append(0)
               
              
               
               
     x=fingers + finger
     c=Counter(x)
     up=c[1]
     down=c[0]
     print(up)
     print(down)
     
     
     cv2.imshow("Frame", frame1);
     key = cv2.waitKey(1) & 0xFF
    
    
     #My Additions
     #Multiple Colours Based on Fingers
     if up == 1:
        
        c = matrix.purple()
        matrix.pixelsFill(c)
     
     if up == 2:
        
        c = matrix.yellow()
        matrix.pixelsFill(c)
     
     if up == 3:
        
        c = matrix.blue()
        matrix.pixelsFill(c)
     
     if up == 4:
        
        c = matrix.red()
        matrix.pixelsFill(c)
     
     if up == 0:
        
        c = matrix.green()
        matrix.pixelsFill(c)
     
     #Below will make the 4x4 matrice shine the correct colour based on If statements based on fingers
     matrix.pixelsShow()
        
     
     if key == ord("q"):
        speak("sir you have"+str(up)+"fingers up  and"+str(down)+"fingers down") 
                    
     if key == ord("s"):
       break
