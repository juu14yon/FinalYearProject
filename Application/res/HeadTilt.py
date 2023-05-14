import cv2
import mediapipe as mp
import numpy as np
from scipy.ndimage import gaussian_filter1d
from math import sqrt, acos

# Distortion matrix
dist_matrix = np.zeros((4, 1), dtype=np.float64)

# Initialize the Gaussian filter parameters
sigma = 3
window_size = 5

# 'Ideal' facemesh coordinates
center_left = np.array([[29.05], [32.7], [-30]])
center_right = np.array([[-29.05], [32.7], [-30]])
model_points = np.array([
    [0.0, 0.0, 0.0],  # Nose
    [43.3, 32.7, -26],  # Right eye outer corner
    [28.9, -28.9, -24.1],  # Right mouth corner
    [0, -63.6, -12.5],  # Chin
    [-43.3, 32.7, -26],  # Left eye outer corner
    [-28.9, -28.9, -24.1]  # Left mouth corner
])

# Landmark indices
core_indices = {33, 159, 158, 145, 153, 133, 468, 469, 470, 471, 472, 263, 386, 385, 374, 380, 362, 473, 474, 475, 476, 477, 6, 1, 10, 152, 284, 454, 397, 54, 234, 172}
left_iris_index = [469, 470, 471, 472]
right_iris_index = [474, 475, 476, 477]

