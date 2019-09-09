#!/usr/bin/env python3

import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import datetime
import sys

import cv2

from PyQt5.QtCore import Qt, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QFrame, QGridLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QImageReader, QPixmap

__author__ = "Stefen Sharkey"
__version__ = "0.01a"
__project__ = "Day / Day"

debug = True

picture_files_directory = str(Path.home()) + "\\Documents\\DayAfterDay\\"


class DayAfterDay(QWidget):

    def __init__(self):
        super().__init__()
        self.title = __project__ + " " + __version__

        self.is_camera_showing = False
        self.is_saving = False

        self.initUI()

    def initUI(self):
        # Set the main window layout.
        grid = QGridLayout()
        self.setLayout(grid)

        # Add the widgets to the main layout.
        grid.addWidget(self.addCamera(), 0, 0)
        grid.addWidget(self.addShutter(), 1, 0)
        grid.addWidget(self.addVLine(), 0, 1, 2, 1)
        grid.addWidget(self.addHistory(), 0, 2, 2, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0)

        self.setWindowTitle(self.title)
        self.show()

    def addCamera(self):
        # Add the camera widget.
        camera = QWidget()
        cameraLayout = QGridLayout()

        if debug:
            camera.setAutoFillBackground(True)
            palette = camera.palette()
            palette.setColor(camera.backgroundRole(), Qt.red)
            camera.setPalette(palette)

        self.cameraLabel = QLabel(self)
        self.cameraLabel.setAlignment(Qt.AlignCenter)

        thread = Thread(self)
        thread.changePixmap.connect(self.setImage)
        thread.start()

        cameraLayout.addWidget(self.cameraLabel)
        camera.setLayout(cameraLayout)

        return camera

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.image = QPixmap.fromImage(image)
        self.cameraLabel.setPixmap(self.image.scaled(self.cameraLabel.width(), self.cameraLabel.height(), Qt.KeepAspectRatio))

        # We don't want the user pressing the shutter if no image has shown.
        self.shutter.setEnabled(True)

    def addShutter(self):
        self.shutter = QPushButton("Take Picture")
        self.shutter.clicked.connect(self.on_shutter_pressed)
        self.shutter.setEnabled(False)
        return self.shutter

    @pyqtSlot()
    def on_shutter_pressed(self):
        # File name follows ISO 8601 standards with an increment counter and are stored and read as follows:
        # DayAfterDay-YYYY-MM-DD-HHMMSS-X
        datetime_formatted = str(datetime.datetime.now())[:-7].replace(" ", "-").replace(":", "")
        increment_counter = 1
        picture_file_extension = ".png"
        picture_file_name = picture_files_directory + "DayAfterDay-" + datetime_formatted + "-"

        # Increment the counter in case file already exists to avoid overwriting files.
        while True:
            if not Path(picture_file_name + str(increment_counter) + picture_file_extension).exists():
                break

            increment_counter += 1

        picture_file_name += str(increment_counter) + picture_file_extension
        self.image.save(picture_file_name, "PNG")

    def addVLine(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        return line

    def addHistory(self):
        history = QWidget()
        history_layout = QVBoxLayout()

        if debug:
            history.setAutoFillBackground(True)
            palette = history.palette()
            palette.setColor(history.backgroundRole(), Qt.green)
            history.setPalette(palette)

        if not os.path.exists(picture_files_directory):
            os.makedirs(picture_files_directory)

        picture_files = [file for file in listdir(picture_files_directory) if isfile(join(picture_files_directory, file))]

        for file in picture_files:
            if QImageReader.supportedImageFormats().count(file[-3:].lower()) > 0:
                history_layout.addWidget(HistoryWidget(picture_files_directory + file))

        # Fill empty space at bottom.
        emptyWidget = QWidget()
        emptyWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        history_layout.addWidget(emptyWidget)

        history.setLayout(history_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(history)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Fixed width set to 237 to account for 37 pixels being used by QScrollArea.
        scroll_area.setFixedWidth(237)

        return scroll_area


class Thread(QThread):

    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()

            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.changePixmap.emit(convertToQtFormat)


class HistoryWidget(QWidget):

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

        self.initUI()

    def initUI(self):
        if debug:
            self.setAutoFillBackground(True)
            palette = self.palette()
            palette.setColor(self.backgroundRole(), Qt.red)
            self.setPalette(palette)

        image = QPixmap(self.image_path)
        imageLabel = QLabel(self)
        # print(self.image_path)
        # imageLabel.setPixmap(image.scaled(imageLabel.width(), imageLabel.height(), Qt.KeepAspectRatio))
        imageLabel.setPixmap(image.scaledToWidth(200))
        # imageLabel.setScaledContents(True)

        self.setFixedSize(200, image.scaledToWidth(200).height())
        layout = QGridLayout()
        layout.addWidget(imageLabel)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DayAfterDay()
    sys.exit(app.exec_())
