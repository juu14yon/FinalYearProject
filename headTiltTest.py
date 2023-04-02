import cv2
from math import tan, pi, atan
from HeadTilt import HeadTilt
from ElementDetector import ElementsDetector

def squaredDistance(a, b):
    ax, ay = a
    bx, by = b

    return (ax-bx)**2 + (ay-by)**2

def pointAndLine(a, b, p):
    ax, ay = a
    bx, by = b
    px, py = p

    m = (by-ay)/(bx-ax)
    k = ay - ax*m

    ly = m*px + k

    if ly == py:
        return 0
    elif ly < py:
        return 1
    else:
        return -1


centerx, centery = 1366//2, 768//2
distance = 50 # centimeter
density = 44 # px/cm
maxa, maxb = round(180*atan(16/distance)/pi, 2), round(180*atan(9/distance)/pi, 2)
left_c_x, left_c_y, left_r = 0, 0, 1
right_c_x, right_c_y, right_r = 0, 0, 1


hd = HeadTilt()
ed = ElementsDetector()

# frame = cv2.imread("forHeadAngles/center.jpg")
# screen = cv2.imread("forHeadAngles/screenshot.png")
# cv2.circle(screen, (centerx, centery), 10, (255, 0, 255), 3)

# frame.flags.writeable = False
# hd.start(frame)
# frame.flags.writeable = True

# flag, centera, centerb = hd.angles()
# print("Center:", centerx, centery, centera, centerb)

# frame = hd.draw(frame)

# cv2.circle(frame, hd.left_eye_outer, 1, (255, 0, 0), 2)
# cv2.circle(frame, hd.left_eye_inner, 1, (255, 0, 0), 2)
# cv2.circle(frame, hd.right_eye_outer, 1, (0, 0, 255), 2)
# cv2.circle(frame, hd.right_eye_inner, 1, (0, 0, 255), 2)

# print("Left:", squaredDistance(hd.left_eye_outer, hd.left_eye_inner))
# print("Right:", squaredDistance(hd.right_eye_outer, hd.right_eye_inner))

# cv2.imshow('Eye Corners', frame)
# cv2.waitKey(0)

cap = cv2.VideoCapture("amitt_gaze_tracking/face.mp4")

# for i in range(1, 9):
#     path = "forHeadAngles/batch2/"+ str(i) + ".jpg"
#     frame = cv2.imread(path)

count = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:  # no frame input
        print("Ignoring empty camera frame.")
        count += 1
        if count > 10:
            break

    frame.flags.writeable = False
    hd.start(frame)
    frame.flags.writeable = True

    flag, alpha, beta = hd.angles()

    # print()
    # print("Angles:", alpha, beta)
    # if flag:
    #     da = alpha - centera
    #     db = beta - centerb
    #     if abs(da) >= maxa or abs(db) >= maxb:
    #         print("Off the screen")
    #     else:
    #         dx = distance * tan(da*pi/180) * density
    #         dy = distance * tan(db*pi/180) * density
    #         # print("Offset:", dx, dy)

    #         x, y = int(centerx + dx), int(centery + dy)
    #         print("New coords:", x, y)

    # cv2.circle(screen, (x, y), 30, (255, 255, 0), 3)
    # cv2.imshow("Screen", screen)

    # frame = hd.draw(frame)

    # cv2.circle(frame, hd.left_eye_outer, 1, (255, 0, 0), 2)
    # cv2.circle(frame, hd.left_eye_inner, 1, (255, 0, 0), 2)
    # cv2.circle(frame, hd.right_eye_outer, 1, (0, 0, 255), 2)
    # cv2.circle(frame, hd.right_eye_inner, 1, (0, 0, 255), 2)

    l_box = [hd.left_eye_top, hd.left_eye_bottom, hd.left_eye_inner[0] - 10, hd.left_eye_outer[0] + 10]
    r_box = [hd.right_eye_top, hd.right_eye_bottom, hd.right_eye_outer[0] - 10, hd.right_eye_inner[0] + 10]

    eyeL = frame[l_box[0]:l_box[1], l_box[2]:l_box[3]]
    eyeR = frame[r_box[0]:r_box[1], r_box[2]:r_box[3]]
    # cv2.imshow("Left", eyeL)
    # cv2.imshow("Right", eyeR)
    
    left_d = hd.irisFinder("L")
    right_d = hd.irisFinder("R")
    irisDiam = max(left_d, right_d)
    dist = 90 - (irisDiam - 1)*2.5

    # centerL = (left_c_x + l_box[2], left_c_y + l_box[0])
    # centerR = (right_c_x + r_box[2], right_c_y + r_box[0])
    # cv2.circle(frame, centerL, irisRadius, (255, 50, 0), 1)
    # cv2.circle(frame, centerL, 1, (255, 50, 0), 2)
    # cv2.circle(frame, centerR, irisRadius, (0, 50, 255), 1)
    # cv2.circle(frame, centerR, 1, (0, 50, 255), 2)

    # print("Left:", squaredDistance(hd.left_eye_outer, hd.left_eye_inner))
    # print("Right:", squaredDistance(hd.right_eye_outer, hd.right_eye_inner))

    cv2.putText(frame, str(dist), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    leftp1, leftp2, rightp1, rightp2 = hd.gaze(dist)
    cv2.line(frame, leftp1, leftp2, (255, 255, 255), 1)
    cv2.line(frame, rightp1, rightp2, (255, 255, 255), 1)

    cv2.imshow('Eye Vectors', frame)

    if cv2.waitKey(2) & 0xFF == 27:
        break
cap.release()

    


