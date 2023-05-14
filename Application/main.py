import sys, os, datetime, json, pickle, webbrowser
import cv2, ffmpegcv
import numpy as np

from mss import mss
from PIL import Image

from skimage.transform import SimilarityTransform
from scipy.ndimage import gaussian_filter1d

from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QPushButton, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5 import QtCore

from res.MainWindow import Ui_MainWindow
from res.HeadTilt import HeadTilt

# Screen dimensions
WIDTH, HEIGHT = 1366, 768
OBJECT = 15

# Gaze predicting model
predictor = pickle.load(open("res/predictor.sav", 'rb'))

# class for calibration stage 1 screen
class CalibrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ht = HeadTilt()
        self.index = 0
        self.COORDINATES = []
        self.predictions = [[0, 0] for i in range(9)]
        self.fillInCoords()

        self.label = QLabel('<H1>Calibration stage 1</H1><BR />Look at the center of a purple circle and click on it', self)
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
        self.button.clicked.connect(self.moveButton)

        self.showFullScreen()

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(self.geometry())

        self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)
        _, frame = self.capture.read()

    def fillInCoords(self):
        for y in range(0, HEIGHT + 1, HEIGHT//2):
            iy = y - OBJECT
            for x in range(0, WIDTH + 1, WIDTH//2):
                ix = x - OBJECT
                self.COORDINATES.append([ix, iy])

    # close window is ESC is pressed
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    # if window is closed, stop caprure, start stage 2
    def closeEvent(self, event):
        _, frame = self.capture.read()
        cv2.imwrite("data/" + str(self.index) + '.jpg', frame)
        self.predCoords(frame)
        if self.index>=27:
            mean = [[i[0]//3, i[1]//3] for i in self.predictions]
            print(self.predictions)
            trans = SimilarityTransform()
            trans.estimate(mean, self.COORDINATES)
            with open('calibration.pkl', 'wb') as f:
                pickle.dump(trans, f)

        event.accept()
        self.capture.release()
        cv2.destroyAllWindows()

    def predCoords(self, frame):
        if self.index<1:
            return True
        frame.flags.writeable = False
        self.ht.start(frame)
        frame.flags.writeable = True
        _, alpha, beta = self.ht.angles()
        left_d = self.ht.diameter("L")
        right_d = self.ht.diameter("R")
        irisDiam = max(left_d, right_d)
        distance = 90 - (irisDiam - 1)*2.5
        leftp1, leftp2, rightp1, rightp2 = self.ht.gaze(distance)

        if self.ht.isFace and len(leftp1)>1:
            new_row = np.array([
                        alpha, beta,
                        distance, 
                        leftp1[0], leftp1[1], 
                        self.ht.vecLeft[0], self.ht.vecLeft[1], self.ht.vecLeft[2],
                        rightp1[0], rightp1[1], 
                        self.ht.vecRight[0], self.ht.vecRight[1], self.ht.vecRight[2],
                        ])
            pred = predictor.predict(new_row.reshape(1, -1))
            x, y = list(map(int, [pred.flat[0], pred.flat[1]]))
            self.predictions[self.index%9-1][0] += x
            self.predictions[self.index%9-1][1] += y
            return True
        return False

    # save a picture from webcam and change circle's position
    def moveButton(self):
        _, frame = self.capture.read()
        print(self.index)

        if self.predCoords(frame):
            cv2.imwrite("data/" + str(self.index) + '.jpg', frame)
            self.label.setText("")

            self.index += 1
            if self.index < 27:
                new_position = QPoint(self.COORDINATES[self.index%9][0], self.COORDINATES[self.index%9][1])
                self.button.move(new_position)
                if self.index%9 == 1:
                    self.label.setText("")
                if self.index == 9:
                    self.label.setText("<H1>Calibration stage 2</H1><BR />Move closer to the screen and start again")
                if self.index == 18:
                    self.label.setText("<H1>Calibration stage 3</H1><BR />Now move farther from the screen")
            else:
                self.close()
        else:
            self.label.setText("<H1>Cannot see your face, try again</H1>")

# main app class
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('res/appIcon.svg'))

        self.green = "#4ddb44"
        self.gray = "#d9d9d9"
        self.cssBackground = 'background-color: %s;\nborder-radius: 0;\n'

        # Load interface and user settings
        self.setupUi(self)
        self.getConfig()
        self.setSettings()

        # Connect buttons to events
        self.helpMenu.triggered.connect(self.helpDisplay)
        self.exitButton.clicked.connect(self.exitApp)
        self.folderButton.clicked.connect(self.openDirectory)
        self.overColorButton.clicked.connect(self.pickColorDialog)
        self.changeDirButton.clicked.connect(self.changeDirectory)
        self.calibrButton.clicked.connect(self.calibration)
        self.themeButton.clicked.connect(self.changeTheme)

        self.topLeftButton.clicked.connect(self.topLeft)
        self.topRightButton.clicked.connect(self.topRight)
        self.botLeftButton.clicked.connect(self.botLeft)
        self.botRightButton.clicked.connect(self.botRight)

        # Connect video-recording thread to the main app
        self.videoThread = VideoThread()
        self.startButton.clicked.connect(self.toggleRec)
        self.videoThread.ImageUpdate.connect(self.imageUpdate)

    # Save setttings and exit
    def exitApp(self):
        with open("res/config.json", "w") as file:
            json.dump(self.settings, file)
        self.close()

    # Read settings if exist
    def getConfig(self):
        if os.path.isfile("res/config.json"):
            with open("res/config.json") as file:
                self.settings = json.load(file)
        else:
            with open("res/config.json", "w") as file:
                currentDirectory = os.getcwd()
                self.settings = {"theme": "Light", "color": "#ffc700", "camPos": "br", "path": currentDirectory}
                json.dump(self.settings, file)

    # Apply settings to the app interface
    def setSettings(self):
        # Set theme
        if self.settings["theme"] == "Light":
            with open("res/lightTheme.qss","r") as f:
                self.setStyleSheet(f.read())
            self.gray = "#d9d9d9"
        else:
            with open("res/darkTheme.qss","r") as f:
                self.setStyleSheet(f.read())
            self.gray = "#545454"

        # Set camera position
        if self.settings["camPos"] == "tl":
            self.topLeft()
        elif self.settings["camPos"] == "tr":
            self.topRight()
        elif self.settings["camPos"] == "bl":
            self.botLeft()
        else:
            self.botRight()

        # Set overlay color
        self.overColorLabel.setStyleSheet(self.cssBackground % self.settings["color"])

        # Apply all changes
        QApplication.processEvents()

    @QtCore.pyqtSlot()
    def helpDisplay(self):
        filename = "file:///" + os.getcwd() + "/res/about/help.html"
        webbrowser.open(filename, new=2)

    # Toggle theme on button click
    def changeTheme(self):
        if self.settings["theme"] == "Light":
            self.settings["theme"] = "Dark"
        else:
            self.settings["theme"] = "Light"
        self.setSettings()

    # Create color picker and set new color
    def pickColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["color"] = color.name()
            self.overColorLabel.setStyleSheet(self.cssBackground % color.name())
            QApplication.processEvents()

    # Next 4 functions are used for camera position
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

    # Toggle recording, disable widgets
    def toggleRec(self):
        flag = self.startButton.isChecked()
        self.videoThread.setParameters(self.settings["camPos"], self.settings["color"][1:], self.settings["path"])
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

    # Open output folder
    def openDirectory(self):
        path = self.settings["path"]
        os.system("start " + path)

    # Create directory picker
    def changeDirectory(self):
        newPath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if newPath!="":
            self.settings["path"] = newPath

    # Start calibration in new window
    def calibration(self):
        if not os.path.isdir("data"):
            os.mkdir("data")
            
        self.second_window = CalibrationWindow()
        self.second_window.show()

    # Connect thread signal to main window
    def imageUpdate(self, image):
        self.frame.setPixmap(QPixmap.fromImage(image))



class VideoThread(QThread):
    ImageUpdate = pyqtSignal(QImage)

    # Get user settings from main window
    def setParameters(self, camPos, color, path):
        self.camPos = camPos
        self.color = tuple(int(color[i:i+2], 16) for i in (4, 2, 0))
        self.path = path

    def getTime(self):
        if self.counter == 15:
            self.counter = 0
            self.sec += 1
            if self.sec == 60:
                self.sec = 0
                self.min += 1
                if self.min==60:
                    self.min = 0
                    self.hour += 1

        s_sec, s_min, s_hour = str(self.sec), str(self.min), str(self.hour)
        if len(s_sec)<2:
            s_sec = "0" + s_sec
        if len(s_min)<2:
            s_min = "0" + s_min
        if len(s_hour)<2:
            s_hour = "0" + s_hour

        time = "{}:{}:{}".format(s_hour, s_min, s_sec)

        return time
    
    def writeToLog(self, faceState, eyeState, inState, d, time):
        if faceState:
            if eyeState:
                if not inState:
                    if d != self.direction:
                        self.logs.write(f"{time} - Looking outside the screen in {d} direction\n")
            else:
                if eyeState != self.state[1]:
                    self.logs.write(f"{time} - Could not find the gaze vectors\n")
        else:
            if faceState != self.state[0]:
                self.logs.write(f"{time} - Could not detect the face\n")

        self.state = [faceState, eyeState]
        self.direction = d


    # Run video thread
    def run(self):
        self.close = False
        self.ThreadActive = True
        self.state = [True, True]
        self.direction = ""
        eyeState = True
        inState = True

        # For coordinates smoothing
        point_buffer = []
        window_size, sigma = 5, 3

        # For time
        self.counter = 0
        self.sec = 0
        self.min = 0
        self.hour = 0

        # For web camera
        self.webH = 150
        self.webW = 200

        # Create object for head and gaze tracking
        hgd = HeadTilt()

        # For screen and webcam recording
        monitor = {'top': 0, 'left':0, 'width':WIDTH, 'height':HEIGHT}
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        video_name = f'/{time_stamp}.mp4'
        self.captured_video = ffmpegcv.VideoWriter(self.path + video_name, 'h264', 15.0, (WIDTH, HEIGHT))
        self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)
        sct = mss()

        log_name = f'{self.path}/{time_stamp}.txt'
        self.logs = open(log_name, "w")

        # If you want to apply affine transformation based on calibration results
        # transFlag = False
        # if os.path.isfile("calibration.pkl"):
        #     with open("calibration.pkl", 'rb') as f:
        #         trans = pickle.load(f)
        #         transFlag = True

        while self.ThreadActive:
            if self.close:
                break
            # Tracking video time (different from real life time)
            self.counter += 1 
            time = self.getTime()

            success, webcam = self.capture.read()
            sct_img = sct.grab(monitor)
            screencap = Image.frombytes('RGB', (sct_img.size.width, sct_img.size.height), sct_img.rgb)
            img_bgr = cv2.cvtColor(np.array(screencap), cv2.COLOR_RGB2BGR)

            # If you want to add time to the video
            # cv2.putText(img_bgr, time, (10, 730), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))

            x, y = [0, 0]
            if success:
                flipped = cv2.flip(webcam, 1)

                # pass webcam to classifier, get x, y
                webcam.flags.writeable = False
                hgd.start(webcam)
                webcam.flags.writeable = True

                flag, alpha, beta = hgd.angles()

                faceState = hgd.isFace
                direction = ""

                if faceState:
                    left_d = hgd.diameter("L")
                    right_d = hgd.diameter("R")
                    irisDiam = max(left_d, right_d)
                    distance = 90 - (irisDiam - 1)*2.5

                    leftp1, leftp2, rightp1, rightp2 = hgd.gaze(distance)

                    if len(leftp1)>1:
                        eyeState = True
                        newData = np.array([
                            alpha, beta,
                            distance, 
                            leftp1[0], leftp1[1], 
                            hgd.vecLeft[0], hgd.vecLeft[1], hgd.vecLeft[2],
                            rightp1[0], rightp1[1], 
                            hgd.vecRight[0], hgd.vecRight[1], hgd.vecRight[2],
                        ])
                        
                        pred = predictor.predict(newData.reshape(1, -1))
                        center = tuple(map(int, [pred.flat[0], pred.flat[1]]))
                        x, y = center

                        # Check if inside the screen
                        if (x<=WIDTH) and (x>=0) and (y<=HEIGHT) and (y>=0):
                            inState = True
                        else:
                            inState = False
                            vert = False
                            if y>HEIGHT:
                                vert = True
                                direction += "down "
                            if y<0:
                                vert = True
                                direction += "up "

                            if x>WIDTH:
                                if vert:
                                    direction += "and "
                                direction += "right"
                            if x<0:
                                if vert:
                                    direction += "and "
                                direction += "left"
                        
                        # Apply affine transformation
                        # if transFlag: 
                        #     x, y = trans([x, y])[0]

                    else:
                        eyeState = False

                self.writeToLog(faceState, eyeState, inState, direction, time)
                
                # Smoothing out predicted coordinates to reduce jitter
                point_buffer.append([x, y])
                point_smoothed = gaussian_filter1d(np.array(point_buffer), sigma=sigma, axis=0)
                if len(point_buffer) >= window_size:
                    point_buffer.pop(0)
                x, y = point_smoothed[-1]

                # Add gaze position on video
                overlay = img_bgr.copy()
                cv2.circle(overlay, (int(x), int(y)), 1, self.color, 60)
                img_bgr = cv2.addWeighted(overlay, 0.3, img_bgr, 0.7, 0)

                # Add web camera to the video
                resized = cv2.resize(flipped, (self.webW, self.webH), interpolation = cv2.INTER_AREA)
                if self.camPos == "tl":
                    img_bgr[:self.webH, :self.webW] = resized
                elif self.camPos == "tr":
                    img_bgr[:self.webH, WIDTH - self.webW:] = resized
                elif self.camPos == "bl":
                    img_bgr[HEIGHT - self.webH:, :self.webW] = resized
                elif self.camPos == "br":
                    img_bgr[HEIGHT - self.webH:, WIDTH - self.webW:] = resized

                # Save the video
                if not self.close:
                    self.captured_video.write(img_bgr)

                    # Pass the video to main window
                    qtImage = QImage(img_bgr.data, img_bgr.shape[1], img_bgr.shape[0], img_bgr.shape[1]*3, QImage.Format_RGB888)
                    frame = qtImage.scaled(930, 930*768//1366, Qt.KeepAspectRatio)
                    self.ImageUpdate.emit(frame)

    # Release all captures and stop the thread
    def stop(self):
        self.close = True
        self.capture.release()
        self.captured_video.release()
        self.logs.close()
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())