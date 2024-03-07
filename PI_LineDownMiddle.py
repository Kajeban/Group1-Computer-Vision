import cv2
import numpy as np
import time 

video = cv2.VideoCapture(0)
# video = cv2.VideoCapture('./Photos/reverse_clip.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0009.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0007.mp4')

#video.set(cv2.CAP_PROP_FPS, 1)
#video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# def nothing(x):
#     pass

# Function to check if a point is on the left or right side of the line
def is_left_of_line(point, line_params):
    slope, intercept = line_params
    x, y = point
    return y - (slope * x + intercept) > 0

# cv2.namedWindow("Trackbars")
# 
# cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
# cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("U - H", "Trackbars", 0, 179, nothing)
# cv2.createTrackbar("U - S", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("U - V", "Trackbars", 0, 255, nothing)

frame_counter = 0
direction = None
overlaps = None
prev_centroids = []
prev_red_area = 0
prev_green_area = 0
pass_ = None
pole_colour = None

previous_position = None
movement_started = False
crossed_pole = False
direction_after_crossing = None

# Define range of red color in HSV
lower_red = np.array([160,153,104])
upper_red = np.array([179,255,255])

# Define Red in lab
# lower_red = np.array([152,103,65])
# upper_red = np.array([179,255,161])
    
# Define Purple
#lower_purple = np.array([125, 193, 47])
#upper_purple = np.array([153, 255, 106])

# Define Yellow
lower_yellow = np.array([19, 114, 223])
upper_yellow = np.array([27, 255, 255])

# Define Yellow (Labs)
# lower_yellow = np.array([15, 115, 170])
# upper_yellow = np.array([110, 255, 211])

# Define Green
lower_green = np.array([33, 77, 93]) #HSV Values for Green (Lower End)
upper_green = np.array([92, 255, 255]) #HSV Values for Green (Upper End) 

while(1):
    # Convert BGR to HSV
    
    ret, frame = video.read() #Read Pi Camera

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
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

    frame = cv2.GaussianBlur(frame, (5,5), 0)
    
#     frame_counter += 1
# 
#     if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
#         frame_counter = 0
#         video.set(cv2.CAP_PROP_POS_FRAMES, 0)

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
    
    green_points = []
    for green in green_contours:
        for point in green:
            green_points.append(point[0])
    
    yellow_points = []
    for yellow in yellow_contours:
        for point in yellow:
            yellow_points.append(point[0])

#     red_area = sum(cv2.contourArea(contour) for contour in red_contours)
    green_area = sum(cv2.contourArea(contour) for contour in green_contours)
    
    if (len(red_points) >= 10) or (len(green_points) >= 10):
        
        if len(red_points) > len(green_points):
            pole_colour = "Red"
            [vx, vy, x, y] = cv2.fitLine(np.array(red_points), cv2.DIST_L2, 0, 0.01, 0.01)
            red_area = sum(cv2.contourArea(contour) for contour in red_contours)
        elif len(green_points) >= len(red_points):
            pole_colour = "Green"
            [vx, vy, x, y] = cv2.fitLine(np.array(green_points), cv2.DIST_L2, 0, 0.01, 0.01)
            green_area = sum(cv2.contourArea(contour) for contour in green_contours)
            
        # Fit a line to the red point
#         [vx, vy, x, y] = cv2.fitLine(np.array(red_points if pole_colour == "Red" else green_points, dtype=np.int64), cv2.DIST_L2, 0, 0.01, 0.01)
        slope = vy / vx
        intercept = y - (slope * x)

        # Calculate endpoints of the line to draw
        height, width, _ = frame.shape
        x1 = 0
        y1 = (slope * x1 + intercept).item()
        x2 = width - 1
        y2 = (slope * x2 + intercept).item()
        
        y1 = max(min(y1, 2147483647), -2147483647)
        y2 = max(min(y2, 2147483647), -2147483647)

        # Draw the line
        cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        direction = "Not in Frame"
        # Check if any purple contour intersects the line
        if len(yellow_points) >= 2:
            for yellow in yellow_contours:
                    
                # Calculate the centroid of the contour
                M = cv2.moments(yellow)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroid = (cx, cy)

                    # Check if the centroid is on the left or right side of the line
                    if is_left_of_line(centroid, (slope, intercept)):
                        direction = "Left"
                    else:
                        direction = "Right"
                        
                    if not movement_started:
                        if is_left_of_line(centroid, (slope, intercept)):
                            movement_started = True
                    else:
                        if not crossed_pole:
                            if not is_left_of_line(previous_position, (slope, intercept)) and is_left_of_line(centroid, (slope, intercept)):
                                crossed_pole = True
                    
                    previous_position = centroid
                    
                    if crossed_pole and direction_after_crossing is None:
                        if is_left_of_line(centroid, (slope, intercept)):
                            direction_after_crossing = "Left"
                        
                        else:
                            direction_after_crossing = "Right"
                            
                        if (pole_colour == "Green"):
                            if green_area < prev_green_area * 0.7:
                                overlaps = ("Intersects")
                                
                            prev_green_area = green_area
                            
                        elif (pole_colour == "Red"):
                            if red_area < prev_red_area * 0.7:
                                overlaps = ("Intersects")
                            
                            prev_red_area = red_area
                            
    if direction_after_crossing:
        print(direction_after_crossing)
        if ((overlaps == "Intersects") and (direction_after_crossing == "Left")):
            pass_ = "Gate Successfully Negotiated"
    
    cv2.putText(frame, "Detcting Pole: {}".format(pole_colour), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.putText(frame, "Position: {}".format(direction), (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.putText(frame, "Status: {}".format(pass_), (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.imshow('Frame', frame)
    cv2.imshow('Green', yellow_mask)
    
    
    direction_after_crossing = None
    overlaps = None
    
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break
    
# Close all windows
video.release()
cv2.destroyAllWindows()
