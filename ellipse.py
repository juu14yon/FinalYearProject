import cv2
import numpy as np

# Default classifiers for detecting frontal face and eyes
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

kernel = np.ones((3, 3), np.uint8)
old_left = [0, 0, 1, 1]
old_right = [0, 0, 1, 1]

# Finds edges (contours) in image, selects one that is more likely to be an iris
# Return ellipse that matches iris' shape
def irisFinder(img, c):
    blur = cv2.GaussianBlur(img, (3, 3), 0)
    edges = cv2.Canny(blur, 1, 255, apertureSize=5)
    cv2.imshow("Edges" + c, edges)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    ellipse = None
    for contour in contours:
        if len(contour) >= 10:
            ellipse = cv2.fitEllipse(contour)
            if max(ellipse[1]) < img.shape[0]//4:
                continue
            else:
                if 0.5 < ellipse[1][0] / ellipse[1][1] < 2:
                    break
    return ellipse

# Changes brightness and contrast of image
# Intended to use for making dark iris more visible and smooth out skin
def brightness(image):
    image = cv2.dilate(cv2.erode(image, kernel), kernel)
    alpha = 1.5 # Simple contrast control 1.0-3.0
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
        ellipse = irisFinder(frame_left, "L")
        cv2.ellipse(frame_left, ellipse, (0, 255, 0), 1)
        cv2.imshow('Left eye', frame_left)

        frame_right = roi_gray_right[right_y:min(right_y + right_h, hFace//2), right_x:min(right_x + right_w, wFace//2)]
        frame_right = brightness(frame_right)
        ellipse = irisFinder(frame_right, "R")
        cv2.ellipse(frame_right, ellipse, (0, 255, 0), 1)
        cv2.imshow('Right eye', frame_right)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        capture.release()
        break

cv2.destroyAllWindows()
