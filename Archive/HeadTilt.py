import cv2
import mediapipe as mp
import numpy as np

class HeadTilt:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_faces=1)
        self.dist_matrix = np.zeros((4, 1), dtype=np.float64)
        self.kernel = np.ones((3, 3), np.uint8)
        self.center_left = np.array([[29.05], [32.7], [-39.5]])
        self.center_right = np.array([[-29.05], [32.7], [-39.5]])

        self.model_points = np.array([
            (0.0, 0.0, 0.0),  # Nose
            (43.3, 32.7, -26),  # Right eye outer corner
            (28.9, -28.9, -24.1),  # Right mouth corner
            (0, -63.6, -12.5),  # Chin
            (-43.3, 32.7, -26),  # Left eye outer corner
            (-28.9, -28.9, -24.1)  # Left mouth corner
        ])
        self.left_iris_index = [469, 470, 471, 472]
        self.right_iris_index = [474, 475, 476, 477]

        self.img_h, self.img_w, self.img_c = 0, 0, 0
        self.face_3d = []
        self.face_2d = []
        self.face_plane = []

        self.left_iris = []
        self.right_iris = []

        self.left_eye_top = 0
        self.left_eye_bottom = 1
        self.right_eye_top = 0
        self.right_eye_bottom = 1
        self.left_eye_outer = (0, 0)
        self.left_eye_inner = (1, 1)
        self.right_eye_outer = (0, 0)
        self.right_eye_inner = (1, 1)

    def start(self, frame):
        # add frame.flags.writeable = False
        self.results = self.face_mesh.process(frame)
        # add frame.flags.writeable = True

        self.img_h, self.img_w, self.img_c = frame.shape
        self.face_3d = []
        self.face_2d = []
        self.face_plane = []

        self.left_iris = []
        self.right_iris = []

        focal_length = 1 * self.img_w

        self.cam_matrix = np.array([ 
            [focal_length, 0, self.img_h / 2],
            [0, focal_length, self.img_w / 2],
            [0, 0, 1]
            ])

        

    def angles(self):
        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                self.left_pupil = (int(face_landmarks.landmark[468].x * self.img_w), int(face_landmarks.landmark[468].y * self.img_h))
                self.right_pupil = (int(face_landmarks.landmark[473].x * self.img_w), int(face_landmarks.landmark[473].y * self.img_h))

                for i in self.left_iris_index:
                    self.left_iris.append((face_landmarks.landmark[i].x * self.img_w, face_landmarks.landmark[i].y) * self.img_h)
                for i in self.right_iris_index:
                    self.right_iris.append((face_landmarks.landmark[i].x * self.img_w, face_landmarks.landmark[i].y) * self.img_h)

                self.left_eye_top = int(face_landmarks.landmark[263].y * self.img_h - 20)
                self.left_eye_bottom = int(face_landmarks.landmark[362].y * self.img_h + 10)
                self.right_eye_top = int(face_landmarks.landmark[33].y * self.img_h - 20)
                self.right_eye_bottom = int(face_landmarks.landmark[133].y * self.img_h + 10)

                self.left_eye_outer = (int(face_landmarks.landmark[263].x * self.img_w), int(face_landmarks.landmark[263].y * self.img_h))
                self.left_eye_inner = (int(face_landmarks.landmark[362].x * self.img_w), int(face_landmarks.landmark[362].y * self.img_h))
                self.right_eye_outer = (int(face_landmarks.landmark[33].x * self.img_w), int(face_landmarks.landmark[33].y * self.img_h))
                self.right_eye_inner = (int(face_landmarks.landmark[133].x * self.img_w), int(face_landmarks.landmark[133].y * self.img_h))

                for idx, lm in enumerate(face_landmarks.landmark):
                    # if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx in {4, 33, 57, 152, 263, 287}:
                        lmh, lmv = lm.x * self.img_w, lm.y * self.img_h
                        if idx == 4:
                            nose_2d = (lmh, lmv)
                            nose_3d = (lmh, lmv, lm.z * 8000)

                        x, y = int(lmh), int(lmv)

                        self.face_2d.append([x, y])
                        self.face_plane.append([x, y, 0])
                        self.face_3d.append([x, y, lm.z])

                self.face_2d = np.array(self.face_2d, dtype=np.float64)
                self.face_plane = np.array(self.face_plane, dtype=np.float64)
                self.face_3d = np.array(self.face_3d, dtype=np.float64)

                # _, self.rot_vec, self.trans_vec = cv2.solvePnP(self.face_3d, self.face_2d, self.cam_matrix, self.dist_matrix)
                _, self.rot_vec, self.trans_vec = cv2.solvePnP(self.model_points, 
                                                               self.face_2d, 
                                                               self.cam_matrix, 
                                                               self.dist_matrix
                                                               )
                _, self.img2world, _ = cv2.estimateAffine3D(self.face_plane, self.model_points)

                # Get rotational matrix
                rmat, jac = cv2.Rodrigues(self.rot_vec)

                # Get angles
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                y = -angles[0] * 360
                x = -angles[1] * 360

            return True, round(x, 3), round(y, 3)
        else:
            return False, 0, 0
        
    def draw(self, frame):
        mp_drawing = mp.solutions.drawing_utils
        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1))
        return frame
    
    def gaze(self, d):
        if self.img2world is not None:
            left_pupil_world = self.img2world @ np.array([[self.left_pupil[0], self.left_pupil[1], 0, 1]]).T
            right_pupil_world = self.img2world @ np.array([[self.right_pupil[0], self.right_pupil[1], 0, 1]]).T
            leftCoords = self.center_left + (left_pupil_world - self.center_left) * d
            rightCoords = self.center_right + (right_pupil_world - self.center_right) * d

            leftp1, leftp2 = self.vector(self.left_pupil, leftCoords, left_pupil_world)
            rightp1, rightp2 = self.vector(self.right_pupil, rightCoords, right_pupil_world)

            return leftp1, leftp2, rightp1, rightp2
        return 0, 0, 0, 0
            
    def vector(self, pupil, coords, worldsCoords):
        (eye_pupil2D, _) = cv2.projectPoints((int(coords[0]), int(coords[1]), int(coords[2])), self.rot_vec,
                                            self.trans_vec, self.cam_matrix, self.dist_matrix)
        (head_pose, _) = cv2.projectPoints((int(worldsCoords[0]), int(worldsCoords[1]), int(40)),
                                        self.rot_vec, self.trans_vec, self.cam_matrix, self.dist_matrix)
        gaze = pupil + (eye_pupil2D[0][0] - pupil) - (head_pose[0][0] - pupil)

        p1 = (int(pupil[0]), int(pupil[1]))
        p2 = (int(gaze[0]), int(gaze[1]))

        return p1, p2
    

    def brightness(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.dilate(cv2.erode(image, self.kernel), self.kernel)
        # image = cv2.equalizeHist(image)
        alpha = 1.6 # Simple contrast control 1.0-3.0
        beta = 50   # Simple brightness control 0-100
        new_image = np.zeros(image.shape, image.dtype)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                new_image[y,x] = np.clip(alpha*image[y,x] + beta, 0, 255)
        # cv2.imshow("Filter", new_image)
        return new_image
    
    def irisFinder(self, iris):
        landmark_distances = []
        if iris == "L":
            iris_landmarks = self.left_iris
        else:
            iris_landmarks = self.right_iris

        for i in range(4):
            for j in range(i+1, 4):
                distance = ((iris_landmarks[i][0] - iris_landmarks[j][0])**2 
                            + (iris_landmarks[i][1] - iris_landmarks[j][1])**2)**0.5
                landmark_distances.append(distance)

        return int(max(landmark_distances))
    
        # img = self.brightness(img)
        # height, width = img.shape
        # h41, h42, v41, v42 = 10, width - 10, 20, height - 10

        # # Apply Hough circles transform to detect iris boundary
        # circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, width//2, param1=30, param2=5, minRadius=(width - 20)//7, maxRadius=(width - 20)//5)
        # if circles is not None:
        #     circles = np.round(circles[0, :]).astype("int")
        #     for i in circles:
        #         x, y, r = i
        #         # Select only circle with center at dark pixel close to the image center
        #         if x<h41 or x>h42 or y<v41 or y>v42:
        #             continue

        #         # if img[y][x] > 200:
        #         #     continue

        #         return x, y, r
        # else:
        #     print("No circles found")
        #     return 0, 0, 1
        
        # return 0, 0, 1

    