class HeadTilt:
    def __init__(self):
        # Loading mediapipe FaceMesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_faces=1)
        self.img_h, self.img_w, self.img_c = 0, 0, 0

        # Initialize the landmark buffer
        self.landmarks_buffer = []
        self.vector_buffer = []
        self.core_coords = []

        # Placeholders
        self.left_iris = []
        self.right_iris = []
        self.left_eye_top = (0, 0)
        self.left_eye_bottom = (1, 1)
        self.right_eye_top = (0, 0)
        self.right_eye_bottom = (1, 1)
        self.left_eye_outer = (0, 0)
        self.left_eye_inner = (1, 1)
        self.right_eye_outer = (0, 0)
        self.right_eye_inner = (1, 1)

        self.isFace = False

    def start(self, frame):
        # add frame.flags.writeable = False
        self.results = self.face_mesh.process(frame)
        # add frame.flags.writeable = True

        self.img_h, self.img_w, self.img_c = frame.shape

        # Clear lists
        self.core_coords = []
        self.face_3d = []
        self.face_2d = []
        self.face_plane = []
        self.left_iris = []
        self.right_iris = []

        self.isFace = False

        # Camera matrix
        focal_length = 1 * self.img_w
        self.cam_matrix = np.array([ 
            [focal_length, 0, self.img_w / 2],
            [0, focal_length, self.img_h / 2],
            [0, 0, 1]
            ])


    def angles(self):
        if self.results.multi_face_landmarks:
            self.isFace = True # There is a face
            for face_landmarks in self.results.multi_face_landmarks:
                # Gaussian smoothing for landmarks to reduce jitter
                landmarks = np.array([[face_landmarks.landmark[i].x, face_landmarks.landmark[i].y, face_landmarks.landmark[i].z] for i in range(478)])
                self.landmarks_buffer.append(landmarks)
                landmarks_smoothed = gaussian_filter1d(np.array(self.landmarks_buffer), sigma=sigma, axis=0)
                if len(self.landmarks_buffer) >= window_size:
                    self.landmarks_buffer.pop(0)

                # Smoothed out landmarks
                lm_smooth = landmarks_smoothed[-1]

                # Get pupils and eyes coordinates (relative coordinates)
                self.left_pupil = (lm_smooth[468][0] * self.img_w, lm_smooth[468][1] * self.img_h)
                self.right_pupil = (lm_smooth[473][0] * self.img_w, lm_smooth[473][1] * self.img_h)

                for i in left_iris_index:
                    self.left_iris.append((lm_smooth[i][0] * self.img_w, lm_smooth[i][1]) * self.img_h)
                for i in right_iris_index:
                    self.right_iris.append((lm_smooth[i][0] * self.img_w, lm_smooth[i][1]) * self.img_h)
                    
                self.right_eye_top = (lm_smooth[386][0] * self.img_w, lm_smooth[386][1] * self.img_h)
                self.right_eye_bottom = (lm_smooth[374][0] * self.img_w, lm_smooth[374][1] * self.img_h)
                self.left_eye_top = (lm_smooth[159][0] * self.img_w, lm_smooth[159][1] * self.img_h)
                self.left_eye_bottom = (lm_smooth[145][0] * self.img_w, lm_smooth[145][1] * self.img_h)

                self.right_eye_outer = (lm_smooth[263][0] * self.img_w, lm_smooth[263][1] * self.img_h)
                self.right_eye_inner = (lm_smooth[362][0] * self.img_w, lm_smooth[362][1] * self.img_h)
                self.left_eye_outer = (lm_smooth[33][0] * self.img_w, lm_smooth[33][1] * self.img_h)
                self.left_eye_inner = (lm_smooth[133][0] * self.img_w, lm_smooth[133][1] * self.img_h)

                # Save necessary landmarks (relative coordinates)
                for id, lm in enumerate(lm_smooth):
                    if id in core_indices:
                        lmx_rel, lmy_rel = lm[0] * self.img_w, lm[1] * self.img_h
                        self.core_coords.append(lmx_rel)
                        self.core_coords.append(lmy_rel)

                    if id in {4, 33, 57, 152, 263, 287}:
                        lmx_rel, lmy_rel = lm[0] * self.img_w, lm[1] * self.img_h
                        x, y = int(lmx_rel), int(lmy_rel)

                        self.face_2d.append([x, y])
                        self.face_plane.append([x, y, 0])
                        self.face_3d.append([x, y, lm[2]])

                self.face_2d = np.array(self.face_2d, dtype=np.float64)
                self.face_plane = np.array(self.face_plane, dtype=np.float64)
                self.face_3d = np.array(self.face_3d, dtype=np.float64)

                # Calculate rotation and translation of FaceMesh
                _, self.rot_vec, self.trans_vec = cv2.solvePnP(model_points, 
                                                               self.face_2d, 
                                                               self.cam_matrix, 
                                                               dist_matrix,
                                                               flags=cv2.SOLVEPNP_ITERATIVE)
                _, self.img2world, _ = cv2.estimateAffine3D(self.face_plane, model_points)
                rmat, _ = cv2.Rodrigues(self.rot_vec)
                transMat = np.hstack((rmat, self.trans_vec.reshape(3, 1)))
                self.transMat = np.vstack((transMat, np.array([0, 0, 0, 1])))

                # Face rotation angles (yaw - L/R, pitch - U/D, roll)
                angles, R, Q, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                y = -angles[0]
                x = -angles[1]
                z = -angles[2]
            return True, round(x, 3), round(y, 3)
        else:
            return False, 0, 0
        
    def draw(self, frame):
        # Draw FaceMesh (without Gaussian smoothing)
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
        if self.isFace and (self.img2world is not None):
            # World coodinates for pupils
            left_pupil_world = self.img2world @ np.array([[self.left_pupil[0], self.left_pupil[1], 0, 1]]).T
            right_pupil_world = self.img2world @ np.array([[self.right_pupil[0], self.right_pupil[1], 0, 1]]).T
            # World coordinates for vectors
            lEyeVec = (left_pupil_world - center_left)
            rEyeVec = (right_pupil_world - center_right)
            leftCoords = center_left + lEyeVec * 11
            rightCoords = center_right + rEyeVec * 11

            # leftCoords[2] = min(12, leftCoords[2])
            # rightCoords[2] = min(12, rightCoords[2])

            self.vecLeft = leftCoords.flat
            self.vecRight = rightCoords.flat

            # Vectors' projections
            leftp1, leftp2 = self.vector(self.left_pupil, leftCoords, left_pupil_world, d)
            rightp1, rightp2 = self.vector(self.right_pupil, rightCoords, right_pupil_world, d)

            # Unit vector projections
            # vecLeft = leftp2 - leftp1
            # self.vecLeft = vecLeft/np.linalg.norm(vecLeft)
            # vecRight = rightp2 - rightp1
            # self.vecRight = vecRight/np.linalg.norm(vecRight)


            # Smoothing to reduce the jitter
            self.vector_buffer.append([leftp2, rightp2])
            vector_smoothed = gaussian_filter1d(np.array(self.vector_buffer), sigma=sigma, axis=0)
            if len(self.vector_buffer) >= window_size:
                self.vector_buffer.pop(0)

            return (int(leftp1[0]), int(leftp1[1])), (int(vector_smoothed[-1][0][0]), int(vector_smoothed[-1][0][1])), (int(rightp1[0]), int(rightp1[1])), (int(vector_smoothed[-1][1][0]), int(vector_smoothed[-1][1][1]))
        return [0], [0], [0], [0]
            
    def vector(self, pupil, coords, worldsCoords, d):
        if self.isFace:
            (eye_pupil2D, _) = cv2.projectPoints((int(coords[0]), int(coords[1]), int(coords[2])), self.rot_vec,
                                                self.trans_vec, self.cam_matrix, dist_matrix)
            (head_pose, _) = cv2.projectPoints((int(worldsCoords[0]), int(worldsCoords[1]), d),
                                            self.rot_vec, self.trans_vec, self.cam_matrix, dist_matrix)
            gaze = pupil + (eye_pupil2D[0][0] - pupil) - (head_pose[0][0] - pupil)

            p1 = pupil
            p2 = gaze

            return p1, p2
        else:
            return 0, 0
    
    def diameter(self, iris):
        if self.isFace:
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
        else:
            return 0
        

    # Eye center and pupil displacement angles
    # def eyeCenter(self, top, bottom, out, inn, pupil, frame):
    #     left_d = self.diameter("L")
    #     right_d = self.diameter("R")
    #     irisDiam = max(left_d, right_d)

    #     center = [0, 0]
    #     m2 = (out[1] - inn[1])/(out[0] - inn[0])
    #     b2 = - out[0] * m2 + out[1]
    #     try:
    #         m1 = (top[1] - bottom[1])/(top[0] - bottom[0])
    #         b1 = - top[0] * m1 + top[1]
    #         center[0] = (b2 - b1)/(m1 - m2)
    #     except:
    #         center[0] = top[0]
        
    #     center[1] = center[0] * m2 + b2

    #     # cv2.circle(frame, (int(center[0]), int(center[1])), 1, (255, 255, 255), 1)
    #     vertical = ((out[0] - inn[0])*(inn[1] - pupil[1]) - (out[1] - inn[1])*(inn[0] - pupil[0]))/sqrt((out[0] - inn[0])**2 + (out[1] - inn[1])**2)
    #     horiz = ((top[0] - bottom[0])*(bottom[1] - pupil[1]) - (top[1] - bottom[1])*(bottom[0] - pupil[0]))/sqrt((top[0] - bottom[0])**2 + (top[1] - bottom[1])**2)
    #     ratio = 1/(irisDiam*irisDiam*2)

    #     vertical = vertical*vertical*ratio
    #     horiz = horiz*horiz*ratio

    #     alpha = acos(1 - vertical)
    #     beta = acos(1 - horiz)

    #     if vertical<0:
    #         alpha *= -1
    #     if horiz<0:
    #         beta *= -1

    #     return alpha*180, beta*180