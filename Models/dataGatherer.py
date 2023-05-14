# Same principle as calibration
# but more points

import sys
import os
import cv2
import datetime
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

# define global variables
WIDTH, HEIGHT = 0, 0
OBJECT = 15
COORDINATES = []
TIME_STAMP = ""

# class for calibration screen
class FirstCalibration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.INDEX = 0

        self.label = QLabel('<H1>Calibration stage 1.1</H1><BR />Look at the center of a purple circle and click on it', self)
        self.label.setStyleSheet('''
            QLabel {
                text-align: center;
                font-size: 24px;
                padding: 100px;
                opacity: 0.5;
            }
        ''')

        self.button = QPushButton('Click', self)
        self.button.setStyleSheet('''
            QPushButton {
                background-color: #6200ad;
                border: none;
                color: #6200ad;
                text-align: center;
                text-decoration: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #8900f2;
            }
            QPushButton:pressed {
                background-color: #fcad03;
            }
        ''')
        self.button.setGeometry(QRect(-OBJECT, -OBJECT, OBJECT*2, OBJECT*2))
        self.button.clicked.connect(self.move_button)

        self.showFullScreen()

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(self.geometry())

        self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)

    # close window is ESC is pressed
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    # if window is closed, stop caprure
    def closeEvent(self, event):
        _, frame = self.capture.read()
        cv2.imwrite("data/" + TIME_STAMP + "/" + str(self.INDEX - 1) + '.jpg', frame)
        event.accept()
        self.capture.release()
        cv2.destroyAllWindows()

    # save a picture from webcam and change circle's position
    def move_button(self):
        _, frame = self.capture.read()
        cv2.imwrite("data/" + TIME_STAMP + "/" + str(self.INDEX - 1) + '.jpg', frame)

        self.INDEX += 1
        if self.INDEX < len(COORDINATES):
            new_position = QPoint(COORDINATES[self.INDEX][0], COORDINATES[self.INDEX][1])
            self.button.move(new_position)
            self.label.setText(str(self.INDEX))
        else:
            self.close()


# creates coordinates for circles from stage 1
def fillInCoords():
    for y in range(0, HEIGHT + 1, HEIGHT//10):
        iy = y - OBJECT
        for x in range(0, WIDTH + 1, WIDTH//20):
            ix = x - OBJECT
            COORDINATES.append([ix, iy])


if __name__ == '__main__':
    TIME_STAMP = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # you must have a folder named 'data' in your directory
    os.mkdir("data/" + TIME_STAMP)

    # start PyQt app
    app = QApplication(sys.argv)
    window = FirstCalibration()
    WIDTH, HEIGHT = window.width(), window.height()
    fillInCoords()

    window.show()
    sys.exit(app.exec_())
