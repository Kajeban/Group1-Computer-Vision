# Group 1 - MEng Group Project
# Computer Vision Code
# Written in Python
# Kajeban Baskaran

import cv2
import numpy as np
import time 
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import subprocess

# server_ip = "172.20.10.5"
server_ip = "192.168.81.237"
topic = "GateNegotiation"

# Open Pi Camera/Open Video File

video = cv2.VideoCapture(0)
# video = cv2.VideoCapture('./Photos/reverse_clip.mp4')
# video = cv2.VideoCapture('./Photos/VID-20240223-WA0009.mp4')
# video = cv2.VideoCapture('./Photos/VID-20240223-WA0007.mp4')

def check_mqtt(server_ip):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    try:
        client.connect(server_ip, 1883, 60)
        client.disconnect()
        return True
    except OSError:
        return False

# def nothing(x):
#     pass

# #  Define trackbars to determine precise colour
# cv2.namedWindow("Trackbars")

# cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
# cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("U - H", "Trackbars", 0, 179, nothing)
# cv2.createTrackbar("U - S", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("U - V", "Trackbars", 0, 255, nothing)

frame_counter = 0
# frame_passed = 0
# direction = None
overlaps = None
# prev_centroids = []
prev_red_area = 0
prev_green_area = 0
# pass_ = None
pole_colour = None
message = None
message_published = False
temparture = None
memory_use = None

previous_position = None
movement_started_1 = False
movement_started_2 = False
crossed_pole = False
direction_after_crossing = None

# Define range of red color in HSV
# lower_red = np.array([160,153,104])
# upper_red = np.array([179,255,255])

# Define Red in lab
lower_red = np.array([154,85,63])
upper_red = np.array([179,255,141])
    
# Define Purple
# lower_yellow = np.array([125, 193, 47])
# upper_yellow = np.array([153, 255, 106])

# Define Yellow
# lower_yellow = np.array([19, 114, 223])
# upper_yellow = np.array([27, 255, 255])

# Define Yellow (Labs)
lower_yellow = np.array([17, 104, 37])
upper_yellow = np.array([74, 255, 173])

# Define Green
lower_green = np.array([33, 77, 93]) #HSV Values for Green (Lower End)
upper_green = np.array([92, 255, 255]) #HSV Values for Green (Upper End) 

connection = False
iterations = 0
while (connection != True) and (iterations < 5):
    connection = check_mqtt(server_ip)
    print("Trying to connect... [",iterations,"]")
    iterations += 1

timer_started = False
if connection == True:
    publish.single("Timer", "True", hostname=server_ip)
    timer_started = True

# publish.single("Timer", "True", hostname=server_ip)
while(1):
    # Convert BGR to HSV
#     if connection:
#         core_voltage = get_core_voltage()
#         temperature = core_voltage
#         publish.single(topic2, temperature, hostname=server_ip)
#     
#         total, free, used = get_memory_use()
#         memory_use = int(used / total * 100)
#         publish.single(topic3, memory_use, hostname=server_ip)
    
    ret, frame = video.read() #Read Pi Camera

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     
#     l_h = cv2.getTrackbarPos("L - H", "Trackbars")
#     l_s = cv2.getTrackbarPos("L - S", "Trackbars")
#     l_v = cv2.getTrackbarPos("L - V", "Trackbars")
#     u_h = cv2.getTrackbarPos("U - H", "Trackbars")
#     u_s = cv2.getTrackbarPos("U - S", "Trackbars")
#     u_v = cv2.getTrackbarPos("U - V", "Trackbars")
# 
#     lower_colour = np.array([l_h, l_s, l_v])
#     upper_colour = np.array([u_h, u_s, u_v])
#     masked = cv2.inRange(hsv, lower_colour, upper_colour)
# 
#     cv2.imshow("Frame", frame)
#     cv2.imshow('Mask', masked)

#     frame = cv2.GaussianBlur(frame, (5,5), 0)
#     
#     frame_counter += 1
# 
#     if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
#         frame_counter = 0
#         video.set(cv2.CAP_PROP_POS_FRAMES, 0)
# #         direction_after_crossing = None
# #         overlaps = None
# #         message_published = False
# 
    # Threshold the HSV image to get only red colors
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    #purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    green_mask = cv2.inRange(hsv, lower_green, upper_green) #Mask Green in Live View

    # Find contours
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Extract red points from contours
    red_points = []
    for red in red_contours:
        for point in red:
            red_points.append(point[0])
    
    # Extract green points from contours
    green_points = []
    for green in green_contours:
        for point in green:
            green_points.append(point[0])
    
    # Extract Yellow points form contours
    yellow_points = []
    for yellow in yellow_contours:
        for point in yellow:
            yellow_points.append(point[0])

    red_area = sum(cv2.contourArea(contour) for contour in red_contours)  # Find total red area sum
    green_area = sum(cv2.contourArea(contour) for contour in green_contours) # Find total green area sum
    
    if (len(red_points) >= 40) or (len(green_points) >= 40): #If red or green is present
        
        # Determine if red pole or green pole
        if len(red_points) > len(green_points):
            pole_colour = "Red"
            [vx, vy, x, y] = cv2.fitLine(np.array(red_points), cv2.DIST_L2, 0, 0.01, 0.01)
            red_area = sum(cv2.contourArea(contour) for contour in red_contours)
        elif len(green_points) >= len(red_points):
            pole_colour = "Green"
            [vx, vy, x, y] = cv2.fitLine(np.array(green_points), cv2.DIST_L2, 0, 0.01, 0.01)
            green_area = sum(cv2.contourArea(contour) for contour in green_contours)
        
        # Determine slope and intercept of line
        slope = vy / vx
        intercept = y - (slope * x)

        # Calculate endpoints of the line to draw
        height, width, _ = frame.shape
        x1 = 0
        y1 = (slope * x1 + intercept).item()
        x2 = width - 1
        y2 = (slope * x2 + intercept).item()
        
        # Limit y1 and y2 values
        y1 = max(min(y1, 2147483647), -2147483647)
        y2 = max(min(y2, 2147483647), -2147483647)

        # Draw the line
        cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # Midpoint of X points
        mp_x = int((x1+x2) / 2)
