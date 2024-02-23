import cv2
import numpy as np

def detect_objects(frame):
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Convert to HSV colour range
    
    #red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    pole_detected = False
    kayaker_detected = False
    x_pole, y_pole, w_pole, h_pole = 0, 0, 0, 0
    
    for red_contour in red_contours:
        area = cv2.contourArea(red_contour)
        
        if area > 1000:
            pole_detected = True
            x_pole, y_pole, w_pole, h_pole = cv2.boundingRect(red_contour)
            cv2.rectangle(frame, (x_pole, y_pole), (x_pole + w_pole, y_pole + h_pole), (0, 255, 0), 2)
            
    return pole_detected, kayaker_detected, (x_pole, y_pole, w_pole, h_pole)

#camera = cv2.VideoCapture(0) #Open Pi Camera
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0005.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0006.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0007.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0008.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0009.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0010.jpg')
#video = cv2.VideoCapture('/home/pi/Desktop/Group1-Camera-Vision/Photos/VID-20240223-WA0007.mp4')
#video = cv2.VideoCapture('/home/pi/Desktop/Group1-Camera-Vision/Photos/VID-20240223-WA0009.mp4')
video = cv2.VideoCapture('/home/pi/Desktop/Group1-Camera-Vision/Photos/reverse_clip.mp4')

#if image is None:
    #print("Image Error")

#if video is None:
    #print("Video Error")

direction = "" # Varibale for direction of paddles

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

# Define Purple
lower_purple_boundary = np.array([120, 50, 50])
upper_purple_boundary = np.array([170, 255, 255])

previous_kayaker_center = None

while(1):
    
    ret, frame = video.read() #Read Pi Camera
    #if not ret:
        #print("Camera Failed")
        #break
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Convert to HSV colour range
    red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View
    
    pole_detected, kayaker_detected, pole_area = detect_objects(red_mask)
    
    if pole_detected and kayaker_detected:
        x_kayaker, y_kayaker, w_kayaker, h_kayaker = pole_area
        kayaker_center = (x_kayaker + w_kayaker // 2, y_kayaker + h_kayaker // 2)
        
        cv2.line(frame, kayaker_center, (x_pole + w_pole // 2, y_pole + h_pole // 2, (0, 0, 255), 2), (0, 0, 255), 2)
        
        if previous_object_center is not None:
            direction_vector = (kayaker_center[0] - previous_kayaker_center[0], kayaker_center[1] - previous_kayaker_center[1])
            
            if direction_vetor[0] > 0:
                direction = "Right"
            elif direction_vector[0] < 0:
                direction = "Left"
            else:
                direction = "None"
            cv2.putText(frame, direction, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 1)
        
        previous_kayaker_center = kayaker_center
    
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Convert to HSV colour range

    red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View
    purple_mask = cv2.inRange(hsv, lower_purple_boundary, upper_purple_boundary)
    #red = cv2.bitwise_and(frame, frame, mask=red_mask) #combines two shades
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    background_mask = background_subtractor.apply(red_mask)
    contours, _ = cv2.findContours(background_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for red_contour in red_contours: # Run whenever green detected
        
        pole_largest_contour = max(red_contours, key=cv2.contourArea) # Find largest green area 
        
        x, y, w, h = cv2.boundingRect(pole_largest_contour) # Rectangle around green item
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Rectangle Frame in fed
        #green_pole_roi = frame[y:y+h, x:x+w]
        #green_pole_edges = cv2.Canny(green_pole_roi, 100, 200)
        
        for purple_contour in purple_contours: # Run when red detected
            #kayaker_largest_contour = max(red_contours, key=cv2.contourArea) # Largest x area
            M = cv2.moments(purple_contour)
        
            if M["m00"] != 0: # Moments to determine center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Determine if right or left of pole
                if cX < x + w // 2:
                    direction = ("Left of Pole")
                else:
                    direction = ("Right of Pole")
               
        # Output direction to screen
        cv2.putText(frame, direction, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 1)
        
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area < 100:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        
        cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)
        RED_POLE_REGION = x + w // 2
        
        if x < RED_POLE_REGION < x + w:
            
            if start_point is None:
                start_point = (x, y)
                
            else:
                end_point = (x, y)
                direction = "Right" if end_point[0] > start_point[0] else "Left"
                
        cv2.putText(frame, direction, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 1)
    """
    #red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View    
    #red = cv2.bitwise_and(frame, frame, mask=red_mask) #combines two shades
    #red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #blurred_image = cv2.GaussianBlur(hsv, (15, 15), 0)
    #canny = cv2.Canny(red_mask, 50, 150)
    #contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    
    #for contour in contours:
        #length = 0.03 * cv2.arcLength(contour, True)
        #approx = cv2.approxPolyDP(contour, length, True)
        
    #white_mask = cv2.inRange(hsv, lower_white_boundary, upper_white_boundary) #Mask Green in Live View    
    #white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    #yellow_mask = cv2.inRange(hsv, lower_yellow_boundary, upper_yellow_boundary) #Mask Green in Live View    
    #yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    #green_mask = cv2.inRange(hsv, lower_green_boundary, upper_green_boundary) #Mask Green in Live View
    #green = cv2.bitwise_and(frame, frame, mask=green_mask) #combines two shades
    #green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
    """
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
                
                #cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
                cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
                
                # Determine if right or left of pole
                if cX < x + w // 2:
                    direction = ("Right of Pole")
                else:
                    direction = ("Left of Pole")
               
        # Output direction to screen
        cv2.putText(frame, direction, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 1)
            
    """
    cv2.imshow('Live Feed', frame) # Open Live Feed Window
    #cv2.imshow('Video Feed', video)
    #cv2.imshow("Purple", purple_mask)
    #cv2.imshow("Red", background_mask)
    
    # Close all program if 'e' is entered
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break
    
# Close all windows
frame.release()
cv2.destroyAllWindows()




