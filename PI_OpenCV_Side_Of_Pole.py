import cv2
import numpy as np

camera = cv2.VideoCapture(0) #Open Pi Camera
direction = "" # Varibale for direction of paddler

# Define White
lower_white_boundary = np.array([0, 0, 200])
upper_white_boundary = np.array([179, 30, 255])

# Define Yellow
lower_yellow_boundary = np.array([20, 100, 100])
upper_yellow_boundary = np.array([40, 255, 255])

# Define Green
lower_green_boundary = np.array([25, 52, 45]) #HSV Values for Green (Lower End)
upper_green_boundary = np.array([102, 255, 255]) #HSV Values for Green (Upper End)

# Define Red
lower_red_boundary = np.array([161, 155, 84]) #HSV Values for Red (Lower End)
upper_red_boundary = np.array([179, 255, 255]) #HSV Values for Red (Upper End) 

while(1):
    
    ret, frame = camera.read() #Read Pi Camera
    if not ret:
        print("Camera Failed")
        break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Convert to HSV colour range
        
    white_mask = cv2.inRange(hsv, lower_white_boundary, upper_white_boundary) #Mask Green in Live View    
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    #yellow_mask = cv2.inRange(hsv, lower_yellow_boundary, upper_yellow_boundary) #Mask Green in Live View    
    #yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    green_mask = cv2.inRange(hsv, lower_green_boundary, upper_green_boundary) #Mask Green in Live View
    #green = cv2.bitwise_and(frame, frame, mask=green_mask) #combines two shades
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View    
    #red = cv2.bitwise_and(frame, frame, mask=red_mask) #combines two shades
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for green_contour in red_contours: # Run whenever green detected
        
        pole_largest_contour = max(red_contours, key=cv2.contourArea) # Find largest green area 
        
        x, y, w, h = cv2.boundingRect(pole_largest_contour) # Rectangle around green item
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Rectangle Frame in fed
        #green_pole_roi = frame[y:y+h, x:x+w]
        #green_pole_edges = cv2.Canny(green_pole_roi, 100, 200)
        
        for red_contour in white_contours: # Run when red detected
            #kayaker_largest_contour = max(red_contours, key=cv2.contourArea) # Largest x area
            M = cv2.moments(red_contour)
        
            if M["m00"] != 0: # Moments to determine center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Determine if right or left of pole
                if cX < x + w // 2:
                    direction = ("Right of Pole")
                else:
                    direction = ("Left of Pole")
               
        # Output direction to screen
        cv2.putText(frame, direction, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 1)
            
    
    cv2.imshow('Live Feed', frame) # Open Live Feed Window
    #cv2.imshow("Canny", canny)
    #cv2.imshow("Red", red)
    
    # Close all program if 'e' is entered
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break
    
# Close all windows
camera.release()
cv2.destroyAllWindows()

