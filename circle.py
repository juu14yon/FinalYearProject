import cv2
from ElementDetector import ElementsDetector

capture = cv2.VideoCapture(cv2.CAP_DSHOW)      
element = ElementsDetector()

while True:
    _, img = capture.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    element.setImage(gray)
    element.faceData()
    element.eyeData()
    element.irisData()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        capture.release()
        break

cv2.destroyAllWindows()
