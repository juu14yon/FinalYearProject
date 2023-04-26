import sys
import cv2
import os
import numpy as np
import csv
import json
from mss import mss
import datetime
from PIL import Image
import ffmpegcv

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QColorDialog, QFileDialog, QPushButton, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon, QCursor
from PyQt5.uic import loadUi

from main_window import Ui_MainWindow

WIDTH, HEIGHT = 1366, 768
OBJECT = 30


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
        self.COORDINATES = []
        self.fillInCoords()

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

    def fillInCoords(self):
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
                self.COORDINATES.append([ix, iy])

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
        cv2.imwrite("data/first/" + str(self.INDEX) + '.jpg', frame)

        self.INDEX += 1
        if self.INDEX < 27:
            new_position = QPoint(self.COORDINATES[self.INDEX%9][0], self.COORDINATES[self.INDEX%9][1])
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

        self.file = open("data/second/coordinates.csv", mode='a', newline='')
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
        cv2.imwrite("data/second/" + str(self.INDEX) + '.jpg', frame)
        new_row = [self.INDEX, x, y]
        self.writer.writerow(new_row)
        self.INDEX += 1

        print("Mouse position: ", x , y)


# main app class
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('res/appIcon.svg'))

        self.green = "#4ddb44"
        self.gray = "#d9d9d9"
        self.cssBackground = 'background-color: %s;\nborder-radius: 0;\n'

        self.setupUi(self)
        self.getConfig()
        self.setSettings()

        self.exitButton.clicked.connect(self.exitApp)
        self.folderButton.clicked.connect(self.openDirectory)
        self.overColorButton.clicked.connect(self.pickColorDialog)
        self.changeDirButton.clicked.connect(self.changeDirectory)
        self.calibrButton.clicked.connect(self.calibration)

        self.topLeftButton.clicked.connect(self.topLeft)
        self.topRightButton.clicked.connect(self.topRight)
        self.botLeftButton.clicked.connect(self.botLeft)
        self.botRightButton.clicked.connect(self.botRight)

        self.videoThread = videoThread()
        self.startButton.clicked.connect(self.toggleRec)
        self.videoThread.ImageUpdate.connect(self.ImageUpdateSlot)

    def exitApp(self):
        with open("config.json", "w") as file:
            json.dump(self.settings, file)
        self.close()

    def getConfig(self):
        if os.path.isfile("config.json"):
            with open("config.json") as file:
                self.settings = json.load(file)
        else:
            with open("config.json", "w") as file:
                currentDirectory = os.getcwd()
                self.settings = {"theme": "Light", "color": "#ffc700", "camPos": "br", "path": currentDirectory}
                json.dump(self.settings, file)

    def setSettings(self):
        if self.settings["camPos"] == "tl":
            self.topLeftButton.setStyleSheet(self.cssBackground % self.green)
        elif self.settings["camPos"] == "tr":
            self.topRightButton.setStyleSheet(self.cssBackground % self.green)
        elif self.settings["camPos"] == "bl":
            self.botLeftButton.setStyleSheet(self.cssBackground % self.green)
        else:
            self.botRightButton.setStyleSheet(self.cssBackground % self.green)

        self.overColorLabel.setStyleSheet(self.cssBackground % self.settings["color"])
        QApplication.processEvents()

    def changeTheme(self):
        if self.theme == "Light":
            self.theme = "Dark"
        else:
            self.theme = "Light"

    def pickColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["color"] = color.name()
            self.overColorLabel.setStyleSheet(self.cssBackground % color.name())
            QApplication.processEvents()

    def topLeft(self):
        self.settings["camPos"] = "tl"
        self.topLeftButton.setStyleSheet(self.cssBackground % self.green)
        self.topRightButton.setStyleSheet(self.cssBackground % self.gray)
        self.botLeftButton.setStyleSheet(self.cssBackground % self.gray)
        self.botRightButton.setStyleSheet(self.cssBackground % self.gray)
        QApplication.processEvents()

    def topRight(self):
        self.settings["camPos"] = "tr"
        self.topLeftButton.setStyleSheet(self.cssBackground % self.gray)
        self.topRightButton.setStyleSheet(self.cssBackground % self.green)
        self.botLeftButton.setStyleSheet(self.cssBackground % self.gray)
        self.botRightButton.setStyleSheet(self.cssBackground % self.gray)
        QApplication.processEvents()

    def botLeft(self):
        self.settings["camPos"] = "bl"
        self.topLeftButton.setStyleSheet(self.cssBackground % self.gray)
        self.topRightButton.setStyleSheet(self.cssBackground % self.gray)
        self.botLeftButton.setStyleSheet(self.cssBackground % self.green)
        self.botRightButton.setStyleSheet(self.cssBackground % self.gray)
        QApplication.processEvents()

    def botRight(self):
        self.settings["camPos"] = "br"
        self.topLeftButton.setStyleSheet(self.cssBackground % self.gray)
        self.topRightButton.setStyleSheet(self.cssBackground % self.gray)
        self.botLeftButton.setStyleSheet(self.cssBackground % self.gray)
        self.botRightButton.setStyleSheet(self.cssBackground % self.green)
        QApplication.processEvents()

    def toggleRec(self):
        flag = self.startButton.isChecked()
        self.videoThread.setParameters(self.settings["camPos"], self.settings["color"], self.settings["path"])
        if flag:
            self.videoThread.start()
            self.recStatLabel.setText("Recording is running...")
            self.recHintLabel.setText("")
            self.startButton.setText("Stop")
            self.startButton.setIcon(QIcon("res/stopIcon.png"))
        else:    
            self.videoThread.stop()
            self.recStatLabel.setText("Recording stopped")
            self.recHintLabel.setText("Press to start recording --->")
            self.startButton.setText("Start")
            self.startButton.setIcon(QIcon("res/playIcon.png"))

        self.overlayWidget.setEnabled(not flag)
        self.webcamWidget.setEnabled(not flag)
        self.otherWidget.setEnabled(not flag)

    def openDirectory(self):
        path = self.settings["path"]
        os.system("start " + path)

    def changeDirectory(self):
        newPath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if newPath!="":
            self.settings["path"] = newPath

    def calibration(self):
        if not os.path.isdir("data"):
            os.mkdir("data")
        if not os.path.isdir("data/first"):
            os.mkdir("data/first")
        if not os.path.isdir("data/second"):
            os.mkdir("data/second")
            
        self.second_window = FirstCalibration()
        self.second_window.show()

    def ImageUpdateSlot(self, Image):
        self.frame.setPixmap(QPixmap.fromImage(Image))



