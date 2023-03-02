import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

img = cv2.imread('data/2023-02-21_22-59-53/first/6.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
kernel = np.ones((5, 5), np.uint8)

def irisFinder(img):
    #blur = cv2.GaussianBlur(img, (3, 3), 0)
    edges = cv2.Canny(img, 80, 255, apertureSize=3)
    cv2.imshow("Edges", edges)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    ellipse = None
    for contour in contours:
        if len(contour) >= 10:
            ellipse = cv2.fitEllipse(contour)
            if 0.5 < ellipse[1][0] / ellipse[1][1] < 2:
                break
    return ellipse

def brightness(image):
    alpha = 1.5 # Simple contrast control 1.0-3.0
    beta = 50   # Simple brightness control 0-100
    new_image = np.zeros(image.shape, image.dtype)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            new_image[y,x] = np.clip(alpha*image[y,x] + beta, 0, 255)

    return new_image


faces = face_cascade.detectMultiScale(gray, 1.3, 5)

for (xFace, yFace, wFace, hFace) in faces:
    face_middle_x, face_middle_y = xFace + wFace//2, yFace + hFace//2
    roi_color = gray[yFace:yFace+hFace, xFace:xFace+wFace]
    cv2.rectangle(gray, (xFace, yFace), (xFace + wFace, yFace + hFace), (255, 0, 0), 5)
    cv2.imshow("Face", roi_color)
    
    roi_gray_left = gray[yFace:face_middle_y, xFace:face_middle_x]
    roi_gray_right = gray[yFace:face_middle_y, face_middle_x:xFace+wFace]

    eye_left = eye_cascade.detectMultiScale(roi_gray_left, 1.3, 5)
    eye_right = eye_cascade.detectMultiScale(roi_gray_right, 1.3, 5)

    try:
        left_x, left_y, left_w, left_h = eye_left[0]
        if left_w==0 or left_h==0:
            left_x, left_y, left_w, left_h = old_left
        else:
            old_left = [left_x, left_y, left_w, left_h]
    except:
        print("No Left")
        left_x, left_y, left_w, left_h = old_left

    try:
        right_x, right_y, right_w, right_h = eye_right[0]
        if right_w==0 or right_h==0:
            right_x, right_y, right_w, right_h = old_right
        else:
            old_right = [right_x, right_y, right_w, right_h]
    except:
        print("No Right")
        right_x, right_y, right_w, right_h = old_right
    
    frame_left = roi_gray_left[left_y:min(left_y + left_h, hFace//2), left_x:min(left_x + left_w, wFace//2)]
    frame_left = brightness(frame_left)
    ellipse = irisFinder(frame_left)
    cv2.ellipse(frame_left, ellipse, (0, 255, 0), 2)
    cv2.imshow('Left eye', frame_left)

    frame_right = roi_gray_right[right_y:min(right_y + right_h, hFace//2), right_x:min(right_x + right_w, wFace//2)]
    frame_right = brightness(frame_right)
    ellipse = irisFinder(frame_right)
    cv2.ellipse(frame_right, ellipse, (0, 255, 0), 2)
    cv2.imshow('Right eye', frame_right)

cv2.waitKey(0)
cv2.destroyAllWindows()
