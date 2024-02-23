import cv2
import numpy as np

camera = cv2.VideoCapture(0) #Open Pi Camera
direction = ""

prev_centroid = None
prev_cX = None

while(1):
    ret, frame = camera.read() #Read Pi Camera
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Convert to HSV colour range
    
    # Define Green
    lower_green_boundary = np.array([25, 52, 45]) #HSV Values for Green (Lower End)
    upper_green_boundary = np.array([102, 255, 255]) #HSV Values for Green (Upper End)    
    green_mask = cv2.inRange(hsv, lower_green_boundary, upper_green_boundary) #Mask Green in Live View
    green = cv2.bitwise_and(frame, frame, mask=green_mask) #combines two shades
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Define Red
    lower_red_boundary = np.array([161, 155, 84]) #HSV Values for Red (Lower End)
    upper_red_boundary = np.array([179, 255, 255]) #HSV Values for Red (Upper End)    
    red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View    
    red = cv2.bitwise_and(frame, frame, mask=red_mask) #combines two shades
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Define White
    lower_white_boundary = np.array([0, 0, 200])
    upper_white_boundary = np.array([179, 30, 255])    
    white_mask = cv2.inRange(hsv, lower_white_boundary, upper_white_boundary) #Mask Green in Live View    
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    if red_contours:
        x, y, w, h = cv2.boundingRect(red_contours[0])
        
        largest_contour = max(red_contours, key=cv2.contourArea)
        
        M = cv2.moments(largest_contour)
        
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
            
        
        kayaker_position = (x + w // 2, y + h // 2)
        cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
        
        
        if prev_centroid is not None:
            prev_cX, _ = prev_centroid
            if cX > prev_cX:
                direction = "Left"
            elif cX < prev_cX:
                direction = "Right"
            else:
                direction = "No Motion"
                
        #print("Motion Direction:", direction)
        cv2.putText(frame, direction, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 2)
            
        prev_centroid = (cX, cY)

           
    #Create Windows to show different feeds
    cv2.imshow('Live Feed', frame)
    cv2.imshow('White Masking', white_mask)
    cv2.imshow('Green Masking', green)
    cv2.imshow('Red Masking', red)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    
# Close all windows
camera.release()
cv2.destroyAllWindows()
