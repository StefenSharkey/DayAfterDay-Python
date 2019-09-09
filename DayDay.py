#!/usr/bin/env python3

import logging
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import sys

from PyQt5.QtCore import Qt, qDebug
from PyQt5.QtWidgets import QApplication, QPushButton, QFrame, QGridLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImageReader, QPixmap

__author__ = "Stefen Sharkey"
__version__ = "0.01a"
__project__ = "Day / Day"

debug = True

class DayDay(QWidget):

    def __init__(self):
        super().__init__()
        self.title = __project__ + " " + __version__
        # self.width = 640
        # self.height = 480

        self.initUI()

    def initUI(self):
        # Set the main window layout.
        grid = QGridLayout()
        self.setLayout(grid)

        # Add the widgets to the main layout.
        grid.addWidget(self.addCamera(), 0, 0)
        grid.addWidget(self.addShutter(), 1, 0)
        grid.addWidget(self.addHistory(), 0, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0)
        # grid.setColumnStretch(2, 1)

        # self.resize(self.width, self.height)
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

        cameraLabel = QLabel("This is where the camera widget would go...IF I HAD ONE.")
        cameraLabel.resize(640, 480)
        cameraLabel.setWordWrap(False)

        cameraLayout.addWidget(cameraLabel)
        camera.setLayout(cameraLayout)
        return camera

    def addShutter(self):
        # Add the shutter button.
        shutter = QPushButton("Take Picture")
        # shutter = QWidget()
        # shutterLayout = QGridLayout()
        #
        # if debug:
        #     shutter.setAutoFillBackground(True)
        #     palette = shutter.palette()
        #     palette.setColor(shutter.backgroundRole(), Qt.blue)
        #     shutter.setPalette(palette)
        #
        # shutterButton = QPushButton("Take Picture")
        #
        # shutterLayout.addWidget(shutterButton)
        # shutter.setLayout(shutterLayout)
        return shutter

    def addHistory(self):
        history = QWidget()
        historyLayout = QVBoxLayout()


        if debug:
            history.setAutoFillBackground(True)
            palette = history.palette()
            palette.setColor(history.backgroundRole(), Qt.green)
            history.setPalette(palette)

        picture_files_directory = str(Path.home()) + "\\Documents\\DayAfterDay\\"

        if not os.path.exists(picture_files_directory):
            os.makedirs(picture_files_directory)

        picture_files = [file for file in listdir(picture_files_directory) if isfile(join(picture_files_directory, file))]

        for file in picture_files:
            if QImageReader.supportedImageFormats().count(file[-3:].lower()) > 0:
                historyLayout.addWidget(HistoryWidget(picture_files_directory + file))
                historyLayout.addWidget(HistoryWidget(picture_files_directory + file))
                historyLayout.addWidget(HistoryWidget(picture_files_directory + file))
                historyLayout.addWidget(HistoryWidget(picture_files_directory + file))
                historyLayout.addWidget(HistoryWidget(picture_files_directory + file))

        emptyWidget = QWidget()
        emptyWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        historyLayout.addWidget(emptyWidget)

        history.setLayout(historyLayout)

        # scrollArea = QScrollArea(history)
        # scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scrollArea.setWidgetResizable(True)
        #
        # scrollArea.setLayout(historyLayout)

        return history


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
    ex = DayDay()
    sys.exit(app.exec_())
