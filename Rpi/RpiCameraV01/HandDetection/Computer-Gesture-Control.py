import cv2
from collections import Counter
from module import findnameoflandmark,findpostion,speak
import math


import os
from time import *

import keyboard
import subprocess

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
     #5 fingers Up does nothing
     #4 Video Start Playing
     #3 Video Stop Playing
     #2 Fingers Zero Volume
     #1 Fingers Full Volume
     #0 Shutdown but has been uncommented so won't activate
     
     
     if up == 4:
         
        keyboard.press_and_release('Ctrl+Alt+n')
        
         
     if up == 3:
        
        keyboard.press_and_release('Ctrl+Alt+b')
        
     
     if up == 2:
           
        volume = 100
        command = ["amixer", "sset", "Master", "{}%".format(volume)]
        subprocess.Popen(command)
     
     if up == 1:
           
        volume = 0
        command = ["amixer", "sset", "Master", "{}%".format(volume)]
        subprocess.Popen(command)    
         
     
     #if up == 0:
        #print('.......Shutting Down in 5 seconds initiated.......')
        #sleep(5)
        #os.system("sudo shutdown -h now")

     if key == ord("q"):
        speak("sir you have"+str(up)+"fingers up  and"+str(down)+"fingers down") 
                    
     if key == ord("s"):
       break