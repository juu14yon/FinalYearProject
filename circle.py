import cv2
import numpy as np

WIDTH, HEIGHT = 640, 480

# Default classifiers for detecting frontal face and eyes
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

kernel = np.ones((3, 3), np.uint8)
old_left = [0, 0, 10, 10]
old_right = [0, 0, 10, 10]

# Finds edges (contours) in image, selects one that is more likely to be an iris
# Return ellipse that matches iris' shape
def irisFinder(img, c):
    height, width = img.shape
    h41, h42, v41, v42 = width//4, width - width//4, height//4, height - height//4

    # Apply Hough circles transform to detect iris boundary
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, width//2, param1=30, param2=5, minRadius=5, maxRadius=height//5)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for i in circles:
            x, y, r = i
            # Select only circle with center at dark pixel close to the image center
            if x<h41 or x>h42 or y<v41 or y>v42:
                continue
            if img[y][x]>125:
                continue
            
            # Draw circle and its center
            cv2.circle(img, (x, y), r, (0, 255, 0), 1)
            cv2.circle(img, (x, y), 1, (0, 0, 255), 1)
    else:
        print("No circles found")

    cv2.imshow("Eye" + c, img)


# Changes brightness and contrast of image
# Intended to use for making dark iris more visible and smooth out skin
def brightness(image):
    image = cv2.dilate(cv2.erode(image, kernel), kernel)
    image = cv2.equalizeHist(image)
    alpha = 1.2 # Simple contrast control 1.0-3.0
    beta = 50   # Simple brightness control 0-100
    new_image = np.zeros(image.shape, image.dtype)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            new_image[y,x] = np.clip(alpha*image[y,x] + beta, 0, 255)
    return new_image

# Start web camera
capture = cv2.VideoCapture(cv2.CAP_DSHOW)

while True:
    # Get frame from webcam, convert to grayscale, find a face
    _, img = capture.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (xFace, yFace, wFace, hFace) in faces:
        if wFace < WIDTH//4 or hFace < HEIGHT // 4:
            continue
        
        xFaceMid, yFaceMid = xFace + wFace//2, yFace + hFace//2
        roi_color = gray[yFace:yFace+hFace, xFace:xFace+wFace]
        cv2.rectangle(gray, (xFace, yFace), (xFace + wFace, yFace + hFace), (255, 0, 0), 5)
        cv2.imshow("Face", roi_color)
        
        # Split face in upper quarters and look for eyes
        roi_gray_left = gray[yFace:yFaceMid, xFace:xFaceMid]
        roi_gray_right = gray[yFace:yFaceMid, xFaceMid:xFace+wFace]

        eye_left = eye_cascade.detectMultiScale(roi_gray_left, 1.3, 5)
        eye_right = eye_cascade.detectMultiScale(roi_gray_right, 1.3, 5)

        # Get eyes' coordinates or use old coordinates if cannot find eyes
        try:
            left_x, left_y, left_w, left_h = eye_left[0]
            if left_w==0 or left_h==0:
                left_x, left_y, left_w, left_h = old_left
            else:
                old_left = [left_x, left_y, left_w, left_h]

            right_x, right_y, right_w, right_h = eye_right[0]
            if right_w==0 or right_h==0:
                right_x, right_y, right_w, right_h = old_right
            else:
                old_right = [right_x, right_y, right_w, right_h]
        except:
            print("No eyes or blink")
            left_x, left_y, left_w, left_h = old_left
            right_x, right_y, right_w, right_h = old_right

        # Apply filter to eye image, find iris, and draw it 
        frame_left = roi_gray_left[left_y:min(left_y + left_h, hFace//2), left_x:min(left_x + left_w, wFace//2)]
        frame_left = brightness(frame_left)
        irisFinder(frame_left, "L")

        frame_right = roi_gray_right[right_y:min(right_y + right_h, hFace//2), right_x:min(right_x + right_w, wFace//2)]
        frame_right = brightness(frame_right)
        irisFinder(frame_right, "R")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        capture.release()
        break

cv2.destroyAllWindows()
