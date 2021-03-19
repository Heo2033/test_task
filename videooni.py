import time

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QSlider
from openni import openni2
from openni.openni2 import SENSOR_DEPTH, SENSOR_COLOR


class VideoOni(QThread):
    pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, video_path, is_color, slider):
        super().__init__()

        self.is_color = is_color
        self.is_paused = False
        self.current_frame = 2  # cap2.oni запускается только со 2-го кадра

        self.slider: QSlider = slider

        self.dev = openni2.Device.open_file(video_path.encode('utf-8'))
        self.pbs = openni2.PlaybackSupport(self.dev)

        self.image_stream = openni2.VideoStream(self.dev, SENSOR_COLOR if is_color else SENSOR_DEPTH)

        self.image_stream.start()

    def run(self):
        numb_frame = self.image_stream.get_number_of_frames()
        self.slider.setRange(2, numb_frame)

        while True:
            if self.current_frame > numb_frame:
                self.current_frame = 2

            if self.current_frame < 2:
                self.current_frame = 2

            self.slider.setValue(self.current_frame)

            self.pbs.seek(self.image_stream, self.current_frame)  # с какого кадра стартовать
            frame_image = self.image_stream.read_frame()

            self.build_frame(frame_image)
            time.sleep(0.016)

            if not self.is_paused:
                self.current_frame += 1
            else:
                continue

        self.image_stream.stop()
        openni2.unload()

    def build_frame(self, frame):
        if self.is_color:
            frame_data = frame.get_buffer_as_uint8()
            frame_array = np.ndarray((frame.height, frame.width, 3), dtype=np.uint8, buffer=frame_data)
        else:
            frame_data = frame.get_buffer_as_uint16()
            frame_array = np.ndarray((frame.height, frame.width), dtype=np.uint16, buffer=frame_data)
            frame_array = frame_array / np.max(frame_array) * 255
            frame_array = np.array(frame_array, dtype=np.uint8)
            frame_array = np.stack((frame_array,) * 3, axis=-1)

        self.pixmap_signal.emit(frame_array)

    def set_sensor(self, is_color):
        self.is_color = is_color
        self.image_stream.stop()
        self.image_stream = openni2.VideoStream(self.dev, SENSOR_COLOR if is_color else SENSOR_DEPTH)
        self.image_stream.start()

    def __del__(self):
        self.image_stream.stop()