class videoThread(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def setParameters(self, camPos, color, path):
        self.camPos = camPos
        self.color = color
        self.path = path

    def run(self):
        self.webH = 150
        self.webW = 200

        self.ThreadActive = True
        monitor = {'top': 0, 'left':0, 'width':WIDTH, 'height':HEIGHT}
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        file_name = f'/{time_stamp}.mp4'

        self.captured_video = ffmpegcv.VideoWriter(self.path + file_name, 'h264', 15.0, (WIDTH, HEIGHT))
        self.capture = cv2.VideoCapture(0)

        sct = mss()

        while self.ThreadActive:
            success, webcam = self.capture.read()
            sct_img = sct.grab(monitor)
            screencap = Image.frombytes('RGB', (sct_img.size.width, sct_img.size.height), sct_img.rgb)
            img_bgr = cv2.cvtColor(np.array(screencap), cv2.COLOR_RGB2BGR)

            if success:
                webcam = cv2.cvtColor(webcam, cv2.COLOR_BGR2RGB)
                flipped = cv2.flip(webcam, 1)
                resized = cv2.resize(flipped, (self.webW, self.webH), interpolation = cv2.INTER_AREA)

                if self.camPos == "tl":
                    img_bgr[:self.webH, :self.webW] = resized
                elif self.camPos == "tr":
                    img_bgr[:self.webH, WIDTH - self.webW:] = resized
                elif self.camPos == "bl":
                    img_bgr[HEIGHT - self.webH:, :self.webW] = resized
                elif self.camPos == "br":
                    img_bgr[HEIGHT - self.webH:, WIDTH - self.webW:] = resized

                self.captured_video.write(img_bgr)

                qtImage = QImage(img_bgr.data, img_bgr.shape[1], img_bgr.shape[0], img_bgr.shape[1]*3, QImage.Format_RGB888)
                frame = qtImage.scaled(930, 930*768//1366, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(frame)

    def stop(self):
        self.capture.release()
        self.captured_video.release()
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())