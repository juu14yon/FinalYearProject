
import cv2
import pygame

ESCAPE_KEY = 27

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

cap = cv2.VideoCapture(cv2.CAP_DSHOW)

screen_resolution=(1280,720)
video_resolution=(1280,720)


pygame.init()
screen = pygame.display.set_mode((600, 480))

screen_resolution = (1366, 768)

# Save old eye coordinates if could not detect eyes
old_left = [0, 0, 1, 1]
old_right = [0, 0, 1, 1]

while 1:
    _, frame = cap.read()
    frame = cv2.flip(frame,1)
    cv2.imshow("Main", frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        # make sure it is the main face
        if w < video_resolution[0] < 50 or h < video_resolution[1]//4:
            continue

        face_middle_x, face_middle_y = x+w//2, y+h//2
        roi_color = frame[y:y+h, x:x+w]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 5)
        cv2.imshow("Face", roi_color)
        
        roi_gray_left = gray[y:face_middle_y, x:face_middle_x]
        roi_gray_right = gray[y:face_middle_y, face_middle_x:x+w]

        eye_left = eye_cascade.detectMultiScale(roi_gray_left, 1.3, 5)
        eye_right = eye_cascade.detectMultiScale(roi_gray_right, 1.3, 5)

        # try:
        #     left_x, left_y, left_w, left_h = eye_left[0]
        #     frame_left = roi_gray_left[left_y:left_y + left_h, left_x:left_x + left_w]
        #     cv2.imshow('Left', frame_left)
        # except:
        #     print("No Left")

        # try:
        #     right_x, right_y, right_w, right_h = eye_right[0]
        #     frame_right = roi_gray_right[right_y:right_y + right_h, right_x:right_x + right_w]
        #     cv2.imshow('Right', frame_right)
        # except:
        #     print("No Right")

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

        
        frame_left = roi_gray_left[left_y:min(left_y + left_h, h//2), left_x:min(left_x + left_w, w//2)]
        cv2.imshow('Left eye', frame_left)
        frame_right = roi_gray_right[right_y:min(right_y + right_h, h//2), right_x:min(right_x + right_w, w//2)]
        cv2.imshow('Right eye', frame_right)

    key_pressed = cv2.waitKey(1) & 0xff
    if key_pressed == ESCAPE_KEY:
        break


pygame.display.quit()
cap.release()
cv2.destroyAllWindows()