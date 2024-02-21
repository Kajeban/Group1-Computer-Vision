import cv2
import numpy as np

camera = cv2.VideoCapture(0) #Open Pi Camera
direction1 = ""

prev_centroid = None
prev_cX = None

def point_position(x, y, x1, y1, x2, y2):
    return ((x2 - x1) * (y - y1) - (y2-y1) * (x - x1)) > 0

while(1):
    
    ret, frame = camera.read() #Read Pi Camera
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Convert to HSV colour range
    
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    #laplacian = cv2.Laplacian(blurred_frame, cv2.CV_64F)
    
    canny = cv2.Canny(blurred_frame, 100, 150)
    edge_contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Define Red
    lower_red_boundary = np.array([161, 155, 84]) #HSV Values for Red (Lower End)
    upper_red_boundary = np.array([179, 255, 255]) #HSV Values for Red (Upper End)    
    red_mask = cv2.inRange(hsv, lower_red_boundary, upper_red_boundary) #Mask Red in Live View    
    red = cv2.bitwise_and(frame, frame, mask=red_mask) #combines two shades
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if (contours):
        x1, y1, w1, h1 = cv2.boundingRect(edge_contours[0])
        
        pole_center_x = x1 + w1 // 2
        pole_center_y = y1 + h1 // 2
        
        for contour in contours[1:]:
            M = cv2.moments(contour)
        
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                if point_position(cX, cY, pole_center_x, pole_center_y, frame.shape[1] // 2, pole_center_y):
                    direction1 = ("Right of Pole")
                else:
                    direction1 = ("Left of Pole")
                    
        else:
            direction1 = ("No Red")
            
        cv2.putText(frame, direction1, (50, 50), cv2.FONT_ITALIC, 2, (0,0,255), 1)
    
    #cv2.imshow("Laplacian", laplacian)
    cv2.imshow('Live Feed', frame)
    cv2.imshow("Canny", canny)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
# Close all windows
camera.release()
cv2.destroyAllWindows()

