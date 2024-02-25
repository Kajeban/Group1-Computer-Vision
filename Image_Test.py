import cv2
import numpy as np
import time 

# video = cv2.VideoCapture('./Photos/reverse_clip.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0009.mp4')
#video = cv2.VideoCapture('./Photos/VID-20240223-WA0007.mp4')
image = cv2.imread('./Photos/IMG-20240223-WA0005.jpg')

overlap_detected = False
overlap_start_time = 0

# Define range of red color in HSV
lower_red = np.array([161,155,84])
upper_red = np.array([179,255,255])
    
# Define Purple
lower_purple = np.array([120, 50, 50])
upper_purple = np.array([170, 255, 255])

pole_x = None
pole_y = None


# Convert BGR to HSV
frame = image

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Threshold the HSV image to get only red colors
red_mask = cv2.inRange(hsv, lower_red, upper_red)
purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)

# Find contours
red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Count red stripes
red_stripe_count = 0
for red_contour in red_contours:        
    if cv2.contourArea(red_contour) > 150:
        red_stripe_count += 1
        # Draw contours for visualization
        cv2.drawContours(frame, [red_contour], -1, (0,  255, 0), 2)

purple_binary = np.zeros_like(purple_mask)  
red_binary = np.zeros_like(red_mask)

overlaps = False
for purple_contour in purple_contours:
    cv2.drawContours(purple_binary, [purple_contour], -1, 255, -1)

for red_contour in red_contours:
        # Create binary masks for purple and red contours
        
        cv2.drawContours(red_binary, [red_contour], -1, 255, -1)

        # Perform bitwise AND operation
intersection = cv2.bitwise_and(purple_binary, red_binary)
intersection_area = np.count_nonzero(intersection)

if intersection_area > 50:  # Adjust threshold as needed
    overlaps = True


# Display the result
cv2.putText(frame, "Red Stripes: {}".format(red_stripe_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.putText(frame, "Purple Overlaps Red: {}".format(overlaps), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
cv2.imshow('Stripes and Objects Detection', frame)
#cv2.imshow('Red Mask', red_mask)
#cv2.imshow('purple mask', purple_mask)
#if overlaps:
    #time.sleep(1)

cv2.waitKey(0)
# Close all windows
cv2.destroyAllWindows()
