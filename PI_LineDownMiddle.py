import cv2
import numpy as np
import time 

video = cv2.VideoCapture(0)
#video = cv2.VideoCapture('./Photos/reverse_clip.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0009.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0007.mp4')

#video.set(cv2.CAP_PROP_FPS, 1)
#video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def nothing(x):
    pass

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
direction = ""
overlaps = ""
prev_centroids = []

# Define range of red color in HSV
lower_red = np.array([160,153,104])
upper_red = np.array([179,255,255])
    
# Define Purple
#lower_purple = np.array([125, 193, 47])
#upper_purple = np.array([153, 255, 106])

# Define Yellow
lower_yellow = np.array([19, 110, 186])
upper_yellow = np.array([47, 255, 255])

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
    
    frame_counter += 1

    if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
        frame_counter = 0
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Threshold the HSV image to get only red colors
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    #purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Find contours
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Extract red points from contours
    red_points = []
    for red in red_contours:
        for point in red:
            red_points.append(point[0])
    
    yellow_points = []
    for yellow in yellow_contours:
        for point in yellow:
            yellow_points.append(point[0])

    red_area = sum(cv2.contourArea(contour) for contour in red_contours)
    print(red_area)
    
    if len(red_points) >= 2:
        # Fit a line to the red points
        [vx, vy, x, y] = cv2.fitLine(np.array(red_points), cv2.DIST_L2, 0, 0.01, 0.01)
        slope = vy / vx
        intercept = y - (slope * x)

        # Calculate endpoints of the line to draw
        height, width, _ = frame.shape
        x1 = 0
        y1 = int((slope * x1 + intercept).item())
        x2 = width - 1
        y2 = int((slope * x2 + intercept).item())
        
        x1 = max(min(x1, width -1), 0)
        y1 = max(min(y1, height -1), 0)
        x2 = max(min(x2, width -1), 0)
        y2 = max(min(y2, height -1), 0)        

        # Draw the line
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        red_area = sum(cv2.contourArea(contour) for contour in red_contours)
        #red_area = cv2.countNonZero(red_mask)
        #print(red_area)
        
        direction = "Not in Frame"
        # Check if any purple contour intersects the line
        if len(yellow_points) >= 2:
            if (red_area == 0):
                overlaps = "Insersects"
            else:
                overlaps = "No Insersects"
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
    
    cv2.putText(frame, "Position: {}".format(direction), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.putText(frame, "Insersects: {}".format(overlaps), (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.imshow('Frame', frame)
    cv2.imshow('Red Mask', red_mask)
    #cv2.imshow('purple mask', purple_mask)
    cv2.imshow('Yellow Mask', yellow_mask)
    #if overlaps:
        #time.sleep(1)

    
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break
    
# Close all windows
video.release()
cv2.destroyAllWindows()
