#!/usr/bin/env python3

import configparser
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import datetime
import sys

import cv2

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

__author__ = "Stefen Sharkey"
__version__ = "0.01b"
__project__ = "Day / Day"

debug = False

files_directory = str(Path.home()) + "\\Documents\\DayAfterDay\\"
config_file_name = files_directory + "DayAfterDay.ini"

class DayAfterDay(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = __project__ + " " + __version__

        self.is_camera_showing = False
        self.is_saving = False

        self.initUI()

    def initUI(self):
        # Set the main window layout.
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.initConfig()
        self.initToolbar()

        # Add the widgets to the main layout.
        self.main_layout.addWidget(self.addCamera(), 0, 0)
        self.main_layout.addWidget(self.addOpacitySlider(), 1, 0)
        self.main_layout.addWidget(self.addShutter(), 2, 0)
        self.main_layout.addWidget(self.addVLine(), 0, 1, 3, 1)
        self.main_layout.addWidget(self.addHistory(), 0, 2, 3, 1)

        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 0)
        self.main_layout.setRowStretch(0, 1)

        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)

        self.setCentralWidget(main_widget)
        self.setWindowTitle(self.title)
        self.show()

    def initConfig(self):
        self.config = configparser.ConfigParser()

        if not Path(config_file_name).exists():
            self.config["DEFAULT"] = {"opacity": "50"}

            with open(config_file_name, "w+") as config_file:
                self.config.write(config_file)

        self.config.read(config_file_name)

    def initToolbar(self):
        file = self.menuBar().addMenu("&File")
        help = self.menuBar().addMenu("&Help")

        quit = QAction("&Quit", self)
        quit.triggered.connect(self.close)

        about_qt = QAction("&About Qt", self)
        about_qt.triggered.connect(qApp.aboutQt)

        file.addAction(quit)
        help.addAction(about_qt)

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
        self.cameraLabel.installEventFilter(self)

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

        self.update()

        # We don't want the user pressing the shutter if no image has shown.
        self.shutter.setEnabled(True)

    def paintEvent(self, event):
        if self.cameraLabel.pixmap() is not None:
            x_loc = ((self.main_layout.itemAtPosition(0, 0).geometry().width() - self.cameraLabel.pixmap().width()) / 2) + 1
            y_loc = (self.main_layout.itemAtPosition(0, 0).geometry().height() - self.cameraLabel.pixmap().height()) / 2
            painter = QPainter()

            painter.begin(self)
            painter.drawPixmap(x_loc, y_loc, self.cameraLabel.pixmap())
            painter.end()

            if len(self.picture_files) > 0:
                painter.begin(self)

                slider_pos = self.slider.sliderPosition()
                self.config.set("DEFAULT", "opacity", str(slider_pos))

                with open(config_file_name, "w") as config_file:
                    self.config.write(config_file)

                painter.setOpacity(slider_pos / 100)
                shadow_picture = QPixmap(files_directory + self.picture_files[0])
                shadow_picture = shadow_picture.scaled(self.cameraLabel.width(), self.cameraLabel.height(), Qt.KeepAspectRatio)
                painter.drawPixmap(x_loc, y_loc, shadow_picture)
                painter.end()

    def eventFilter(self, obj, ev):
        return ev.type() == QEvent.Paint

    def addOpacitySlider(self):
        parent = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Previous Picture Opacity")
        label.setAlignment(Qt.AlignCenter)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(10)
        self.slider.setFixedWidth(250)
        self.slider.setSliderPosition(int(self.config["DEFAULT"]["opacity"]))

        layout.addWidget(label)
        layout.addWidget(self.slider, alignment=Qt.AlignCenter)

        parent.setLayout(layout)

        return parent

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
        picture_file_name = files_directory + "DayAfterDay-" + datetime_formatted + "-"

        # Increment the counter in case file already exists to avoid overwriting files.
        while True:
            if not Path(picture_file_name + str(increment_counter) + picture_file_extension).exists():
                break

            increment_counter += 1

        picture_file_name += str(increment_counter) + picture_file_extension
        self.image.save(picture_file_name, "PNG")
        self.history_layout.insertWidget(0, HistoryWidget(picture_file_name))
        self.picture_files.insert(0, picture_file_name[len(files_directory):])

    def addVLine(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        return line

    def addHistory(self):
        history = QWidget()
        self.history_layout = QVBoxLayout()

        if debug:
            history.setAutoFillBackground(True)
            palette = history.palette()
            palette.setColor(history.backgroundRole(), Qt.green)
            history.setPalette(palette)

        if not os.path.exists(files_directory):
            os.makedirs(files_directory)

        files = [file for file in listdir(files_directory) if isfile(join(files_directory, file))]
        files.sort(reverse=True)

        self.picture_files = []

        for file in files:
            if QImageReader.supportedImageFormats().count(file[-3:].lower()) > 0:
                self.picture_files.append(file)
                self.history_layout.addWidget(HistoryWidget(files_directory + file))

        # Fill empty space at bottom.
        emptyWidget = QWidget()
        emptyWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.history_layout.addWidget(emptyWidget)

        history.setLayout(self.history_layout)

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