#         mp_y = int((y1+y2) / 2)
        
        # Check if any yellow contour intersects the line
        if len(yellow_points) >= 15: 
            for yellow in yellow_contours:
                
                largest = max(yellow_contours, key=cv2.contourArea) # Determine largest area of yellow
                
                # Calculate the centroid of the contour
                M = cv2.moments(largest)
                
                # Determine center co-ordinates of yellow
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroid = (cx, cy) 
                    
                    # Draw circle around yellow item                    
                    cv2.circle(frame, centroid, 10, (0, 255, 255), -1)
                       
                    # Determine if kayaker starts from right or left of frame   
                    if (movement_started_1 == False) and (movement_started_2 == False):
                        if (mp_x < cx):
                            movement_started_1 = True
                        elif (mp_x > cx):
                            movement_started_2 = True
                    # Determine if kayaker crosses the pole and in which direction
                    else:
                        if ((crossed_pole == False) and previous_position != None):
                            if not (mp_x < cx) and (mp_x < previous_position) and (movement_started_1):
                                crossed_pole = True
                                if (mp_x > cx):
                                    direction_after_crossing = ("Left")
                                elif (mp_x < cx):
                                    direction_after_crossing = ("Right")
                            elif not (mp_x > cx) and (mp_x > previous_position) and (movement_started_2):
                                crossed_pole = True
                                if (mp_x > cx):
                                    direction_after_crossing = ("Left")
                                elif (mp_x <= cx):
                                    direction_after_crossing = ("Right")

                    # Previous Co-ordinates == Current Co-ordinates                     
                    previous_position = cx
                    
                    # used to determine if kayaker crosses in between poles or outside of poles
                    if movement_started_1 or movement_started_2:                            
                        if (pole_colour == "Green"):
                            if (mp_x > cx):
                                direction_after_crossing = ("Left")
                            elif (mp_x < cx):
                                direction_after_crossing = ("Right")
                                
                            if green_area < prev_green_area * 0.88:
                                overlaps = ("Intersects")
                                
                            prev_green_area = green_area
                            
                        elif (pole_colour == "Red"):
                            if (mp_x > cx):
                                direction_after_crossing = ("Left")
                            elif (mp_x < cx):
                                direction_after_crossing = ("Right")
                                
                            if red_area < prev_red_area * 0.88:
                                overlaps = ("Intersects")
                            
                            prev_red_area = red_area                   
                
                # Run when kayaker crosses between poles and no message has been transmitted (to avoid repeatedly sending same message)
                if crossed_pole and (message_published == False):
                    if (pole_colour == "Red"):
                        if ((overlaps == "Intersects") and (direction_after_crossing == "Left")):
                            message = "Red Gate - Pass"

                        else:
                            pass_= "Gate Unsuccesful"
                            message = "Red Gate - Fail"
                            

                    elif (pole_colour == "Green"):
                        if ((overlaps == "Intersects") and (direction_after_crossing == "Right")):
                            message = "Green Gate - Pass"

                        else:
                            message = "Green Gate - Fail"
                    
                    # If no message has been sent, then transmit message and set flag
                    if (message != None):
                        print(message)
                        
                        if connection == True:
                            publish.single(topic, message, hostname=server_ip)
                            
                        message_published = True
                
        # When no yellow present, reset and ready for next kayaker/competitor
        elif len(yellow_points) == 0:
            overlaps = None
            message_published = False
            message = None
            previous_position = None
            movement_started_1 = False
            movement_started_2 = False
            crossed_pole = False
            direction_after_crossing = None
            prev_red_area = 0
            prev_green_area = 0
            pole_colour = None
            
    iterations = 0
    while (connection != True) and (iterations < 2):
        connection = check_mqtt(server_ip)
        print("Trying to connect... [",iterations,"]")
        iterations += 1
                
        
    if (connection == True) and (timer_started == False):
        publish.single("Timer", "True", hostname=server_ip)
        timer_started = True
    
    cv2.putText(frame, "Detcting Pole: {}".format(overlaps), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.putText(frame, "Position: {}".format(direction_after_crossing), (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2) #Add Positon Text to Frame Window
    cv2.putText(frame, "Status: {}".format(message), (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2) # Add Status Text to Frame Window
    cv2.imshow('Frame', frame) # Open Frame Window (could be turned off when in use to save processing power)
#     cv2.imshow('Red', red_mask)
#     cv2.imshow('Yellow', yellow_mask)

    # Terminate program when e is pressed
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break


publish.single("Timer", "false", hostname=server_ip)
# Close all windows
video.release()
cv2.destroyAllWindows()
