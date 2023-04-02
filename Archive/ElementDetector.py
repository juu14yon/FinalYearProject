import cv2
import numpy as np

class ElementsDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        self.WIDTH, self.HEIGHT = 640, 480
        self.kernel = np.ones((3, 3), np.uint8)

        self.old_left = [0, 0, 10, 10]
        self.old_right = [0, 0, 10, 10]
        self.centerLeft, self.radiusLeft = (0, 0), 1
        self.centerRight, self.radiusRight = (0, 0), 1

        self.imageFlag = False
        self.faceFlag = False
        self.eyesFlag = False

    def setImage(self, gray):
        self.gray = gray
        self.imageFlag = True

    def faceData(self):
        if self.imageFlag:
            # Find face
            faces = self.face_cascade.detectMultiScale(self.gray, 1.3, 5)
            for (xFace, yFace, wFace, hFace) in faces:
                if wFace < self.WIDTH//4 or hFace < self.HEIGHT // 4:
                    continue
                xFaceMid, yFaceMid = xFace + wFace//2, yFace + hFace//2

                # Save relative face coordinates and dimensions
                self.xFace, self.yFace, self.wFace, self.hFace, self.xFaceMid, self.yFaceMid = xFace, yFace, wFace, hFace, xFaceMid, yFaceMid
                self.faceFlag = True
                break

        else:
            print("ERROR: No image to start detection")

        self.imageFlag = False

    def eyeData(self):
        if self.faceFlag:
            # Crop face to upper quarters where eyes are most likely to be
            self.face_left = self.gray[self.yFace:self.yFaceMid, self.xFace:self.xFaceMid]
            self.face_right = self.gray[self.yFace:self.yFaceMid, self.xFaceMid:self.xFace+self.wFace]

            # Find eyes
            eye_left = self.eye_cascade.detectMultiScale(self.face_left, 1.3, 5)
            eye_right = self.eye_cascade.detectMultiScale(self.face_right, 1.3, 5)

            # Save eyes' relative coordinates and dimensions
            try:
                left_x, left_y, left_w, left_h = eye_left[0]
                if left_w==0 or left_h==0:
                    self.eyesFlag = False
                else:
                    self.old_left = eye_left[0]
                    self.eyesFlag = True

                right_x, right_y, right_w, right_h = eye_right[0]
                if right_w==0 or right_h==0:
                    self.eyesFlag = False
                else:
                    self.old_right =  eye_right[0]
                    self.eyesFlag = self.eyesFlag and True
            except:
                self.eyesFlag = False

        else:
            print("ERROR: No face found to detect eyes")
        
        self.faceFlag = False

    def irisData(self):
        if self.eyesFlag:
            left_x, left_y, left_w, left_h = self.old_left
            right_x, right_y, right_w, right_h = self.old_right

            # Crop face quarters to eyes
            eyeLeft = self.face_left[left_y:min(left_y + left_h, self.hFace//2), left_x:min(left_x + left_w, self.wFace//2)]
            eyeRight = self.face_right[right_y:min(right_y + right_h, self.hFace//2), right_x:min(right_x + right_w, self.wFace//2)]

            # Find irises and save their relative coordinates and dimensions
            iris = self.irisFinder(eyeLeft, self.centerLeft, self.radiusLeft)
            if iris is not None:
                self.centerLeft, self.radiusLeft = (iris[0], iris[1]), iris[2]
            
            iris = self.irisFinder(eyeRight, self.centerRight, self.radiusRight)
            if iris is not None:
                self.centerRight, self.radiusRight = (iris[0], iris[1]), iris[2]

            # Draw circles estimating irises and show them
            # cv2.circle(eyeLeft, self.centerLeft, self.radiusLeft, (0, 255, 0), 1)
            # cv2.circle(eyeLeft, self.centerLeft, 1, (0, 0, 255), 1)
            # cv2.imshow("Left", eyeLeft)

            # cv2.circle(eyeRight, self.centerRight, self.radiusRight, (0, 255, 0), 1)
            # cv2.circle(eyeRight, self.centerRight, 1, (0, 0, 255), 1)
            # cv2.imshow("Right", eyeRight)

        else:
            print("ERROR: No eye found to detect iris")

        self.eyesFlag = False

    # Changes brightness and contrast of image
    # Intended to use for making dark iris more visible and smooth out skin
    def brightness(self, image):
        image = cv2.dilate(cv2.erode(image, self.kernel), self.kernel)
        image = cv2.equalizeHist(image)
        alpha = 1.2 # Simple contrast control 1.0-3.0
        beta = 50   # Simple brightness control 0-100
        new_image = np.zeros(image.shape, image.dtype)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                new_image[y,x] = np.clip(alpha*image[y,x] + beta, 0, 255)
        return new_image
    
    def irisFinder(self, img, center, radius):
        img = self.brightness(img)
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

                return x, y, r
        else:
            print("No circles found")
            return center[0], center[1], radius
