import cv2
import numpy as np

cap = cv2.VideoCapture(0) #Open Pi Camera

while(1):
    
    ret, frame = cap.read() #Read Pi Camera
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    light_green = np.array([40, 40, 40]) #HSV Values for Green (Lower End)
    dark_green = np.array([70, 255, 255]) #HSV Values for Green (Upper End)
    
    mask_green = cv2.inRange(hsv, light_green, dark_green) #Mask Green in Live View
    
    res_green = cv2.bitwise_and(frame, frame, mask=mask_green)
     
    light_yellow = np.array([0, 100, 100]) #HSV Values for Yellow (Lower End)
    dark_yellow = np.array([10, 255, 255]) #HSV Values for Yellow (Upper End
    
    green_contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, green_contours, -1, (0, 255, 0), 2)
    
    kayaker_mask = cv2.inRange(hsv, light_yellow, dark_yellow) #Mask Yellow in Live View
    kayaker_contours, _ = cv2.findContours(kayaker_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    pole_colours = []
    if len(green_contours) >= 2:
        pole_colours.append("Green")
    
    if kayaker_contours:
        x, y, w, h = cv2.boundingRect(kayaker_contours[0])
        
        kayaker_position = (x + w // 2, y + h // 2)
        cv2.circle(frame, kayaker_position, 10, (0, 0, 255), -1)
        
        if "Green" in pole_colours:
            direction = "Downstream"
        else:
            direction = "Pending"
    
    
    print(direction)
    
    #Create Windows to show different feeds
    cv2.imshow('Live Feed', frame)
    cv2.imshow('Green Masking', mask_green)
    cv2.imshow('Yellow Masking', kayaker_mask)
    cv2.imshow('Results', res_green)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): #Press q to terminate program
        break
    
# Close all windows
cap.release()
cv2.destroyAllWindows()
