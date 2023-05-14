import cv2
from HeadTilt import HeadTilt

distance = 50 # centimeter
ht = HeadTilt()
cap = cv2.VideoCapture(0)
count = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        count += 1
        if count > 10:
            break

    frame.flags.writeable = False
    ht.start(frame)
    frame.flags.writeable = True

    flag, alpha, beta = ht.angles()
    if ht.isFace:
        left_d = ht.diameter("L")
        right_d = ht.diameter("R")
        irisDiam = max(left_d, right_d)
        distance = 90 - (irisDiam - 1)*2.5
        cv2.putText(frame, str(distance), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

        leftp1, leftp2, rightp1, rightp2 = ht.gaze(distance)
        
        if len(leftp1)>1:
            cv2.line(frame, leftp1, leftp2, (255, 255, 255), 1)
            cv2.line(frame, rightp1, rightp2, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "Cannot find gaze vectors", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        
        frame = ht.draw(frame)
    else:
        cv2.putText(frame, "Cannot find face", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    cv2.imshow('Eye Vectors', frame)

    if cv2.waitKey(2) & 0xFF == 27:
        break

cap.release()

    


