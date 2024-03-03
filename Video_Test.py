import cv2
import numpy as np
import time

# video = cv2.VideoCapture('./Photos/reverse_clip.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0009.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0007.mp4')
#video = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0005.jpg')
#video = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0006.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0007.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0008.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0009.jpg')
#image = cv2.imread('/home/pi/Desktop/Group1-Camera-Vision/Photos/IMG-20240223-WA0010.jpg')
#video = cv2.VideoCapture('/home/pi/Desktop/Group1-Camera-Vision/Photos/VID-20240223-WA0007.mp4')
#video = cv2.VideoCapture('/home/pi/Desktop/Group1-Camera-Vision/Photos/VID-20240223-WA0009.mp4')
#video = cv2.VideoCapture('/home/pi/Desktop/Group1-Camera-Vision/Photos/reverse_clip.mp4')
video = cv2.VideoCapture(0) #Open Pi Camera

#video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#video.set(cv2.CAP_PROP_FPS, 30)

direction = ""
overlaps = False
#frame_counter = 0
overlap_detected = False
overlap_start_time = 0
overalaps = 0

# Define range of red color in HSV
#lower_red = np.array([161,155,84])
#upper_red = np.array([179,255,255])

lower_red = np.array([129,100,50])
upper_red = np.array([179,255,255])
    
# Define Purple
lower_purple = np.array([120, 50, 50])
upper_purple = np.array([170, 255, 255])

# Define Green
#lower_green = np.array([25, 52, 45]) #HSV Values for Green (Lower End)
#upper_green = np.array([102, 200, 200]) #HSV Values for Green (Upper End)

# Orange
lower_orange = np.array([5, 100, 100])
upper_orange = np.array([15, 255, 255])

while(1):
    # Convert BGR to HSV
    
    ret, frame = video.read() #Read Pi Camera
    #frame = video
    #frame_counter += 1

    #if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
        #frame_counter = 0
        #video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only red colors
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    #purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
    #green_mask = cv2.inRange(hsv, lower_green, upper_green)
    orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Find contours
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #pole_largest_contour = max(red_contours, key=cv2.contourArea)
    #x, y, w, h = cv2.boundingRect(pole_largest_contour) # Rectangle around green item

    # Count red stripes
    red_stripe_count = 0
    for red_contour in red_contours:
        pole_largest_contour = max(red_contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(pole_largest_contour) # Rectangle around green item
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #cv2.drawContours(frame, [red_contour], -1, (0,  255, 0), 2)
        if cv2.contourArea(red_contour) > 10:
            red_stripe_count += 1
            # Draw contours for visualization
            cv2.drawContours(frame, [red_contour], -1, (0,  255, 0), 2)
            #pole_largest_contour = max(red_contours, key=cv2.contourArea)
            #x, y, w, h = cv2.boundingRect(pole_largest_contour) # Rectangle around green item
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            break
        for orange_contour in orange_contours: # Run when red detected
            #kayaker_largest_contour = max(red_contours, key=cv2.contourArea) # Largest x area
            M = cv2.moments(orange_contour)
        
            if M["m00"] != 0: # Moments to determine center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Determine if right or left of pole
                if cX < ( (x + w // 2) + (y + h // 2) // 2 ):
                    direction = ("Left of Pole")
                else:
                    direction = ("Right of Pole")
    """
    for orange_contour in orange_contours:
        for red_contour in red_contours:
            orange_binary = np.zeros_like(orange_mask)
            red_binary = np.zeros_like(red_mask)
            cv2.drawContours(orange_binary, [orange_contour], -1, 255, -1)
            cv2.drawContours(red_binary, [red_contour], -1, 255, -1)

                # Perform bitwise AND operation
            intersection = cv2.bitwise_and(orange_binary, red_binary)
            intersection_area = np.count_nonzero(intersection)
            if intersection_area > 50:  # Adjust threshold as needed
                overlaps += 1
                break
        if overlaps:
            break
    """
    # Display the result
    cv2.putText(frame, "Red Stripes: {}".format(red_stripe_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    #cv2.putText(frame, "Purple Overlaps Red: {}".format(overlaps), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, "Position: {}".format(direction), (20,120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow('Poles', frame)
    cv2.imshow('Red Mask', red_mask)
    #cv2.imshow('purple mask', purple_mask)
    #cv2.imshow('Green mask', green_mask)
    cv2.imshow('Orange Mask', orange_mask)
    #if overlaps:
        #time.sleep(1)
    
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break
    
# Close all windows
video.release()
cv2.destroyAllWindows()
