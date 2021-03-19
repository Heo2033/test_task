import sys

from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QStyle
from openni import openni2

import design
from videooni import VideoOni


class Window(design.UiWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.oni_video: VideoOni = None

        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.play_pause)
        self.slider.sliderMoved.connect(self.set_position)
        self.check_box.clicked.connect(self.set_sensor)
        self.back_frame.clicked.connect(self.skip_back)
        self.forward_frame.clicked.connect(self.skip_forward)

        # инициализация драйвера
        openni2.initialize()

        self.show()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", '*.oni')

        if filename != '':
            if self.oni_video is not None:
                self.oni_video.terminate()

            self.oni_video = VideoOni(filename, self.check_box.isChecked(), self.slider)

            # подключение обнавления изображения
            self.oni_video.pixmap_signal.connect(self.update_image)

            # запуск oni
            self.oni_video.start()
            self.oni_video.slider = self.slider

            self.play_btn.setEnabled(True)
            self.check_box.setEnabled(True)

            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def play_pause(self):
        self.oni_video.is_paused = not self.oni_video.is_paused

        self.back_frame.setEnabled(self.oni_video.is_paused)
        self.forward_frame.setEnabled(self.oni_video.is_paused)

        if self.oni_video.is_paused:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def set_position(self, position):
        self.oni_video.current_frame = position

    def set_sensor(self):
        self.oni_video.set_sensor(self.check_box.isChecked())

    def skip_forward(self):
        self.oni_video.current_frame += 1

    def skip_back(self):
        self.oni_video.current_frame -= 1

    def update_image(self, frame_array):
        """вывод на экран"""

        h, w, _ = frame_array.shape

        # конвертация в qt
        qt_format = QtGui.QImage(frame_array.data, w, h, QtGui.QImage.Format_RGB888)
        self.video_widget.setPixmap(QPixmap.fromImage(qt_format))

    def __del__(self):
        openni2.unload()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()

    sys.exit(app.exec_())
