# This is code for a PyQt5 app that can be used for data gathering.

import sys
import os
import cv2
import csv
import datetime
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

# define global variables
WIDTH, HEIGHT = 0, 0
OBJECT = 30
COORDINATES = []
TIME_STAMP = ""


# a class for label from main screen of stage 2
class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mousePressEvent(self, event):
        self.setParent(None)


# class for calibration stage 1 screen
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
        self.button.setGeometry(QRect(0, 0, OBJECT, OBJECT))
        self.button.clicked.connect(self.move_button)

        self.showFullScreen()

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(self.geometry())

        self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)

    # close window is ESC is pressed
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    # if window is closed, stop caprure, start stage 2
    def closeEvent(self, event):
        event.accept()
        self.capture.release()
        cv2.destroyAllWindows()
        self.second_window = SecondCalibration()
        self.second_window.show()

    # save a picture from webcam and change circle's position
    def move_button(self):
        _, frame = self.capture.read()
        cv2.imwrite("data/" + TIME_STAMP + "/first/" + str(self.INDEX) + '.jpg', frame)

        self.INDEX += 1
        if self.INDEX < 27:
            new_position = QPoint(COORDINATES[self.INDEX%9][0], COORDINATES[self.INDEX%9][1])
            self.button.move(new_position)
            if self.INDEX%9 == 1:
                self.label.setText("")
            if self.INDEX == 9:
                self.label.setText("<H1>Calibration stage 1.2</H1><BR />Move closer to the screen and start again")
            if self.INDEX == 18:
                self.label.setText("<H1>Calibration stage 1.3</H1><BR />Now move farther from the screen")
        else:
            self.close()


# class for calibration stage 2 screen
class SecondCalibration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.INDEX = 0

        self.file = open("data/" + TIME_STAMP + "/second/coordinates.csv", mode='a', newline='')
        self.writer = csv.writer(self.file)

        self.label = ClickableLabel(self)
        self.label.setText('<H1>Calibration stage 2</H1><BR />Follow your mouse cursor as accuratelly as possible<BR />Click to start')
        self.label.setStyleSheet('''
            QLabel {
                text-align: center;
                font-size: 24px;
                padding: 100px;
                opacity: 0.5;
            }
        ''')

        self.showFullScreen()

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(self.geometry())

        self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)
        # self.capture = cv2.VideoCapture("C:/FYP Project/code/media/kaggleDS/Videos/b.mp4")
        self.setMouseTracking(True)
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.saveData)
        
    # if ESC is pressed, close csv file, stop capture, close window
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.file.close()
            self.capture.release()
            cv2.destroyAllWindows()
            self.close()

    # delay for saving webcam frame after cursor is moved
    def mouseMoveEvent(self, event):
        self.timer.stop()
        self.timer.start()

    # save a picture from webcam and cursor's coordinates
    def saveData(self):
        cursor_position = QCursor.pos()
        x = cursor_position.x()
        y = cursor_position.y()

        _, frame = self.capture.read()
        cv2.imwrite("data/" + TIME_STAMP + "/second/" + str(self.INDEX) + '.jpg', frame)
        new_row = [self.INDEX, x, y]
        self.writer.writerow(new_row)
        self.INDEX += 1

        print("Mouse position: ", x , y)


# creates coordinates for circles from stage 1
def fillInCoords():
    for y in range(0, HEIGHT + 1, HEIGHT//2):
        if y == 0:
            iy = y
        else:
            iy = y - OBJECT
        for x in range(0, WIDTH + 1, WIDTH//2):
            if x == 0:
                ix = x
            else:
                ix = x - OBJECT
            COORDINATES.append([ix, iy])


if __name__ == '__main__':
    TIME_STAMP = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # you must have a folder named 'data' in your directory
    os.mkdir("data/" + TIME_STAMP)
    os.mkdir("data/" + TIME_STAMP + "/first")
    os.mkdir("data/" + TIME_STAMP + "/second")

    # start PyQt app
    app = QApplication(sys.argv)
    window = FirstCalibration()
    WIDTH, HEIGHT = window.width(), window.height()
    fillInCoords()

    window.show()
    sys.exit(app.exec_())
